# 🔧 Troubleshooting Twelvelabs "Failed Connection" Error

## ❌ **The Error**
```
Error uploading to Twelvelabs: Failed connection
```

## 🔍 **Root Cause Analysis**

The "Failed connection" error can have several causes. Let's diagnose and fix them systematically:

### **1. API Key Issues** ⚠️ (Most Common)

Even if your API key is in the `.env` file, it might not be properly loaded or valid.

#### **Diagnostic Steps:**
```bash
# Test if your API key is loaded
python3 -c "
import os
from dotenv import load_dotenv
load_dotenv()
api_key = os.getenv('TWELVELABS_API_KEY')
print(f'API Key loaded: {api_key[:10]}...' if api_key else 'API Key not found!')
print(f'Starts with tlk_: {api_key.startswith(\"tlk_\") if api_key else False}')
"
```

#### **Solutions:**
1. **Verify API key format:**
   - Should start with `tlk_`
   - Should be 32+ characters long
   - No extra spaces or quotes

2. **Test API key manually:**
   ```bash
   curl -H "x-api-key: your_actual_key_here" https://api.twelvelabs.io/v1.2/indexes
   ```

3. **Regenerate API key:**
   - Go to [Twelvelabs Dashboard](https://dashboard.twelvelabs.io/)
   - Generate a new API key
   - Update your `.env` file

### **2. Network/Firewall Issues**

#### **Diagnostic Steps:**
```bash
# Test basic connectivity to Twelvelabs
ping api.twelvelabs.io

# Test HTTPS connectivity
curl -I https://api.twelvelabs.io/v1.2/

# Check if you're behind a corporate firewall
curl -v https://api.twelvelabs.io/v1.2/ 2>&1 | grep -i proxy
```

#### **Solutions:**
1. **Check firewall settings**
2. **Configure proxy if needed**
3. **Try from a different network**

### **3. File Upload Issues**

#### **Common Problems:**
- File too large (>2GB limit)
- Unsupported video format
- Corrupted video file
- Insufficient permissions

#### **Diagnostic Steps:**
```bash
# Check video file
ls -la videos/your_video_file.webm
file videos/your_video_file.webm
```

#### **Solutions:**
1. **Check file size:** Maximum 2GB
2. **Verify format:** MP4, WebM, AVI, MOV supported
3. **Test with a small sample video first**

### **4. SDK Version Issues**

#### **Check Current Version:**
```bash
pip show twelvelabs
```

#### **Update to Latest:**
```bash
pip install --upgrade twelvelabs
```

### **5. Rate Limiting/Service Issues**

#### **Diagnostic Steps:**
```bash
# Check Twelvelabs service status
curl -I https://api.twelvelabs.io/v1.2/health 2>/dev/null | head -1
```

#### **Solutions:**
1. **Wait and retry** (rate limiting)
2. **Check [Twelvelabs Status Page](https://status.twelvelabs.io/)** (if available)
3. **Contact Twelvelabs support**

## 🛠️ **Systematic Troubleshooting Steps**

### **Step 1: Basic Environment Check**
```bash
# 1. Check if .env file exists and has the right content
cat .env

# 2. Verify Python can load the environment
python3 -c "
from dotenv import load_dotenv
import os
load_dotenv()
print('TWELVELABS_API_KEY:', 'SET' if os.getenv('TWELVELABS_API_KEY') else 'NOT SET')
print('GOOGLE_API_KEY:', 'SET' if os.getenv('GOOGLE_API_KEY') else 'NOT SET')
"
```

### **Step 2: Test API Connectivity**
```bash
# Create test script
cat > test_connection.py << 'EOF'
import os
from dotenv import load_dotenv
from twelvelabs import TwelveLabs

load_dotenv()
api_key = os.getenv('TWELVELABS_API_KEY')

if not api_key:
    print("❌ No API key found!")
    exit(1)

print(f"✅ API key found: {api_key[:10]}...")

try:
    client = TwelveLabs(api_key=api_key)
    indexes = client.index.list()
    print("✅ Successfully connected to Twelvelabs!")
    print(f"✅ Found {len(indexes)} indexes")
except Exception as e:
    print(f"❌ Connection failed: {e}")
EOF

python3 test_connection.py
```

### **Step 3: Test with Minimal Example**
```bash
# Create minimal test
cat > minimal_test.py << 'EOF'
import os
from dotenv import load_dotenv
from twelvelabs import TwelveLabs

load_dotenv()
client = TwelveLabs(api_key=os.getenv('TWELVELABS_API_KEY'))

try:
    # Just try to list indexes (no file upload)
    result = client.index.list()
    print("✅ Basic API calls work!")
    
    # If you have a small test video
    # task = client.task.create(
    #     index_id="your_index_id", 
    #     file="small_test_video.mp4"
    # )
    # print("✅ File upload works!")
    
except Exception as e:
    print(f"❌ Error: {e}")
    print(f"❌ Error type: {type(e)}")
EOF

python3 minimal_test.py
```

## 🔧 **Immediate Fixes to Try**

### **Fix 1: Update Your .env File**
Make sure your `.env` file looks exactly like this:
```env
# Google Gemini API key for speech analysis
GOOGLE_API_KEY=your_actual_google_key_here

# Twelvelabs API key for video analysis
TWELVELABS_API_KEY=tlk_your_actual_key_here
```

### **Fix 2: Restart Everything**
```bash
# Kill any running processes
pkill -f "python.*main.py"

# Clear Python cache
find . -name "*.pyc" -delete
find . -name "__pycache__" -type d -exec rm -rf {} +

# Restart the server
python3 main.py
```

### **Fix 3: Test with Different Video**
```bash
# Try with a very small test video first
curl -o test_video.mp4 "https://sample-videos.com/zip/10/mp4/SampleVideo_360x240_1mb.mp4"

# Then test the upload with this smaller file
```

### **Fix 4: Temporary Workaround**
If nothing else works, you can temporarily disable Twelvelabs:

```python
# In main.py, add this at the top:
TWELVELABS_ENABLED = False  # Set to False to disable

# Then modify the upload section:
if not TWELVELABS_ENABLED:
    print("Twelvelabs disabled - skipping video analysis")
    session["status"] = "completed"
    return
```

## 🎯 **Expected Results After Fix**

Once fixed, you should see:
```
✅ Twelvelabs client initialized successfully
✅ Video uploaded to Twelvelabs. Task ID: abc123
✅ Twelvelabs analysis completed for client xyz
```

## 🆘 **Still Not Working?**

1. **Share the exact error message** you're seeing
2. **Test with the diagnostic scripts** above
3. **Check your account status** at Twelvelabs dashboard
4. **Contact Twelvelabs support** with:
   - Your API key (first 10 characters only)
   - The exact error message
   - Video file details (size, format)
   - Your SDK version

## 💡 **Prevention Tips**

1. **Always test with small files first**
2. **Monitor your API usage/credits**
3. **Keep your SDK updated**
4. **Have backup error handling**
5. **Log detailed error information**

This comprehensive troubleshooting should help identify and resolve the connection issue! 🎉