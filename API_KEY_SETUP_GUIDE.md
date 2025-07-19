# 🔑 API Key Setup Guide

## 🎯 **The Issue**

Your `.env` file exists but contains **placeholder values** instead of your actual API keys. This is why you're getting the "Failed connection" error.

**Current `.env` file:**
```env
TWELVELABS_API_KEY=your_twelvelabs_api_key_here  # ❌ This is a placeholder!
```

**What you need:**
```env
TWELVELABS_API_KEY=tlk_1234567890abcdef1234567890abcdef  # ✅ Real API key
```

## 🚀 **Step-by-Step Fix**

### **Step 1: Get Your Twelvelabs API Key**

1. **Visit the Twelvelabs Dashboard:**
   - Go to [https://dashboard.twelvelabs.io/](https://dashboard.twelvelabs.io/)

2. **Sign up or Sign in:**
   - Create a free account if you don't have one
   - Sign in if you already have an account

3. **Navigate to API Keys:**
   - Look for "API Keys" or "Settings" in the dashboard
   - Find the section that shows your API key

4. **Copy Your API Key:**
   - Your key should start with `tlk_`
   - It will be about 32 characters long
   - Example: `tlk_1234567890abcdef1234567890abcdef`

### **Step 2: Update Your .env File**

1. **Open the `.env` file** in your project directory

2. **Replace the placeholder** with your actual API key:

   **Before:**
   ```env
   TWELVELABS_API_KEY=your_twelvelabs_api_key_here
   ```

   **After:**
   ```env
   TWELVELABS_API_KEY=tlk_your_actual_key_from_dashboard
   ```

3. **Save the file**

### **Step 3: Get Your Google Gemini API Key (if needed)**

If you also need to set up the Google API key:

1. **Visit Google AI Studio:**
   - Go to [https://aistudio.google.com/](https://aistudio.google.com/)

2. **Get API Key:**
   - Click "Get API Key"
   - Create a new API key

3. **Update .env:**
   ```env
   GOOGLE_API_KEY=your_actual_google_api_key
   ```

### **Step 4: Restart Your Application**

```bash
python main.py
```

## 🔍 **How to Verify It's Working**

After updating your API keys, you should see:

### **✅ Successful Startup Messages:**
```
Twelvelabs client initialized successfully
Starting speech therapy server...
```

### **❌ Error Messages to Watch For:**
```
Warning: TWELVELABS_API_KEY not found in environment variables
Failed to initialize Twelvelabs client
```

## 📋 **Complete .env File Example**

Your final `.env` file should look like this:

```env
# Google Gemini API key for speech analysis
GOOGLE_API_KEY=AIzaSyB1234567890abcdef1234567890abcdef

# Twelvelabs API key for video analysis
TWELVELABS_API_KEY=tlk_1234567890abcdef1234567890abcdef
```

## 🔐 **Security Best Practices**

- ✅ **Never commit** your `.env` file to version control
- ✅ **Keep your API keys private**
- ✅ **Don't share** your keys in screenshots or messages
- ✅ **Regenerate keys** if they're accidentally exposed

## 🆘 **Still Having Issues?**

### **If you can't find your Twelvelabs API key:**
1. Check all sections of the Twelvelabs dashboard
2. Look for "Account Settings" or "Developer Settings"
3. Contact Twelvelabs support if needed

### **If the connection still fails:**
1. Double-check the API key format (starts with `tlk_`)
2. Ensure there are no extra spaces or quotes
3. Try regenerating a new API key
4. Check your account status and credits

### **Test your API key manually:**
```bash
curl -H "x-api-key: tlk_your_actual_key" https://api.twelvelabs.io/v1.2/indexes
```

## 🎉 **Success!**

Once your API keys are properly configured:
- ✅ No more connection errors
- ✅ Video recording and upload works
- ✅ Twelvelabs analysis provides deep insights
- ✅ Your speech therapy app is fully functional

**Remember:** Replace the placeholder text with your actual API keys from the respective dashboards!