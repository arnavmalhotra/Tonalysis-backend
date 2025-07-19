# 🎬 Where to Find Your Twelvelabs Analysis Results

## 📍 **Location Overview**

The Twelvelabs analysis appears in **TWO main places** in your speech therapy app:

### 1. **💬 Speech Analysis Panel** (Right Sidebar)
### 2. **💡 Real-Time Feedback Cards** (Bottom Left of Video)

---

## 🎯 **Detailed Locations**

### 1. **Main Analysis Panel** (Primary Location)

**Where:** Right sidebar → "💬 Speech Analysis" card

**What you'll see:**
```
💬 Speech Analysis
├── [Your real-time analyses from during the session]
└── 🎬 Deep Video Analysis
    ├── Summary: [AI overview of your presentation]
    ├── Detailed Insights: [Comprehensive breakdown]
    └── Recommendations: [Specific improvement suggestions]
```

**Example Output:**
```
🎬 Deep Video Analysis

Summary:
The speaker demonstrated good vocal clarity and maintained consistent eye contact throughout the presentation. However, there were noticeable nervous gestures and some filler words that detracted from the overall delivery.

Detailed Insights:
Speaking Style & Delivery: The pace was appropriate for the content, with clear articulation. However, the speaker used filler words like "um" and "uh" approximately 12 times during the 3-minute session.

Body Language & Presence: Posture was generally good, though hand gestures became repetitive. Eye contact was maintained 80% of the time, which is excellent for building audience connection.

Recommendations:
• Focus on reducing filler words through practice pauses
• Vary hand gestures for more engaging delivery
• Practice breathing techniques to reduce nervous movements

Powered by Twelvelabs AI Video Understanding
```

### 2. **Real-Time Feedback Cards** (Secondary Display)

**Where:** Bottom left of the video area (floating cards)

**What you'll see:**
- 🎉 "Deep video analysis complete!"
- 💡 "Body Language: Focus on maintaining good posture"
- 👁️ "Eye Contact: Practice maintaining consistent eye contact"
- 🗣️ "Speech Delivery: Work on speech pace and clarity"

These cards appear automatically and fade after 8 seconds.

---

## ⏱️ **Timeline: When Analysis Appears**

### **During Your Session:**
1. **Start Practice** → "Video recording started" (feedback card)
2. **Speaking** → Real-time speech & body language feedback
3. **End Session** → "Processing video for Twelvelabs analysis..." (feedback card)

### **After Your Session:**
4. **Upload Phase** → "Video uploaded! Deep analysis starting..." (feedback card)
5. **Processing Phase** → Status updates every 10 seconds:
   - "Uploading to Twelvelabs..."
   - "Processing video..."
   - "Analyzing content..."
6. **Completion** → **🎉 Full analysis appears!**

---

## 🎨 **Visual Example**

```
┌─────────────────────────────────────────────────────────────┐
│  🎥 Video Area                          📊 Right Sidebar    │
│                                        ┌─────────────────┐   │
│                                        │ 💬 Speech Analysis│   │
│  ┌─ Feedback Cards (Bottom Left)       │                 │   │
│  │ 💡 Eye Contact: Practice...         │ Analysis #1...  │   │
│  │ 🎉 Deep analysis complete!          │                 │   │
│  └─                                    │ 🎬 Deep Video   │   │
│                                        │ Analysis        │   │
│                                        │                 │   │
│                                        │ Summary: The    │   │
│                                        │ speaker showed  │   │
│                                        │ good clarity... │   │
│                                        │                 │   │
│                                        │ Detailed        │   │
│                                        │ Insights: ...   │   │
│                                        │                 │   │
│                                        │ Recommendations:│   │
│                                        │ • Reduce fillers│   │
│                                        │ • Improve pace  │   │
│                                        └─────────────────┘   │
└─────────────────────────────────────────────────────────────┘
```

---

## 🔍 **What Analysis Includes**

### **📋 Summary Section**
- Overall assessment of your presentation
- Key strengths and areas for improvement
- Professional-level evaluation

### **🔍 Detailed Insights**
- **Speaking Style & Delivery:** Pace, clarity, volume, pauses
- **Body Language & Presence:** Posture, gestures, facial expressions
- **Content Organization:** Structure, flow, engagement techniques
- **Areas for Improvement:** Specific actionable feedback

### **✅ Recommendations**
- Categorized suggestions (Body Language, Eye Contact, Speech Delivery)
- Timestamped examples from your video
- Specific practice exercises
- Next steps for development

---

## ⚡ **Quick Access Tips**

### **To See Analysis Faster:**
1. Keep the right sidebar open during practice
2. Watch for the green "🎉 Deep video analysis complete!" card
3. Scroll down in the Speech Analysis panel to see the new section

### **If Analysis Doesn't Appear:**
1. **Check the browser console** (F12) for any errors
2. **Verify your API key** is set in `.env`
3. **Wait a bit longer** - analysis can take 5-10 minutes
4. **Check feedback cards** for error messages

### **To Review Later:**
- The analysis stays in the Speech Analysis panel until you start a new session
- You can scroll through all the feedback in the sidebar
- Screenshots recommended for keeping records

---

## 🚀 **Pro Tips**

1. **Multiple Sessions:** Each new practice session adds analysis below the previous one
2. **Best View:** Expand your browser window for better readability
3. **Mobile:** On mobile, swipe to see the right sidebar
4. **Debugging:** Check browser console (F12) if analysis doesn't appear

The Twelvelabs analysis provides professional-level insights that complement the real-time feedback, giving you a complete picture of your presentation skills! 🎯