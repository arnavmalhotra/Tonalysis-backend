// Background service worker for Voice Transcriber Chrome Extension

// Extension installation and update handling
chrome.runtime.onInstalled.addListener((details) => {
  console.log('Voice Transcriber extension installed/updated');
  
  if (details.reason === 'install') {
    // Set default settings on first install
    chrome.storage.sync.set({
      transcriber_settings: {
        language: 'en-US',
        continuous: true,
        punctuation: true
      }
    });
    
    // Open welcome page or setup instructions
    chrome.tabs.create({
      url: chrome.runtime.getURL('popup.html')
    });
  }
});

// Handle extension icon click - this is mainly handled by popup, but we can add logic here
chrome.action.onClicked.addListener((tab) => {
  // This won't typically fire because we have a popup, but it's here for completeness
  console.log('Extension icon clicked on tab:', tab.url);
});

// Listen for messages from content scripts or popup
chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
  console.log('Background received message:', request);
  
  switch (request.action) {
    case 'startTranscription':
      handleStartTranscription(sender.tab);
      sendResponse({ success: true });
      break;
      
    case 'stopTranscription':
      handleStopTranscription(sender.tab);
      sendResponse({ success: true });
      break;
      
    case 'getStoredTranscription':
      getStoredTranscription().then(sendResponse);
      return true; // Indicates async response
      
    case 'saveTranscription':
      saveTranscription(request.text).then(sendResponse);
      return true; // Indicates async response
      
    case 'updateBadge':
      updateBadge(request.text, request.tabId);
      sendResponse({ success: true });
      break;
      
    case 'getGeminiFeedback':
      getGeminiFeedback(request.text, request.context, request.quickTips).then(sendResponse);
      return true;

    default:
      console.log('Unknown action:', request.action);
      sendResponse({ error: 'Unknown action' });
  }
});

// Handle tab updates to reset badge if needed
chrome.tabs.onUpdated.addListener((tabId, changeInfo, tab) => {
  if (changeInfo.status === 'complete') {
    // Reset badge when page loads
    chrome.action.setBadgeText({ text: '', tabId: tabId });
  }
});

// Handle tab removal to clean up any stored data
chrome.tabs.onRemoved.addListener((tabId, removeInfo) => {
  // Clean up any tab-specific data
  chrome.storage.local.remove(`tab_${tabId}_transcription`);
});

// Functions for handling transcription operations
async function handleStartTranscription(tab) {
  try {
    // Update badge to indicate recording
    chrome.action.setBadgeText({ text: '🎙️', tabId: tab.id });
    chrome.action.setBadgeBackgroundColor({ color: '#f44336', tabId: tab.id });
    
    // Inject content script if not already present
    try {
      await chrome.scripting.executeScript({
        target: { tabId: tab.id },
        files: ['content.js']
      });
    } catch (error) {
      console.log('Content script already injected or injection failed:', error);
    }
    
    // Send message to content script to start transcription
    chrome.tabs.sendMessage(tab.id, { action: 'startTranscription' });
    
  } catch (error) {
    console.error('Error starting transcription:', error);
  }
}

async function handleStopTranscription(tab) {
  try {
    // Reset badge
    chrome.action.setBadgeText({ text: '', tabId: tab.id });
    
    // Send message to content script to stop transcription
    chrome.tabs.sendMessage(tab.id, { action: 'stopTranscription' });
    
  } catch (error) {
    console.error('Error stopping transcription:', error);
  }
}

async function getStoredTranscription() {
  return new Promise((resolve) => {
    chrome.storage.local.get(['last_transcription', 'last_updated'], (result) => {
      resolve({
        transcription: result.last_transcription || '',
        lastUpdated: result.last_updated || null
      });
    });
  });
}

async function saveTranscription(text) {
  return new Promise((resolve) => {
    const data = {
      last_transcription: text,
      last_updated: Date.now()
    };
    
    chrome.storage.local.set(data, () => {
      resolve({ success: true });
    });
  });
}

function updateBadge(text, tabId) {
  if (text && text.length > 0) {
    chrome.action.setBadgeText({ text: '📝', tabId: tabId });
    chrome.action.setBadgeBackgroundColor({ color: '#4CAF50', tabId: tabId });
  } else {
    chrome.action.setBadgeText({ text: '', tabId: tabId });
  }
}

async function getGeminiFeedback(text, context, quickTips) {
  const { apiKey } = await chrome.storage.local.get(['apiKey']);

  if (!apiKey) {
    return { feedback: '❌ No API key found. Please set it in extension options.' };
  }

  let prompt;
  if (quickTips) {
    prompt = `You're a live communication coach. Based only on the transcript below, write 3–4 extremely brief, one-sentence suggestions to help the speaker improve. Each tip must:

    - Be a standalone sentence
    - Be realistic and actionable, like: “Avoid filler words” or “Try starting with a stronger opening”
    - Use a natural and friendly tone
    - Be written as plain sentences with **no bullets, no numbers, no symbols, no headings**
    - Return only the list of tips — nothing else

    Transcript:
    """
    ${text}
    """
    `;
  } else {
    prompt = `do nothing
    `;
  }

  try {
    const response = await fetch(
      `https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key=${apiKey}`,
      {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          contents: [{ parts: [{ text: prompt }] }]
        })
      }
    );
    
    const data = await response.json();
    console.log('Full Gemini API response:', data);

    const feedback = data?.candidates?.[0]?.content?.parts?.[0]?.text;
    return {
      feedback: feedback || '⚠️ Gemini returned no feedback.\n\n(Raw: ' + JSON.stringify(data) + ')'
    };

  } catch (error) {
    console.error('Gemini API error:', error);
    return { feedback: `❌ Error contacting Gemini: ${error.message}` };
  }
}

async function cleanupOldData() {
  try {
    const result = await chrome.storage.local.get(null);
    const cutoffTime = Date.now() - (7 * 24 * 60 * 60 * 1000); // 7 days ago
    
    const keysToRemove = [];
    
    for (const [key, value] of Object.entries(result)) {
      // Remove old tab-specific transcriptions
      if (key.startsWith('tab_') && value.timestamp && value.timestamp < cutoffTime) {
        keysToRemove.push(key);
      }
    }
    
    if (keysToRemove.length > 0) {
      chrome.storage.local.remove(keysToRemove);
      console.log('Cleaned up old transcription data:', keysToRemove.length, 'items');
    }
  } catch (error) {
    console.error('Error during cleanup:', error);
  }
}

// Note: Context menus and keyboard shortcuts removed to avoid permission issues

// Error handling and logging
chrome.runtime.onSuspend.addListener(() => {
  console.log('Voice Transcriber extension suspending');
});

chrome.runtime.onStartup.addListener(() => {
  console.log('Voice Transcriber extension starting up');
}); 