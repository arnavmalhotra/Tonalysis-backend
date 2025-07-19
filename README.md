# 🧠 Tonalysis Suite

A unified AI-powered communication toolkit featuring:

1. **🎤 Tonalysis** — A real-time speech & body language therapy platform  
2. **🧩 Voice Transcriber Extension** — A Chrome extension for real-time transcription

---
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
git clone https://github.com/arnavmalhotra/Tonalysis-backend.git
cd Tonalysis
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


----------------

# 🎤 Voice Transcriber Chrome Extension

A powerful Chrome extension that provides real-time audio transcription using the Web Speech API, enhanced with AI feedback from **Google Gemini**. Capture, analyze, and improve your speech directly in the browser.

---

## ✨ Features

- **Real-time transcription** using browser's built-in speech recognition
- **AI-Powered Feedback** via **Google Gemini** *(optional integration)*
- **Multiple language support** (English, Spanish, French, German, etc.)
- **Continuous mode** for long-form transcription
- **Auto punctuation** for better readability
- **Copy to clipboard** functionality
- **Save transcriptions** as text files
- **Floating overlay** for page-level transcription
- **Keyboard shortcuts** for quick access
- **Persistent storage** to save your transcriptions
- **Modern, responsive UI** with professional styling

---

## 🧠 AI Feedback with Google Gemini

You can connect the extension to Google Gemini to receive intelligent feedback on your speaking style, clarity, tone, and pacing.

### 🔍 What AI Feedback Includes

- Summary of your speaking tone and clarity
- Highlighted filler words, pauses, or stuttering
- Suggestions for improved delivery and structure
- Constructive analysis of speech patterns

### 🛠️ Setup for AI Feedback

> ⚠️ **Note:** This feature requires a valid **Google Gemini API Key** and internet access.

1. **Get an API Key** from [Google AI Studio](https://makersuite.google.com/app/apikey)
2. In the extension’s **Extension options**, paste your key in the **"Gemini API Key"** field
3. Once enabled, you'll see an **"Analyze with AI"** button after each transcription
4. Click it to send your text to Gemini and receive feedback

> **Privacy Note:** Only the transcribed text is sent to Google Gemini. No audio or personal data is shared.

---

## 🚀 Installation

1. **Download the Extension Files**
   - Clone or download all files to a local directory:
     ```
     voice-transcriber/
     ├── manifest.json
     ├── popup.html
     ├── popup.js
     ├── styles.css
     ├── background.js
     ├── content.js
     └── README.md
     ```

2. **Open Chrome Extensions Page**
   - Go to `chrome://extensions/`
   - Enable "Developer mode"

3. **Load the Extension**
   - Click "Load unpacked"
   - Select the `voice-transcriber` folder

4. **Pin the Extension** (Optional)
   - Click the puzzle icon in Chrome's toolbar
   - Pin "Voice Transcriber"

---

## 🔬 Advanced Features

### Language Selection
- Available in the settings panel

### Continuous Mode
- Perfect for lectures, meetings, or interviews

### Auto Punctuation
- Formats your speech into structured sentences

### Copy & Save
- Save your transcript or copy it with a single click

### Page Overlay
- Transcribe while watching videos or browsing

### Keyboard Shortcuts
- `Ctrl+Shift+T`: Toggle transcription
- `Ctrl+Shift+C`: Copy transcription

---

## ⚙️ Configuration

### Settings Options

| Setting | Description | Default |
|---------|-------------|---------|
| Language | Recognition language | English (US) |
| Continuous Mode | Records until stopped | Off |
| Auto Punctuation | Adds punctuation automatically | On |
| Gemini API Key | Enables AI feedback | *Optional* |

---

### Stored Data

- **User preferences** and settings
- **Recent transcriptions** (stored locally for 7 days)
- **Gemini API key** (stored locally; not shared externally)

---

## 🔧 Troubleshooting

<details>
<summary>Common Issues</summary>

#### "Speech recognition not supported"
- Use Google Chrome or a Chromium-based browser

#### "Microphone access denied"
- Allow mic access in Chrome settings

#### Poor transcription quality
- Use a clear mic and speak at a moderate pace

#### Gemini API feedback not working
- Ensure API key is valid
- Check console for response errors
</details>

<details>
<summary>Advanced Debugging</summary>

1. Open `chrome://extensions/`
2. Click "Inspect views: background page"
3. Check the Console for logs and errors
</details>

---

## 🌐 Browser Compatibility

| Browser | Status |
|--------|--------|
| Chrome | ✅ Supported |
| Edge (Chromium) | ✅ Supported |
| Firefox | ❌ Not supported |
| Safari | ❌ Not supported |

---

## 🔒 Privacy & Security

- Speech recognition is handled **entirely in-browser**
- Transcriptions and settings are stored **locally**
- Google Gemini integration sends only **text**, no audio
- No third-party tracking or analytics

---

## License

This project is for educational and personal use.

----

## Support

For issues or questions:
1. Check the troubleshooting section
2. Verify all prerequisites are met
3. Ensure proper API key configuration 
