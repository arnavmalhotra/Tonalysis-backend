# Speech Therapy WebSocket Server Documentation

## Overview

This project implements a real-time speech therapy analysis system that uses WebSocket connections for live speech transcription and AI-powered feedback using Google's Gemini API.

## Architecture

### Backend (FastAPI + WebSockets)
- **Framework**: FastAPI with WebSocket support
- **AI Integration**: Google Gemini API for speech analysis
- **Real-time Communication**: WebSocket for bidirectional streaming
- **Language**: Python 3.x

### Frontend
- **Technology**: HTML5 with Web Speech API
- **Real-time Updates**: WebSocket client for live transcription
- **Speech Recognition**: Browser-based speech-to-text

## Features

### 1. Real-time Speech Transcription
- Live speech-to-text conversion using browser's Web Speech API
- Continuous streaming of transcribed text to backend
- Visual feedback showing interim and final transcriptions

### 2. AI-Powered Speech Analysis
- Gemini AI analyzes speech patterns every 10 seconds
- Provides personalized feedback as a virtual speech therapist
- Tracks analysis history to avoid repetitive feedback

### 3. Speech Metrics Tracking
- Word count and unique word usage
- Filler word detection ("um", "uh", "like", etc.)
- Analysis counter to track session progress

### 4. Dynamic Feedback System
- Rotating focus areas for varied feedback:
  - Analysis #1: Overall clarity and pace
  - Analysis #2: Vocabulary variety and word choice
  - Analysis #3: Sentence structure and flow
  - Analysis #4: Confidence and emphasis
  - Analysis #5: Natural pauses and breathing
- Context-aware suggestions based on previous feedback

## Installation & Setup

### Prerequisites
- Python 3.8+
- Google Gemini API key
- Modern web browser (Chrome, Edge, or Safari)

### Backend Setup

1. Create virtual environment:
```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install fastapi uvicorn google-genai python-dotenv
```

3. Set up environment variables:
```bash
# Create .env file
echo "GEMINI_API_KEY=your-api-key-here" > .env
```

4. Run the server:
```bash
python main.py
```

The server will start on `http://localhost:8000`

### Frontend Setup

Simply open `speech_recognition_client.html` in a modern web browser.

## API Endpoints

### WebSocket Endpoint
- **URL**: `ws://localhost:8000/ws/text/{client_id}`
- **Purpose**: Real-time text streaming and analysis

#### Message Formats

**Client to Server:**
```json
{
  "type": "streaming_transcription",
  "text": "transcribed speech text",
  "is_final": false,
  "client_id": "123",
  "timestamp": "2024-01-01T12:00:00"
}
```

**Server to Client (Analysis):**
```json
{
  "type": "analysis",
  "text": "Speech therapist feedback",
  "transcript_analyzed": "original transcript",
  "timestamp": "2024-01-01T12:00:00",
  "analysis_number": 1
}
```

### HTTP Endpoints
- **GET** `/` - Health check endpoint

## Usage Guide

1. **Start the Backend Server**:
   ```bash
   source venv/bin/activate
   python main.py
   ```

2. **Open the Frontend**:
   - Open `speech_recognition_client.html` in Chrome/Edge/Safari
   - Click "Connect to Server"
   - Click "Start Recording"

3. **Speaking Session**:
   - Speak naturally into your microphone
   - Watch real-time transcription appear
   - Every 10 seconds, receive AI-powered feedback
   - Timer shows countdown to next analysis

4. **Analysis Features**:
   - Live transcription with highlighted interim results
   - Speech therapy feedback appears in green section
   - History of last 3 analyses displayed
   - Word count and metrics tracked

## Code Structure

### main.py
- **WebSocket Handler**: Manages real-time connections
- **Gemini Integration**: AI analysis with context awareness
- **Buffer Management**: Handles transcript accumulation
- **Metrics Tracking**: Monitors speech patterns

### speech_recognition_client.html
- **Speech Recognition**: Browser-based speech-to-text
- **WebSocket Client**: Real-time server communication
- **UI Components**: Live transcription and analysis display
- **Timer System**: Countdown to next analysis

## Key Implementation Details

### Speech Analysis Algorithm
1. Accumulates transcribed text over 10-second intervals
2. Calculates speech metrics (word count, unique words, fillers)
3. Sends context-aware prompt to Gemini including:
   - Current transcript
   - Speech metrics
   - Previous feedback history
   - Specific focus area for current analysis
4. Returns personalized, non-repetitive feedback

### Real-time Streaming
- Frontend continuously streams transcription data
- Backend processes both interim and final transcriptions
- Efficient buffer management for 10-second windows
- Automatic cleanup on client disconnect

### Error Handling
- Graceful WebSocket disconnection handling
- API error fallbacks
- Client-side error messages
- Automatic reconnection capability

## Future Enhancements

1. **Electron Desktop App**: Native desktop application with advanced features
2. **Punctuation Support**: Automatic punctuation in transcriptions
3. **Multi-language Support**: Speech recognition in multiple languages
4. **Session Recording**: Save and replay speech sessions
5. **Progress Tracking**: Long-term improvement metrics
6. **Export Functionality**: Download transcripts and analyses

## Troubleshooting

### Common Issues

1. **"No speech detected"**
   - Check microphone permissions in browser
   - Ensure microphone is working properly
   - Speak clearly and closer to microphone

2. **Connection errors**
   - Verify backend server is running
   - Check WebSocket URL matches server address
   - Ensure CORS is properly configured

3. **No analysis received**
   - Verify GEMINI_API_KEY is set correctly
   - Check console for API errors
   - Ensure you speak for at least 10 seconds

### Browser Compatibility
- **Best**: Chrome, Edge (Chromium-based)
- **Good**: Safari
- **Limited**: Firefox (no Web Speech API support)

## Security Considerations

- CORS enabled for development (restrict in production)
- API keys stored in environment variables
- WebSocket connections should use WSS in production
- Client IDs are randomly generated

## Performance Notes

- Efficient streaming with minimal latency
- Async processing prevents blocking
- Thread pool for Gemini API calls
- Automatic buffer cleanup on disconnect
