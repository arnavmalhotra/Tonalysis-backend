from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
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

# Initialize Gemini client
client = genai.Client()

# Thread pool for async operations
executor = ThreadPoolExecutor(max_workers=4)

# Store transcript buffers and analysis data for each client
transcript_buffers: Dict[str, List[str]] = {}
last_analysis_time: Dict[str, float] = {}
analysis_history: Dict[str, List[str]] = {}
speech_metrics: Dict[str, Dict] = {}


@app.get("/")
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
    
    try:
        while True:
            message = await websocket.receive_text()
            data = json.loads(message)
            
            if data.get("type") == "streaming_transcription":
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
                        await websocket.send_json({
                            "type": "analysis",
                            "text": analysis,
                            "transcript_analyzed": recent_transcript,
                            "timestamp": datetime.now().isoformat(),
                            "analysis_number": speech_metrics[client_id]["analyses_count"]
                        })
                        
                        print(f"[Client #{client_id}] Analysis #{speech_metrics[client_id]['analyses_count']} sent: {analysis[:100]}...")
                    
                    # Reset for next analysis
                    transcript_buffers[client_id] = []
                    last_analysis_time[client_id] = current_time
                
    except WebSocketDisconnect:
        print(f"\nText streaming client #{client_id} disconnected")
        # Clean up buffers
        if client_id in transcript_buffers:
            del transcript_buffers[client_id]
        if client_id in last_analysis_time:
            del last_analysis_time[client_id]
        if client_id in analysis_history:
            del analysis_history[client_id]
        if client_id in speech_metrics:
            del speech_metrics[client_id]
    except Exception as e:
        print(f"\nError in text websocket: {e}")
        await websocket.close()


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)