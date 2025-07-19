from fastapi import FastAPI, WebSocket, WebSocketDisconnect, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse
from typing import List, Dict
import json
import asyncio
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime
from google import genai
import time
from dotenv import load_dotenv
import os
import tempfile
import subprocess
from twelvelabs import TwelveLabs
from twelvelabs.models.task import Task

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

# Initialize TwelveLabs client
tl_client = TwelveLabs(api_key=os.getenv('TWELVELABS_API_KEY'))

# Get or create index for video analysis
def get_or_create_index():
    """Get existing index or create a new one"""
    try:
        # Try to list existing indexes
        indexes = tl_client.index.list()
        
        # Look for an existing index with our name
        for index in indexes:
            if index.name == "speech-therapy-sessions":
                print(f"Using existing index: {index.id}")
                return index.id
        
        # If not found, create a new index
        print("Creating new index for speech therapy sessions...")
        new_index = tl_client.index.create(
            name="speech-therapy-sessions",
            models=[{"name": "pegasus1.2", "options": ["visual", "audio"]}]
        )
        print(f"Created new index: {new_index.id}")
        return new_index.id
        
    except Exception as e:
        print(f"Error managing index: {e}")
        # Fallback to a hardcoded index if needed
        return None

INDEX_ID = get_or_create_index()

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


@app.post("/api/analyze-video")
async def analyze_video(
    video: UploadFile = File(...),
    client_id: str = Form(...),
    duration: int = Form(...)
):
    """Analyze video with TwelveLabs for comprehensive therapy insights"""
    print(f"[Client #{client_id}] Received video for analysis, duration: {duration}s")
    
    try:
        # Check minimum duration
        if duration < 4:
            return JSONResponse(
                status_code=400,
                content={"error": "Video too short. Minimum 4 seconds required."}
            )
        
        # Save uploaded video temporarily
        with tempfile.NamedTemporaryFile(delete=False, suffix=".webm") as tmp_webm:
            content = await video.read()
            tmp_webm.write(content)
            tmp_webm_path = tmp_webm.name
            print(f"Saved WebM to: {tmp_webm_path}, size: {len(content)} bytes")
        
        # Convert WebM to MP4 using FFmpeg
        tmp_mp4_path = tmp_webm_path.replace('.webm', '.mp4')
        print(f"Converting WebM to MP4: {tmp_mp4_path}")
        
        try:
            result = subprocess.run([
                'ffmpeg', '-i', tmp_webm_path,
                '-c:v', 'libx264',
                '-c:a', 'aac',
                '-movflags', '+faststart',
                '-y',  # Overwrite output file
                tmp_mp4_path
            ], capture_output=True, text=True)
            
            if result.returncode != 0:
                print(f"FFmpeg error: {result.stderr}")
                raise Exception(f"FFmpeg conversion failed: {result.stderr}")
            
            print(f"Successfully converted to MP4")
            
            # Use MP4 file for TwelveLabs
            video_path = tmp_mp4_path
        except Exception as e:
            print(f"FFmpeg conversion failed, using original WebM: {e}")
            video_path = tmp_webm_path
        
        # Analyze with TwelveLabs
        analysis_result = await analyze_video_with_twelvelabs(video_path, client_id)
        
        # Clean up temporary files
        try:
            os.unlink(tmp_webm_path)
            if os.path.exists(tmp_mp4_path):
                os.unlink(tmp_mp4_path)
        except:
            pass
        
        return JSONResponse(content=analysis_result)
        
    except Exception as e:
        print(f"Error analyzing video: {e}")
        import traceback
        traceback.print_exc()
        return JSONResponse(
            status_code=500,
            content={"error": str(e)}
        )


async def analyze_video_with_twelvelabs(video_path: str, client_id: str) -> dict:
    """Use TwelveLabs to analyze the practice session video"""
    try:
        print(f"[Client #{client_id}] Starting TwelveLabs analysis...")
        
        # Check if we have a valid index
        if not INDEX_ID:
            raise Exception("No valid TwelveLabs index available. Please check your API key and try again.")
        
        # Upload video to TwelveLabs
        print(f"Uploading video to TwelveLabs index: {INDEX_ID}")
        
        # Create a task for video upload
        task = tl_client.task.create(
            index_id=INDEX_ID,
            file=video_path
        )
        
        print(f"Task created: {task.id}")
        
        # Wait for the task to complete
        def on_task_update(task: Task):
            print(f"Task status: {task.status}")
        
        task.wait_for_done(callback=on_task_update)
        
        if task.status != "ready":
            raise Exception(f"Task failed with status: {task.status}")
        
        video_id = task.video_id
        print(f"Video uploaded successfully: {video_id}")
        
        # Perform comprehensive analysis using open-ended generate
        print("Generating comprehensive therapy analysis...")
        
        prompt = """You are an expert speech and body language therapist analyzing a practice session video. 
        Please provide a comprehensive analysis covering:
        
        1. **Speech Analysis**:
           - Clarity and articulation
           - Pace and rhythm
           - Volume and projection
           - Use of pauses and emphasis
           - Filler words and verbal habits
        
        2. **Body Language Analysis**:
           - Posture and stance
           - Facial expressions
           - Eye contact with camera
           - Hand gestures and movement
           - Overall confidence and presence
        
        3. **Overall Performance**:
           - Energy levels throughout
           - Engagement and enthusiasm
           - Areas of strength
           - Specific areas for improvement
        
        4. **Actionable Recommendations**:
           - Top 3-5 specific things to work on
           - Exercises or techniques to practice
           - What to focus on in the next session
        
        Please be encouraging but specific, providing timestamps when noting particular moments.
        Format your response in clear sections with practical advice."""
        
        # Use analyze endpoint for open-ended analysis
        text_stream = tl_client.analyze_stream(
            video_id=video_id,
            prompt=prompt
        )
        
        # Collect the streamed text
        detailed_analysis = ""
        for text in text_stream:
            detailed_analysis += text
        
        print(f"Generated detailed analysis: {len(detailed_analysis)} characters")
        
        # Also get video gist for additional context
        gist_result = tl_client.gist(
            video_id=video_id,
            types=["title", "topic", "hashtag"]
        )
        
        # Format the analysis result
        analysis = {
            "video_id": video_id,
            "detailed_analysis": detailed_analysis,
            "topics": list(gist_result.topics) if gist_result.topics else [],
            "hashtags": list(gist_result.hashtags) if gist_result.hashtags else [],
            "title": gist_result.title if hasattr(gist_result, 'title') else "Practice Session",
            "status": "complete"
        }
        
        print(f"[Client #{client_id}] TwelveLabs analysis complete")
        return analysis
        
    except Exception as e:
        print(f"TwelveLabs analysis error: {e}")
        import traceback
        traceback.print_exc()
        
        # Return a graceful error response
        return {
            "error": str(e),
            "status": "failed",
            "note": "Video analysis encountered an error. Please try again."
        }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)