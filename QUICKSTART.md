# 🚀 Quick Start Guide - Fix Installation Error

## The Issue
You encountered: `ERROR: Could not find a version that satisfies the requirement twelvelabs-python`

## ✅ Solution

The correct package name is `twelvelabs`, not `twelvelabs-python`. I've already fixed the files for you.

## 🔧 Installation Steps

### 1. Install the Correct Package

```bash
pip install twelvelabs==0.4.10
```

If you get permission errors, try:
```bash
pip install --user twelvelabs==0.4.10
# OR
pip install --break-system-packages twelvelabs==0.4.10
```

### 2. Install All Dependencies

```bash
pip install -r requirements.txt
```

### 3. Set Up Environment Variables

Create/update your `.env` file:
```env
# Google Gemini API key for speech analysis
GOOGLE_API_KEY=your_google_api_key_here

# Twelvelabs API key for video analysis  
TWELVELABS_API_KEY=your_twelvelabs_api_key_here
```

**Get your API keys:**
- **Google Gemini**: https://makersuite.google.com/app/apikey
- **Twelvelabs**: https://twelvelabs.io (sign up → dashboard → generate API key)

### 4. Test Installation

```bash
python3 -c "from twelvelabs import TwelveLabs; print('✅ Success!')"
```

### 5. Run the Application

```bash
python3 main.py
```

Open http://localhost:8000 in your browser.

## 🎯 What's New with Twelvelabs Integration

### Before (Real-time only)
- ✅ Live speech recognition
- ✅ Real-time body language analysis  
- ✅ Immediate feedback (every 10-30 seconds)

### After (Real-time + Deep Analysis)
- ✅ Everything from before
- 🆕 **Automatic video recording** during practice
- 🆕 **Deep AI analysis** of entire presentation
- 🆕 **Comprehensive insights** with specific recommendations
- 🆕 **Content search** - find specific moments in your video

### Workflow
1. **Start Practice** → Video recording begins automatically
2. **Get Real-time Feedback** → Speech & body language analysis
3. **End Session** → Video uploaded to Twelvelabs for deep analysis
4. **Review Deep Insights** → Comprehensive report with recommendations

## 🔧 Alternative Installation (If Still Having Issues)

### Option 1: Use the Setup Script
```bash
python3 setup.py
```

### Option 2: Manual Installation
```bash
# Install each package individually
pip install fastapi==0.116.1
pip install uvicorn==0.35.0
pip install websockets==15.0.1
pip install google-genai==1.26.0
pip install python-dotenv==1.1.1
pip install requests==2.32.4
pip install twelvelabs==0.4.10
```

### Option 3: Using pipx (if available)
```bash
pipx install twelvelabs==0.4.10
```

## 🚨 Troubleshooting

### Import Error
If you get import errors when running the app:
```bash
python3 -c "import sys; print(sys.path)"
```
Make sure the package is installed in the right Python environment.

### Permission Errors
```bash
# Use user installation
pip install --user twelvelabs==0.4.10

# OR create a virtual environment
python3 -m venv myenv
source myenv/bin/activate  # On Windows: myenv\Scripts\activate
pip install -r requirements.txt
```

### API Key Issues
- Make sure your `.env` file is in the project root
- No quotes needed around the API keys in `.env`
- Check that your API keys are valid and have proper permissions

## 🎉 You're Ready!

Once everything is installed:

1. **Configure API keys** in `.env`
2. **Run** `python3 main.py`
3. **Open** http://localhost:8000
4. **Start practicing** and get both real-time feedback and deep video analysis!

The combination of real-time feedback and Twelvelabs' comprehensive video analysis will give you professional-level insights into your presentation skills.

---

### 📚 Next Steps
- See `README.md` for complete documentation
- Check out the video analysis features
- Practice short presentations to test the system
- Review the detailed feedback and recommendations