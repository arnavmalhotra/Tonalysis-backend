# Speech Therapy Practice App with Twelvelabs Integration

A real-time speech and presentation practice application that provides:
- **Live speech analysis** using Google Gemini AI
- **Real-time body language detection** using MediaPipe
- **Deep video analysis** using Twelvelabs AI
- **Comprehensive feedback** on presentation skills

## Features

### Real-Time Analysis
- 🎤 **Speech Recognition**: Live transcription with immediate feedback
- 👤 **Body Language Detection**: Emotion, posture, and energy level tracking
- 📊 **Performance Metrics**: Real-time scoring and improvement suggestions

### Deep Video Analysis (Twelvelabs)
- 🎬 **Video Recording**: Automatic session recording during practice
- 🧠 **AI-Powered Insights**: Comprehensive analysis of presentation skills
- 📝 **Detailed Feedback**: Specific recommendations for improvement
- 🔍 **Content Search**: Find specific moments and patterns in your presentation

## Setup Instructions

### 1. Install Dependencies

```bash
# Install Python dependencies
pip install -r requirements.txt

# Note: If you encounter permission issues, use:
pip install --user -r requirements.txt
```

### 2. Configure API Keys

Create a `.env` file in the project root with your API keys:

```env
# Google Gemini API key for speech analysis
GOOGLE_API_KEY=your_google_api_key_here

# Twelvelabs API key for video analysis
TWELVELABS_API_KEY=your_twelvelabs_api_key_here
```

#### Getting API Keys:

**Google Gemini API:**
1. Visit [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Create a new API key
3. Copy the key to your `.env` file

**Twelvelabs API:**
1. Sign up at [Twelvelabs](https://twelvelabs.io)
2. Navigate to your dashboard
3. Generate an API key
4. Copy the key to your `.env` file

### 3. Run the Application

```bash
# Start the server
python main.py

# The app will be available at http://localhost:8000
```

## How It Works

### Session Flow
1. **Start Practice**: Click "Start Practice" to begin a session
2. **Real-Time Feedback**: Get immediate feedback on speech and body language
3. **Video Recording**: Your session is automatically recorded
4. **Deep Analysis**: After ending the session, Twelvelabs analyzes the full video
5. **Comprehensive Report**: Receive detailed insights and recommendations

### Analysis Components

#### Real-Time Analysis (Every 10-30 seconds)
- **Speech Analysis**: Clarity, pace, filler words, vocabulary variety
- **Body Language**: Emotion detection, posture assessment, energy levels
- **Performance Scoring**: Live feedback on your presentation skills

#### Deep Video Analysis (Post-session)
- **Video Summary**: AI-generated overview of your presentation
- **Presentation Analysis**: Detailed breakdown of speaking style and delivery
- **Body Language Insights**: Comprehensive posture and gesture analysis
- **Actionable Recommendations**: Specific improvement suggestions with timestamps

### Twelvelabs Features

The integration with Twelvelabs provides:

1. **Video Understanding**: Advanced AI analysis of your entire presentation
2. **Content Search**: Find specific moments (e.g., "nervous gestures", "confident delivery")
3. **Pattern Recognition**: Identify recurring habits and behaviors
4. **Contextual Insights**: Understand how different parts of your presentation perform
5. **Improvement Tracking**: Compare sessions over time

## Technology Stack

- **Backend**: FastAPI, Python
- **AI Services**: 
  - Google Gemini (speech analysis)
  - Twelvelabs (video analysis)
  - MediaPipe (body language detection)
- **Frontend**: Vanilla JavaScript, WebRTC, MediaRecorder API
- **Real-time Communication**: WebSockets

## File Structure

```
├── main.py                           # Main server with Twelvelabs integration
├── body_language.js                  # MediaPipe body language analysis
├── speech_recognition_client.html    # Frontend with video recording
├── requirements.txt                  # Python dependencies
├── .env                             # API keys configuration
├── videos/                          # Recorded session videos
└── models/                          # MediaPipe model files
```

## API Endpoints

### Video Session Management
- `POST /api/start-video-session/{client_id}` - Start recording session
- `POST /api/upload-video/{client_id}` - Upload recorded video
- `POST /api/end-video-session/{client_id}` - End session and start analysis
- `GET /api/video-session/{client_id}` - Get session status and results

### WebSocket Events
- `video_session_started` - Notify server of recording start
- `video_session_ended` - Notify server of recording end
- `twelvelabs_analysis_complete` - Receive analysis results

## Troubleshooting

### Common Issues

1. **Twelvelabs SDK Installation Error**
   ```bash
   pip install twelvelabs==0.4.10
   ```

2. **Video Recording Not Working**
   - Ensure HTTPS or localhost (required for MediaRecorder)
   - Check browser permissions for camera/microphone
   - Verify WebRTC support

3. **API Key Issues**
   - Verify keys are correctly set in `.env`
   - Check API key permissions and quotas
   - Ensure proper formatting (no quotes needed in .env)

4. **Video Upload Fails**
   - Check video file size (Twelvelabs has limits)
   - Verify network connectivity
   - Check server logs for detailed errors

### Browser Compatibility

- **Chrome**: Fully supported
- **Firefox**: Supported (may need different MediaRecorder options)
- **Safari**: Supported with limitations
- **Edge**: Fully supported

## Advanced Configuration

### Video Recording Settings

Modify the video recording parameters in `speech_recognition_client.html`:

```javascript
const options = {
    mimeType: 'video/webm;codecs=vp9,opus',
    videoBitsPerSecond: 2500000, // Adjust for quality/size balance
    audioBitsPerSecond: 128000
};
```

### Twelvelabs Analysis Engines

The app uses multiple analysis engines for comprehensive insights:

- **Marengo 2.6**: Visual, conversation, text-in-video, logo detection
- **Pegasus 1.1**: Visual and conversation analysis

Modify engines in `main.py` if needed.

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## License

This project is for educational and practice purposes. Please ensure compliance with API terms of service.

## 🆘 Troubleshooting

If you encounter issues:

### **Connection Errors:**
- See `TROUBLESHOOTING_CONNECTION_ISSUES.md` for detailed debugging steps
- Verify your `.env` file contains valid API keys
- Test with smaller video files first

### **API Key Errors:**
- Ensure API keys start with `tlk_` (Twelvelabs) and `AIza` (Google)
- No quotes or extra spaces in the `.env` file
- Regenerate keys if needed

### **Common Issues:**
1. **"Failed connection"** → Check API key and network connectivity
2. **"Index.create() missing models"** → Fixed in latest version
3. **"Invalid model_options"** → Fixed in latest version

### **Getting Help:**
- Check the troubleshooting guides in this repository
- Test with diagnostic scripts provided
- Contact Twelvelabs support if API issues persist

## Support

For issues related to:
- **Twelvelabs API**: [Twelvelabs Documentation](https://docs.twelvelabs.io)
- **Google Gemini**: [Gemini API Documentation](https://ai.google.dev/gemini-api)
- **MediaPipe**: [MediaPipe Documentation](https://developers.google.com/mediapipe)

---

## Next Steps

After setup, try these features:

1. **Practice a short presentation** (2-3 minutes)
2. **Review real-time feedback** during the session
3. **Wait for Twelvelabs analysis** (may take 5-10 minutes)
4. **Explore detailed insights** and recommendations
5. **Practice again** and compare improvements

The combination of real-time feedback and deep video analysis provides a comprehensive view of your presentation skills, helping you improve faster and more effectively. 