# 🔧 Fixing Twelvelabs "Failed Connection" Error

## ❌ **The Error**
```
Error uploading to Twelvelabs: Failed connection
```

## 🔍 **Root Cause**
The "Failed connection" error typically indicates one of these issues:

1. **Missing API Key** ⚠️ (Most Common)
2. **Invalid API Key** 
3. **Network connectivity issues**
4. **Twelvelabs service temporarily unavailable**

## ✅ **Solution Steps**

### **Step 1: Configure Your Twelvelabs API Key**

The most likely cause is that your Twelvelabs API key is not configured.

1. **Create a `.env` file** in your project root directory:
   ```bash
   touch .env
   ```

2. **Add your Twelvelabs API key** to the `.env` file:
   ```env
   # Google Gemini API key for speech analysis
   GOOGLE_API_KEY=your_google_api_key_here
   
   # Twelvelabs API key for video analysis
   TWELVELABS_API_KEY=your_twelvelabs_api_key_here
   ```

3. **Get your Twelvelabs API Key:**
   - Go to [Twelvelabs Dashboard](https://dashboard.twelvelabs.io/)
   - Sign up for a free account if you don't have one
   - Navigate to the "API Keys" section
   - Copy your API key
   - Paste it in the `.env` file (replace `your_twelvelabs_api_key_here`)

### **Step 2: Verify API Key Format**

Your Twelvelabs API key should look like:
```
TWELVELABS_API_KEY=tlk_1234567890abcdef1234567890abcdef
```

- Starts with `tlk_`
- Followed by 32 characters (letters and numbers)
- No quotes around the key
- No spaces

### **Step 3: Test the Connection**

1. **Restart your server** to load the new environment variables:
   ```bash
   python main.py
   ```

2. **Check the startup logs** for:
   ```
   ✅ "Twelvelabs client initialized successfully"
   ```
   
   If you see:
   ```
   ❌ "Warning: TWELVELABS_API_KEY not found in environment variables"
   ```
   Then the API key is not being loaded properly.

### **Step 4: Additional Troubleshooting**

If you still get connection errors after setting the API key:

#### **Check Your Internet Connection:**
```bash
ping api.twelvelabs.io
```

#### **Test API Key Manually:**
```bash
curl -H "x-api-key: your_api_key_here" https://api.twelvelabs.io/v1.2/indexes
```

#### **Check Twelvelabs Service Status:**
- Visit [Twelvelabs Status Page](https://status.twelvelabs.io/) (if available)
- Check their [Discord community](https://discord.com/invite/EFXvh5C6mT) for service updates

## 🎯 **Complete .env File Example**

Create a `.env` file in your project root with this structure:

```env
# Google Gemini API key for speech analysis
GOOGLE_API_KEY=your_google_api_key_here

# Twelvelabs API key for video analysis
TWELVELABS_API_KEY=tlk_your_actual_key_here
```

## 🔍 **Verification Checklist**

After setting up your API key:

- [ ] `.env` file exists in project root
- [ ] `TWELVELABS_API_KEY` is set in `.env`
- [ ] API key starts with `tlk_`
- [ ] No quotes or spaces around the key
- [ ] Server restarted after adding the key
- [ ] Startup message shows "Twelvelabs client initialized successfully"

## 🚀 **Expected Behavior After Fix**

Once the API key is properly configured:

1. **Server startup** will show:
   ```
   ✅ Twelvelabs client initialized successfully
   ```

2. **Video upload** will work without connection errors

3. **Video analysis** will proceed normally:
   ```
   Starting Twelvelabs analysis for videos/session_123_video.webm
   Video uploaded to Twelvelabs. Task ID: 67890abcdef
   Twelvelabs analysis completed for client 123
   ```

## 💡 **Getting Your Twelvelabs API Key**

If you don't have a Twelvelabs account yet:

1. **Sign up** at [https://dashboard.twelvelabs.io/](https://dashboard.twelvelabs.io/)
2. **Free credits** are available for testing
3. **API key** is generated automatically
4. **Copy the key** and add it to your `.env` file

## 🆘 **Still Having Issues?**

If connection errors persist:

1. **Check API key validity** in the Twelvelabs dashboard
2. **Verify your account status** (credits, permissions)
3. **Try a simple API test** using curl or Postman
4. **Contact Twelvelabs support** or check their Discord community

The connection error should be resolved once your API key is properly configured! 🎉