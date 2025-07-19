from fastapi import FastAPI, WebSocket, WebSocketDisconnect, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from typing import List, Dict, Optional
import json
import asyncio
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime
from google import genai
import time
import os
import uuid
from dotenv import load_dotenv

# Try to import Twelvelabs SDK
try:
    from twelvelabs import TwelveLabs
    TWELVELABS_AVAILABLE = True
except ImportError:
    print("Warning: Twelvelabs SDK not installed. Install with: pip install twelvelabs")
    TWELVELABS_AVAILABLE = False

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

# Create videos directory if it doesn't exist
os.makedirs("videos", exist_ok=True)
app.mount("/videos", StaticFiles(directory="videos"), name="videos")

# Serve JavaScript files directly from root
@app.get("/body_language.js")
async def serve_body_language_js():
    return FileResponse("body_language.js", media_type="application/javascript")

# Initialize Gemini client
client = genai.Client()

# Initialize Twelvelabs client if available
twelvelabs_client = None
if TWELVELABS_AVAILABLE:
    try:
        twelvelabs_api_key = os.getenv("TWELVELABS_API_KEY")
        if twelvelabs_api_key:
            twelvelabs_client = TwelveLabs(api_key=twelvelabs_api_key)
            print("Twelvelabs client initialized successfully")
        else:
            print("Warning: TWELVELABS_API_KEY not found in environment variables")
    except Exception as e:
        print(f"Failed to initialize Twelvelabs client: {e}")

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

# Store video recording sessions
video_sessions: Dict[str, Dict] = {}

@app.get("/")
async def serve_client():
    return FileResponse("speech_recognition_client.html")

@app.get("/api")
async def root():
    return {"message": "Speech Therapy WebSocket Server with Twelvelabs Integration"}

# New endpoint to start video recording session
@app.post("/api/start-video-session/{client_id}")
async def start_video_session(client_id: str):
    """Start a new video recording session"""
    session_id = str(uuid.uuid4())
    video_sessions[client_id] = {
        "session_id": session_id,
        "start_time": datetime.now().isoformat(),
        "video_path": f"videos/session_{session_id}.webm",
        "status": "recording"
    }
    return {"session_id": session_id, "status": "started"}

# New endpoint to end video recording and trigger Twelvelabs analysis
@app.post("/api/end-video-session/{client_id}")
async def end_video_session(client_id: str):
    """End video recording session and start Twelvelabs analysis"""
    if client_id not in video_sessions:
        raise HTTPException(status_code=404, detail="Video session not found")
    
    session = video_sessions[client_id]
    session["end_time"] = datetime.now().isoformat()
    session["status"] = "processing"
    
    # Start Twelvelabs analysis in background
    if TWELVELABS_AVAILABLE and twelvelabs_client:
        asyncio.create_task(process_video_with_twelvelabs(client_id, session))
    
    return {"message": "Video session ended, analysis starting", "session": session}

# New endpoint to upload video file
@app.post("/api/upload-video/{client_id}")
async def upload_video(client_id: str, video: UploadFile = File(...)):
    """Upload video file for analysis"""
    if client_id not in video_sessions:
        raise HTTPException(status_code=404, detail="Video session not found")
    
    session = video_sessions[client_id]
    video_path = session["video_path"]
    
    # Save uploaded video
    with open(video_path, "wb") as buffer:
        content = await video.read()
        buffer.write(content)
    
    session["video_uploaded"] = True
    session["video_size"] = len(content)
    
    return {"message": "Video uploaded successfully", "path": video_path}

# Get video session status
@app.get("/api/video-session/{client_id}")
async def get_video_session(client_id: str):
    """Get video session status and analysis results"""
    if client_id not in video_sessions:
        raise HTTPException(status_code=404, detail="Video session not found")
    
    return video_sessions[client_id]

