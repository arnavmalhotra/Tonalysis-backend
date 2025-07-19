from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from typing import List, Dict
import json
import asyncio
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime
from google import genai
import time
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files for models and assets
app.mount("/models", StaticFiles(directory="models"), name="models")

# Serve JavaScript files directly from root
@app.get("/body_language.js")
async def serve_body_language_js():
    return FileResponse("body_language.js", media_type="application/javascript")

# Initialize Gemini client
client = genai.Client()

# Thread pool for async operations
executor = ThreadPoolExecutor(max_workers=4)

# Store transcript buffers and analysis data for each client
transcript_buffers: Dict[str, List[str]] = {}
last_analysis_time: Dict[str, float] = {}
analysis_history: Dict[str, List[str]] = {}
speech_metrics: Dict[str, Dict] = {}

# Store body language data for each client
body_language_buffers: Dict[str, List[Dict]] = {}
last_body_analysis_time: Dict[str, float] = {}
body_language_history: Dict[str, List[str]] = {}


@app.get("/")
async def serve_client():
    return FileResponse("speech_recognition_client.html")

@app.get("/api")
async def root():
    return {"message": "Speech Therapy WebSocket Server"}


async def analyze_with_gemini(transcript: str, client_id: str) -> str:
    """Analyze transcript with Gemini as a speech therapist"""
    try:
        # Get previous analyses for this client
        previous_analyses = analysis_history.get(client_id, [])
        previous_feedback = "\n".join(previous_analyses[-3:]) if previous_analyses else "No previous feedback"
        
        # Calculate basic metrics
        words = transcript.split()
        word_count = len(words)
        unique_words = len(set(words))
        
        # Common filler words
        filler_words = ["um", "uh", "like", "you know", "basically", "actually", "literally"]
        filler_count = sum(1 for word in words if word.lower() in filler_words)
        
        prompt = f"""You are an experienced speech therapist providing personalized feedback. 

Current transcript (last 10 seconds, {word_count} words):
"{transcript}"

Speech metrics:
- Total words: {word_count}
- Unique words: {unique_words}
- Filler words detected: {filler_count}

Previous feedback given:
{previous_feedback}

IMPORTANT INSTRUCTIONS:
1. Provide DIFFERENT feedback than before - focus on new aspects each time
2. Be specific - mention exact words or phrases from the transcript
3. Notice and praise improvements if any
4. Vary your suggestions - don't repeat the same advice
5. Consider these rotating focus areas:
   - First analysis: Overall clarity and pace
   - Second analysis: Vocabulary variety and word choice
   - Third analysis: Sentence structure and flow
   - Fourth analysis: Confidence and emphasis
   - Fifth analysis: Natural pauses and breathing
   
Keep response to 2-3 sentences. Be encouraging but specific. If you notice the speaker said very little, encourage them to speak more."""

        response = await asyncio.get_event_loop().run_in_executor(
            executor,
            lambda: client.models.generate_content(
                model="gemini-2.5-flash", 
                contents=prompt
            )
        )
        return response.text
    except Exception as e:
        print(f"Gemini API error: {e}")
        return f"Analysis temporarily unavailable: {str(e)}"


async def analyze_body_language_with_gemini(body_data: List[Dict], client_id: str) -> str:
    """Analyze body language patterns with Gemini as a body language expert"""
    try:
        # Get previous body language analyses for this client
        previous_analyses = body_language_history.get(client_id, [])
        previous_feedback = "\n".join(previous_analyses[-2:]) if previous_analyses else "No previous feedback"
        
        # Calculate patterns from recent body language data
        emotions = [item.get('emotion', 'neutral') for item in body_data]
        postures = [item.get('posture', {}).get('label', 'unknown') for item in body_data]
        fatigue_levels = [item.get('fatigue', {}).get('label', 'unknown') for item in body_data]
        
        # Find most common patterns
        most_common_emotion = max(set(emotions), key=emotions.count)
        good_posture_ratio = sum(1 for p in postures if p == 'good') / len(postures) if postures else 0
        tired_ratio = sum(1 for f in fatigue_levels if f == 'tired') / len(fatigue_levels) if fatigue_levels else 0
        
        prompt = f"""You are an expert body language coach providing personalized feedback for someone during a speech therapy session.

Recent body language data (last 30 seconds):
- Dominant emotion: {most_common_emotion}
- Good posture ratio: {good_posture_ratio:.1%}
- Fatigue signs: {tired_ratio:.1%}
- Total data points: {len(body_data)}

Previous feedback given:
{previous_feedback}

IMPORTANT INSTRUCTIONS:
1. Provide DIFFERENT feedback than before - focus on new aspects each time
2. Be encouraging and constructive
3. Give specific, actionable advice for body language during speech
4. Consider these rotating focus areas:
   - First analysis: Overall posture and presence
   - Second analysis: Facial expressions and emotional engagement
   - Third analysis: Energy levels and alertness
   - Fourth analysis: Professional presentation
   - Fifth analysis: Confidence and body language harmony

Keep response to 2-3 sentences. Be supportive but specific. If the data shows good patterns, acknowledge and encourage them."""

        response = await asyncio.get_event_loop().run_in_executor(
            executor,
            lambda: client.models.generate_content(
                model="gemini-2.5-flash", 
                contents=prompt
            )
        )
        return response.text
    except Exception as e:
        print(f"Body language analysis error: {e}")
        return f"Body language analysis temporarily unavailable: {str(e)}"


