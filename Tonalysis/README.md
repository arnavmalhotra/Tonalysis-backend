# Tonalysis - Speech & Body Language Therapy Platform

A real-time speech therapy platform that analyzes your voice, body language, and presentation skills using AI-powered feedback.

## Features

- 🎤 **Real-time Speech Analysis**: Live transcription with AI-powered feedback
- 👤 **Body Language Detection**: Facial expression and posture analysis using MediaPipe
- 🎯 **Interactive Practice Sessions**: Guided practice with countdown and feedback
- 📊 **Performance Tracking**: Visual progress indicators and session summaries
- 💡 **Smart Feedback**: Contextual tips for improvement

## Prerequisites

- Python 3.9 or higher
- Google Gemini API key
- Modern web browser (Chrome, Edge, or Safari recommended)
- Webcam for body language analysis

## Setup Instructions

### 1. Clone the Repository
```bash
git clone <your-repo-url>
cd Tonalysis-backend
```

### 2. Set Up Python Environment
```bash
# Activate virtual environment (if using venv)
source venv/bin/activate  # On macOS/Linux
# or
venv\Scripts\activate     # On Windows

# Install dependencies
pip install -r requirements.txt
```

### 3. Configure Environment Variables
Create a `.env` file in the project root:
```bash
# Create .env file
touch .env
```

Add your Google Gemini API key to the `.env` file:
```
GOOGLE_API_KEY=your_gemini_api_key_here
```

### 4. Get Google Gemini API Key
1. Go to [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Sign in with your Google account
3. Click "Create API Key"
4. Copy the API key and paste it in your `.env` file

## Running the Application

### 1. Start the Backend Server
```bash
# Make sure your virtual environment is activated
python main.py
```

The server will start on `http://localhost:8000`

### 2. Open the Application
1. Open your web browser
2. Navigate to `http://localhost:8000`
3. You should see the Tonalysis interface

### 3. Start a Practice Session
1. Click "Connect to Server" to establish WebSocket connection
2. Click "Start Camera" to enable body language analysis
3. Click "🎤 Start Practice" to begin your session
4. Follow the countdown and start speaking!

## Usage Guide

### Practice Session Flow
1. **Idle State**: Click "Start Practice" to begin
2. **Countdown**: 3-2-1 countdown with preparation tips
3. **Recording**: Real-time feedback appears as you speak
4. **Paused**: Click "Stop" to pause and review
5. **Summary**: View your performance scores and tips

### Feedback Types
- **👍 Positive**: Great progress and improvements
- **⚠️ Warning**: Areas for improvement
- **⛔ Critical**: Important issues to address
- **💡 Info**: General tips and guidance

### Body Language Analysis
- **Emotion Detection**: Happy, neutral, sad, surprised, etc.
- **Posture Analysis**: Excellent, good, fair, poor
- **Energy Levels**: Alert, moderate, tired, very tired

## Troubleshooting

### Common Issues

**1. "Speech recognition not supported"**
- Use Chrome, Edge, or Safari
- Ensure microphone permissions are granted

**2. "Failed to start camera"**
- Check webcam permissions
- Ensure no other app is using the camera

**3. "Analysis temporarily unavailable"**
- Check your Google API key in `.env`
- Verify internet connection
- Check API quota limits

**4. "WebSocket connection failed"**
- Ensure the backend server is running
- Check if port 8000 is available
- Try refreshing the page

### API Key Issues
If you get authentication errors:
1. Verify your API key is correct
2. Check if you have sufficient quota
3. Ensure the key has access to Gemini models

## Development

### Project Structure
```
Tonalysis-backend/
├── main.py                 # FastAPI backend server
├── body_language.js        # Frontend body language analysis
├── speech_recognition_client.html  # Main UI
├── requirements.txt        # Python dependencies
├── .env                    # Environment variables (create this)
├── models/                 # ML model files
└── venv/                   # Python virtual environment
```

### Adding New Features
1. Backend: Modify `main.py` for new API endpoints
2. Frontend: Update HTML/JS for UI changes
3. Body Language: Modify `body_language.js` for new detection

## API Endpoints

- `GET /`: Main application interface
- `GET /api`: Health check endpoint
- `GET /body_language.js`: Body language analysis script
- `WS /ws/text/{client_id}`: WebSocket for real-time communication

## Technologies Used

- **Backend**: FastAPI, Python, WebSockets
- **Frontend**: HTML5, JavaScript, MediaPipe
- **AI**: Google Gemini API
- **Computer Vision**: MediaPipe Face Mesh
- **Speech Recognition**: Web Speech API

## License

This project is for educational and personal use.

## Support

For issues or questions:
1. Check the troubleshooting section
2. Verify all prerequisites are met
3. Ensure proper API key configuration 