async def process_video_with_twelvelabs(client_id: str, session: Dict):
    """Process video with Twelvelabs API for deep analysis"""
    try:
        if not twelvelabs_client:
            print("Twelvelabs client not available")
            return
        
        video_path = session["video_path"]
        
        # Check if video file exists
        if not os.path.exists(video_path):
            print(f"Video file not found: {video_path}")
            session["status"] = "error"
            session["error"] = "Video file not found"
            return
        
        print(f"Starting Twelvelabs analysis for {video_path}")
        session["status"] = "uploading_to_twelvelabs"
        
        # Create index if it doesn't exist
        index_name = "speech_therapy_analysis"
        try:
            # Try to get existing index
            indexes = twelvelabs_client.index.list()
            index = None
            for idx in indexes:
                if idx.name == index_name:
                    index = idx
                    break
            
            if not index:
                # Create new index with comprehensive analysis models
                index = twelvelabs_client.index.create(
                    name=index_name,
                    models=[
                        {
                            "name": "marengo2.7",
                            "options": ["visual", "audio"]
                        },
                        {
                            "name": "pegasus1.2",
                            "options": ["visual", "audio"]
                        }
                    ]
                )
                print(f"Created new index: {index.id}")
        
        except Exception as e:
            print(f"Error managing index: {e}")
            session["status"] = "error"
            session["error"] = f"Index error: {str(e)}"
            return
        
        # Upload video
        try:
            task = twelvelabs_client.task.create(
                index_id=index.id,
                file=video_path,
                language="en"
            )
            
            session["twelvelabs_task_id"] = task.id
            session["status"] = "processing_twelvelabs"
            
            print(f"Video uploaded to Twelvelabs. Task ID: {task.id}")
            
            # Wait for processing to complete
            while True:
                task_status = twelvelabs_client.task.retrieve(task.id)
                
                if task_status.status == "ready":
                    session["twelvelabs_video_id"] = task_status.video_id
                    session["status"] = "analyzing"
                    break
                elif task_status.status in ["failed", "error"]:
                    session["status"] = "error"
                    session["error"] = f"Twelvelabs processing failed: {task_status.status}"
                    return
                
                # Wait before checking again
                await asyncio.sleep(10)
            
            # Perform various analyses
            video_id = task_status.video_id
            analyses = await perform_comprehensive_analysis(video_id, session)
            
            session["twelvelabs_analysis"] = analyses
            session["status"] = "completed"
            session["completed_time"] = datetime.now().isoformat()
            
            print(f"Twelvelabs analysis completed for client {client_id}")
        
        except Exception as e:
            print(f"Error uploading to Twelvelabs: {e}")
            session["status"] = "error"
            session["error"] = f"Upload error: {str(e)}"
    
    except Exception as e:
        print(f"Error in Twelvelabs processing: {e}")
        session["status"] = "error"
        session["error"] = str(e)