@app.websocket("/ws/text/{client_id}")
async def text_websocket_endpoint(websocket: WebSocket, client_id: str):
    await websocket.accept()
    print(f"Text streaming client #{client_id} connected")
    
    # Initialize buffers for this client
    transcript_buffers[client_id] = []
    last_analysis_time[client_id] = time.time()
    analysis_history[client_id] = []
    speech_metrics[client_id] = {
        "total_words": 0,
        "total_fillers": 0,
        "analyses_count": 0
    }
    
    # Initialize body language buffers
    body_language_buffers[client_id] = []
    last_body_analysis_time[client_id] = time.time()
    body_language_history[client_id] = []
    
    try:
        while True:
            message = await websocket.receive_text()
            data = json.loads(message)
            
            if data.get("type") == "heartbeat":
                # Handle heartbeat - just acknowledge to keep connection alive
                print(f"[Client #{client_id}] Heartbeat received")
                continue
            elif data.get("type") == "body_language":
                # Handle body language data
                emotion = data.get("emotion", "neutral")
                posture = data.get("posture", {})
                fatigue = data.get("fatigue", {})
                
                # Store body language data
                body_language_buffers[client_id].append({
                    "emotion": emotion,
                    "posture": posture,
                    "fatigue": fatigue,
                    "timestamp": data.get("timestamp", datetime.now().isoformat())
                })
                
                print(f"[Client #{client_id}] Body language: {emotion}, {posture.get('label', 'unknown')}, {fatigue.get('label', 'unknown')}")
                
                # Check if it's time for body language analysis (every 30 seconds)
                current_time = time.time()
                if current_time - last_body_analysis_time[client_id] >= 30:
                    recent_body_data = body_language_buffers[client_id]
                    
                    if len(recent_body_data) >= 5:  # Need at least 5 data points
                        print(f"[Client #{client_id}] Analyzing body language patterns...")
                        
                        # Analyze with Gemini
                        analysis = await analyze_body_language_with_gemini(recent_body_data, client_id)
                        
                        # Store analysis in history
                        body_language_history[client_id].append(analysis)
                        
                        # Count analyses
                        analysis_count = len(body_language_history[client_id])
                        
                        # Send analysis to frontend
                        await websocket.send_json({
                            "type": "body_language_feedback",
                            "text": analysis,
                            "analysis_number": analysis_count,
                            "timestamp": datetime.now().isoformat()
                        })
                        
                        print(f"[Client #{client_id}] Body language analysis #{analysis_count} sent: {analysis[:100]}...")
                    
                    # Reset for next analysis
                    body_language_buffers[client_id] = []
                    last_body_analysis_time[client_id] = current_time
                
            elif data.get("type") == "streaming_transcription":
                text = data.get("text", "")
                is_final = data.get("is_final", False)
                
                # Print the streaming text with clear formatting
                if is_final:
                    print(f"\n[Client #{client_id}] Final: {text}")
                    # Store final transcript
                    transcript_buffers[client_id].append(text)
                else:
                    # Use carriage return to update the same line for interim results
                    print(f"\r[Client #{client_id}] Speaking: {text}", end="", flush=True)
                
                # Check if it's time for analysis (every 10 seconds)
                current_time = time.time()
                if current_time - last_analysis_time[client_id] >= 10:
                    # Get the last 10 seconds of transcript
                    recent_transcript = " ".join(transcript_buffers[client_id])
                    
                    if recent_transcript.strip():
                        print(f"\n[Client #{client_id}] Analyzing transcript...")
                        
                        # Analyze with Gemini
                        analysis = await analyze_with_gemini(recent_transcript, client_id)
                        
                        # Store analysis in history
                        analysis_history[client_id].append(analysis)
                        
                        # Update metrics
                        speech_metrics[client_id]["analyses_count"] += 1
                        
                        # Send analysis to frontend
                        analysis_message = {
                            "type": "analysis",
                            "text": analysis,
                            "transcript_analyzed": recent_transcript,
                            "timestamp": datetime.now().isoformat(),
                            "analysis_number": speech_metrics[client_id]["analyses_count"]
                        }
                        
                        print(f"[Client #{client_id}] Sending analysis message: {analysis_message}")
                        await websocket.send_json(analysis_message)
                        print(f"[Client #{client_id}] Analysis #{speech_metrics[client_id]['analyses_count']} sent successfully!")
                    
                    # Reset for next analysis
                    transcript_buffers[client_id] = []
                    last_analysis_time[client_id] = current_time
                else:
                    # Debug: show time remaining until next analysis
                    time_remaining = 10 - (current_time - last_analysis_time[client_id])
                    if time_remaining > 0 and time_remaining < 1:
                        print(f"[Client #{client_id}] Next analysis in {time_remaining:.1f}s")
                
    except WebSocketDisconnect:
        print(f"\nText streaming client #{client_id} disconnected")
        # Clean up speech buffers
        if client_id in transcript_buffers:
            del transcript_buffers[client_id]
        if client_id in last_analysis_time:
            del last_analysis_time[client_id]
        if client_id in analysis_history:
            del analysis_history[client_id]
        if client_id in speech_metrics:
            del speech_metrics[client_id]
        
        # Clean up body language buffers
        if client_id in body_language_buffers:
            del body_language_buffers[client_id]
        if client_id in last_body_analysis_time:
            del last_body_analysis_time[client_id]
        if client_id in body_language_history:
            del body_language_history[client_id]
    except Exception as e:
        print(f"\nError in text websocket: {e}")
        await websocket.close()


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)