async def perform_comprehensive_analysis(video_id: str, session: Dict) -> Dict:
    """Perform comprehensive video analysis using Twelvelabs"""
    analyses = {}
    
    try:
        # 1. Generate summary
        summary_result = twelvelabs_client.generate.summarize(
            video_id=video_id,
            type="summary"
        )
        analyses["summary"] = summary_result.summary
        
        # 2. Analyze conversation and speech patterns
        conversation_result = twelvelabs_client.generate.summarize(
            video_id=video_id,
            type="topic"
        )
        analyses["topics"] = conversation_result.summary
        
        # 3. Search for specific presentation elements
        presentation_queries = [
            "What is the speaker's body language and posture like?",
            "How confident does the speaker appear?",
            "Are there any nervous habits or gestures?",
            "How is the speaker's eye contact and facial expressions?",
            "What is the pace and clarity of speech?",
            "Are there any filler words or verbal tics?",
            "How engaging is the speaker's delivery?",
            "What improvements could be made to the presentation style?"
        ]
        
        search_results = []
        for query in presentation_queries:
            try:
                result = twelvelabs_client.search.query(
                    index_id=session.get("index_id"),
                    query_text=query,
                    options=["visual", "conversation"],
                    video_id=video_id
                )
                
                if result.data:
                    search_results.append({
                        "query": query,
                        "results": [
                            {
                                "confidence": clip.confidence,
                                "start": clip.start,
                                "end": clip.end,
                                "video_id": clip.video_id
                            }
                            for clip in result.data[:3]  # Top 3 results per query
                        ]
                    })
            except Exception as e:
                print(f"Search query failed for '{query}': {e}")
        
        analyses["presentation_analysis"] = search_results
        
        # 4. Generate detailed insights using the search results
        insights_prompt = f"""
        Based on the video analysis of a practice presentation session, provide detailed feedback on:
        
        1. **Speaking Style & Delivery**
           - Speech pace, clarity, and volume
           - Use of pauses and emphasis
           - Vocal variety and engagement
        
        2. **Body Language & Presence**
           - Posture and positioning
           - Gestures and hand movements
           - Facial expressions and eye contact
        
        3. **Content Organization**
           - Structure and flow
           - Key points delivery
           - Audience engagement techniques
        
        4. **Areas for Improvement**
           - Specific actionable recommendations
           - Practice exercises suggestions
           - Next steps for development
        
        Video Summary: {analyses.get('summary', 'No summary available')}
        Topics Covered: {analyses.get('topics', 'No topics identified')}
        
        Provide constructive, specific feedback in a supportive tone suitable for someone practicing their presentation skills.
        """
        
        # Generate insights using Gemini
        gemini_analysis = await asyncio.get_event_loop().run_in_executor(
            executor,
            lambda: client.models.generate_content(
                model="gemini-2.5-flash",
                contents=insights_prompt
            )
        )
        
        analyses["detailed_insights"] = gemini_analysis.text
        
        # 5. Create actionable recommendations
        recommendations = []
        
        # Analyze the results to create specific recommendations
        for search_result in search_results:
            query = search_result["query"]
            if "body language" in query.lower() and search_result["results"]:
                recommendations.append({
                    "category": "Body Language",
                    "recommendation": "Focus on maintaining good posture and purposeful gestures",
                    "timestamp_examples": [r["start"] for r in search_result["results"][:2]]
                })
            elif "eye contact" in query.lower() and search_result["results"]:
                recommendations.append({
                    "category": "Eye Contact",
                    "recommendation": "Practice maintaining consistent eye contact with the camera/audience",
                    "timestamp_examples": [r["start"] for r in search_result["results"][:2]]
                })
            elif "speech" in query.lower() and search_result["results"]:
                recommendations.append({
                    "category": "Speech Delivery", 
                    "recommendation": "Work on speech pace and clarity for better audience engagement",
                    "timestamp_examples": [r["start"] for r in search_result["results"][:2]]
                })
        
        analyses["recommendations"] = recommendations
        
        return analyses
    
    except Exception as e:
        print(f"Error in comprehensive analysis: {e}")
        return {"error": str(e)}


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
        
        prompt = f"""You are an experienced speech and tone expert providing personalized feedback. Analyze the impression given by the speaker. Briefly explain why that is the impression given using real psychology, then give suggestions for improvement. 

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
        
        prompt = f"""You are an expert body language coach providing personalized feedback for someone. Analyze the impression given by them. Briefly explain why that is the impression given using real psychology, then give suggestions for improvement.

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
            elif data.get("type") == "video_session_started":
                # Handle video session start notification
                print(f"[Client #{client_id}] Video session started")
                await websocket.send_json({
                    "type": "video_session_acknowledged",
                    "message": "Video recording session started"
                })
                continue
            elif data.get("type") == "video_session_ended":
                # Handle video session end and send Twelvelabs analysis status
                print(f"[Client #{client_id}] Video session ended")
                if client_id in video_sessions:
                    session = video_sessions[client_id]
                    await websocket.send_json({
                        "type": "twelvelabs_analysis_status",
                        "status": session.get("status", "unknown"),
                        "session_id": session.get("session_id")
                    })
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
            
            # Check for Twelvelabs analysis completion and send updates
            if client_id in video_sessions:
                session = video_sessions[client_id]
                if session.get("status") == "completed" and not session.get("results_sent"):
                    await websocket.send_json({
                        "type": "twelvelabs_analysis_complete",
                        "analysis": session.get("twelvelabs_analysis", {}),
                        "session_id": session.get("session_id")
                    })
                    session["results_sent"] = True
                
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