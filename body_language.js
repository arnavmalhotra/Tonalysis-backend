(function() {
    'use strict';
    
    // Global variables
    let videoElement = null;
    let canvasElement = null;
    let canvasContext = null;
    let websocket = null;
    let lastPostTime = 0;
    let isProcessing = false;
    let emotionHistory = [];
    let faceMesh = null;
    let camera = null;
    
    // Initialize MediaPipe Face Mesh
    async function initializeFaceMesh() {
        try {
            console.log('Initializing MediaPipe Face Mesh...');
            
            faceMesh = new FaceMesh({
                locateFile: (file) => {
                    return `https://cdn.jsdelivr.net/npm/@mediapipe/face_mesh/${file}`;
                }
            });
            
            faceMesh.setOptions({
                maxNumFaces: 1,
                refineLandmarks: true,
                minDetectionConfidence: 0.5,
                minTrackingConfidence: 0.5
            });
            
            faceMesh.onResults(onFaceMeshResults);
            console.log('MediaPipe Face Mesh initialized successfully');
            return true;
            
        } catch (error) {
            console.error('Failed to initialize Face Mesh:', error);
            return false;
        }
    }
    
    // Handle Face Mesh results
    function onFaceMeshResults(results) {
        if (!results.multiFaceLandmarks || results.multiFaceLandmarks.length === 0) {
            console.log('No face detected');
            updateEmotionUI({ emotion: 'neutral', confidence: 0.5 }, null, null);
            return;
        }
        
        const landmarks = results.multiFaceLandmarks[0];
        const emotion = analyzeEmotionFromLandmarks(landmarks);
        
        // Draw face mesh
        drawFaceMesh(results.multiFaceLandmarks[0]);
        
        // Update emotion history
        emotionHistory.push({ 
            emotion: emotion.emotion, 
            confidence: emotion.confidence, 
            faceDetected: true 
        });
        if (emotionHistory.length > 10) {
            emotionHistory.shift();
        }
        
        // Get stable emotion
        const stableEmotion = getStableEmotion();
        
        // Update UI
        updateEmotionUI(stableEmotion, analyzePosture(landmarks), analyzeFatigue(landmarks));
        
        // Send to server every 2 seconds
        const timestamp = Date.now();
        if (timestamp - lastPostTime > 2000 && websocket?.readyState === WebSocket.OPEN) {
            const postureData = analyzePosture(landmarks);
            const fatigueData = analyzeFatigue(landmarks);
            
            websocket.send(JSON.stringify({
                type: 'body_language',
                emotion: stableEmotion.emotion,
                posture: postureData,
                fatigue: fatigueData,
                confidence: {
                    emotion: stableEmotion.confidence,
                    posture: postureData.confidence,
                    fatigue: fatigueData.confidence
                },
                timestamp: new Date().toISOString()
            }));
            lastPostTime = timestamp;
            console.log('Body language data sent to server');
        }
    }
    
    // Analyze emotion using MediaPipe landmarks (468 points)
    function analyzeEmotionFromLandmarks(landmarks) {
        if (!landmarks || landmarks.length < 468) {
            return { emotion: 'neutral', confidence: 0.5 };
        }
        
        try {
            // Key facial landmark indices
            const LEFT_EYE = [33, 7, 163, 144, 145, 153, 154, 155, 133, 173, 157, 158, 159, 160, 161, 246];
            const RIGHT_EYE = [362, 382, 381, 380, 374, 373, 390, 249, 263, 466, 388, 387, 386, 385, 384, 398];
            const MOUTH = [61, 84, 17, 314, 405, 320, 307, 375, 321, 308, 324, 318];
            
            // Calculate eye openness
            const leftEyeOpenness = calculateEyeOpenness(landmarks, LEFT_EYE);
            const rightEyeOpenness = calculateEyeOpenness(landmarks, RIGHT_EYE);
            const eyeOpenness = (leftEyeOpenness + rightEyeOpenness) / 2;
            
            // Calculate mouth openness
            const mouthOpenness = calculateMouthOpenness(landmarks, MOUTH);
            
            // Calculate eyebrow position
            const leftEyebrow = calculateEyebrowPosition(landmarks, [70, 63, 105, 66, 107]);
            const rightEyebrow = calculateEyebrowPosition(landmarks, [336, 296, 334, 293, 300]);
            const eyebrowPosition = (leftEyebrow + rightEyebrow) / 2;
            
            // Calculate mouth corner lift (smile detection)
            const mouthCornerLift = calculateMouthCornerLift(landmarks);
            
            console.log(`Facial metrics: eyeOpenness=${eyeOpenness.toFixed(3)}, mouthOpenness=${mouthOpenness.toFixed(3)}, eyebrowPosition=${eyebrowPosition.toFixed(3)}, mouthCornerLift=${mouthCornerLift.toFixed(3)}`);
            
            // More sensitive emotion detection with scoring system
            let emotion = 'neutral';
            let confidence = 0.5;
            
            // Calculate emotion scores
            const emotionScores = {
                happy: 0,
                sad: 0,
                surprised: 0,
                angry: 0,
                fearful: 0,
                disgusted: 0,
                neutral: 0
            };
            
            // Happy scoring: raised mouth corners, slight eye squint
            if (mouthCornerLift > 0.005) emotionScores.happy += 1;
            if (mouthCornerLift > 0.01) emotionScores.happy += 1;
            if (eyeOpenness < 0.15) emotionScores.happy += 1;
            
            // Sad scoring: drooping mouth corners, lowered eyebrows
            if (mouthCornerLift < -0.005) emotionScores.sad += 1;
            if (mouthCornerLift < -0.01) emotionScores.sad += 1;
            if (eyebrowPosition > 0.35) emotionScores.sad += 1;
            
            // Surprised scoring: wide eyes, open mouth, raised eyebrows
            if (eyeOpenness > 0.2) emotionScores.surprised += 1;
            if (eyeOpenness > 0.25) emotionScores.surprised += 1;
            if (mouthOpenness > 0.25) emotionScores.surprised += 1;
            if (eyebrowPosition < 0.3) emotionScores.surprised += 1;
            
            // Angry scoring: furrowed brow, tight mouth
            if (eyebrowPosition > 0.4) emotionScores.angry += 1;
            if (mouthOpenness < 0.1) emotionScores.angry += 1;
            if (eyeOpenness < 0.1) emotionScores.angry += 1;
            
            // Fearful scoring: very wide eyes, open mouth
            if (eyeOpenness > 0.3) emotionScores.fearful += 1;
            if (mouthOpenness > 0.3) emotionScores.fearful += 1;
            if (eyebrowPosition < 0.25) emotionScores.fearful += 1;
            
            // Disgusted scoring: wrinkled nose area, small mouth
            if (mouthOpenness < 0.15) emotionScores.disgusted += 1;
            if (eyebrowPosition > 0.45) emotionScores.disgusted += 1;
            
            // Neutral scoring: balanced features
            if (Math.abs(mouthCornerLift) < 0.005) emotionScores.neutral += 1;
            if (eyeOpenness > 0.1 && eyeOpenness < 0.2) emotionScores.neutral += 1;
            if (mouthOpenness > 0.1 && mouthOpenness < 0.2) emotionScores.neutral += 1;
            
            // Find highest scoring emotion
            const maxScore = Math.max(...Object.values(emotionScores));
            const bestEmotion = Object.keys(emotionScores).find(key => emotionScores[key] === maxScore);
            
            if (maxScore >= 1) {
                emotion = bestEmotion;
                confidence = 0.6 + (maxScore - 1) * 0.1;
            } else {
                emotion = 'neutral';
                confidence = 0.7;
            }
            
            return { emotion, confidence };
            
        } catch (error) {
            console.error('Emotion analysis error:', error);
            return { emotion: 'neutral', confidence: 0.5 };
        }
    }
    
    // Calculate eye openness
    function calculateEyeOpenness(landmarks, eyeIndices) {
        const eyePoints = eyeIndices.map(i => landmarks[i]);
        const eyeHeight = Math.abs(eyePoints[1].y - eyePoints[5].y);
        const eyeWidth = Math.abs(eyePoints[0].x - eyePoints[8].x);
        return eyeHeight / eyeWidth;
    }
    
    // Calculate mouth openness
    function calculateMouthOpenness(landmarks, mouthIndices) {
        const mouthPoints = mouthIndices.map(i => landmarks[i]);
        const mouthHeight = Math.abs(mouthPoints[1].y - mouthPoints[7].y);
        const mouthWidth = Math.abs(mouthPoints[0].x - mouthPoints[6].x);
        return mouthHeight / mouthWidth;
    }
    
    // Calculate eyebrow position
    function calculateEyebrowPosition(landmarks, eyebrowIndices) {
        const eyebrowPoints = eyebrowIndices.map(i => landmarks[i]);
        const avgY = eyebrowPoints.reduce((sum, point) => sum + point.y, 0) / eyebrowPoints.length;
        return avgY;
    }
    
    // Calculate mouth corner lift (smile detection)
    function calculateMouthCornerLift(landmarks) {
        // Get mouth corner points
        const leftCorner = landmarks[61];  // Left mouth corner
        const rightCorner = landmarks[291]; // Right mouth corner
        const leftUpperLip = landmarks[0];  // Upper lip left
        const rightUpperLip = landmarks[17]; // Upper lip right
        
        // Calculate the vertical lift of mouth corners relative to upper lip
        const leftLift = leftUpperLip.y - leftCorner.y;
        const rightLift = rightUpperLip.y - rightCorner.y;
        
        // Average lift (positive = smile, negative = frown)
        return (leftLift + rightLift) / 2;
    }
    
    // Draw face mesh
    function drawFaceMesh(landmarks) {
        if (!canvasContext || !canvasElement) return;
        
        canvasContext.clearRect(0, 0, canvasElement.width, canvasElement.height);
        
        // Draw face mesh connections
        canvasContext.strokeStyle = '#00ff00';
        canvasContext.lineWidth = 1;
        
        // Draw key facial features
        const connections = [
            // Face outline
            [10, 338, 297, 332, 284, 251, 389, 356, 454, 323, 361, 288, 397, 365, 379, 378, 400, 377, 152, 148, 176, 149, 150, 136, 172, 58, 132, 93, 234, 127, 162, 21, 54, 103, 67, 109, 10],
            // Eyes
            [33, 7, 163, 144, 145, 153, 154, 155, 133, 173, 157, 158, 159, 160, 161, 246],
            [362, 382, 381, 380, 374, 373, 390, 249, 263, 466, 388, 387, 386, 385, 384, 398],
            // Mouth
            [61, 84, 17, 314, 405, 320, 307, 375, 321, 308, 324, 318]
        ];
        
        connections.forEach(connection => {
            canvasContext.beginPath();
            connection.forEach((index, i) => {
                const point = landmarks[index];
                const x = point.x * canvasElement.width;
                const y = point.y * canvasElement.height;
                
                if (i === 0) {
                    canvasContext.moveTo(x, y);
                } else {
                    canvasContext.lineTo(x, y);
                }
            });
            canvasContext.stroke();
        });
        
        // Draw landmark points
        canvasContext.fillStyle = '#ff0000';
        landmarks.forEach(landmark => {
            const x = landmark.x * canvasElement.width;
            const y = landmark.y * canvasElement.height;
            canvasContext.beginPath();
            canvasContext.arc(x, y, 1, 0, 2 * Math.PI);
            canvasContext.fill();
        });
    }
    
    // Initialize camera
    async function initializeCamera() {
        try {
            videoElement = document.getElementById('video');
            canvasElement = document.getElementById('canvas');
            
            if (!videoElement || !canvasElement) {
                console.error('Video or canvas element not found');
                return false;
            }
            
            canvasContext = canvasElement.getContext('2d');
            
            // Set canvas size
            canvasElement.width = 640;
            canvasElement.height = 480;
            
            // Initialize MediaPipe camera
            camera = new Camera(videoElement, {
                onFrame: async () => {
                    if (faceMesh) {
                        await faceMesh.send({ image: videoElement });
                    }
                },
                width: 640,
                height: 480
            });
            
            await camera.start();
            console.log('MediaPipe camera started successfully');
            
            return true;
            
        } catch (error) {
            console.error('Camera initialization error:', error);
            return false;
        }
    }
    
    // Update emotion UI
    function updateEmotionUI(emotion, postureData, fatigueData) {
        const emotionElement = document.getElementById('emotionMetric');
        const postureElement = document.getElementById('postureMetric');
        const fatigueElement = document.getElementById('fatigueMetric');
        
        if (emotionElement) {
            emotionElement.textContent = `Emotion: ${emotion.emotion}`;
            emotionElement.className = 'metric';
            if (['happy', 'surprised'].includes(emotion.emotion)) {
                emotionElement.classList.add('good');
            } else if (['sad', 'angry', 'fearful', 'disgusted'].includes(emotion.emotion)) {
                emotionElement.classList.add('alert');
            } else {
                emotionElement.classList.add('warning');
            }
        }
        
        if (postureElement && postureData) {
            postureElement.textContent = `Posture: ${postureData.label}`;
            postureElement.className = 'metric';
            if (postureData.label === 'excellent' || postureData.label === 'good') {
                postureElement.classList.add('good');
            } else if (postureData.label === 'poor') {
                postureElement.classList.add('alert');
            } else {
                postureElement.classList.add('warning');
            }
        }
        
        if (fatigueElement && fatigueData) {
            fatigueElement.textContent = `Energy: ${fatigueData.label}`;
            fatigueElement.className = 'metric';
            if (fatigueData.label === 'alert') {
                fatigueElement.classList.add('good');
            } else if (fatigueData.label === 'tired' || fatigueData.label === 'very tired') {
                fatigueElement.classList.add('alert');
            } else {
                fatigueElement.classList.add('warning');
            }
        }
    }
    
    // Analyze posture based on facial features and head position
    function analyzePosture(landmarks) {
        if (!landmarks || landmarks.length < 468) {
            return { label: 'unknown', confidence: 0.5 };
        }
        
        try {
            // Get head position landmarks
            const nose = landmarks[1];
            const leftEye = landmarks[33];
            const rightEye = landmarks[362];
            const leftEar = landmarks[234];
            const rightEar = landmarks[454];
            
            // Calculate head tilt (how straight the head is)
            const eyeCenterX = (leftEye.x + rightEye.x) / 2;
            const earCenterX = (leftEar.x + rightEar.x) / 2;
            const headTilt = Math.abs(eyeCenterX - earCenterX);
            
            // Calculate head position (how centered)
            const headCentered = Math.abs(nose.x - 0.5); // 0.5 is center
            
            // Calculate eye level (how alert)
            const eyeLevel = (leftEye.y + rightEye.y) / 2;
            
            console.log(`Posture metrics: headTilt=${headTilt.toFixed(3)}, headCentered=${headCentered.toFixed(3)}, eyeLevel=${eyeLevel.toFixed(3)}`);
            
            let posture = 'good';
            let confidence = 0.6;
            
            // Good posture: straight head, centered, alert eyes
            if (headTilt < 0.05 && headCentered < 0.1 && eyeLevel < 0.4) {
                posture = 'excellent';
                confidence = 0.9;
            } else if (headTilt < 0.1 && headCentered < 0.2 && eyeLevel < 0.5) {
                posture = 'good';
                confidence = 0.8;
            } else if (headTilt > 0.15 || headCentered > 0.3 || eyeLevel > 0.6) {
                posture = 'poor';
                confidence = 0.7;
            } else {
                posture = 'fair';
                confidence = 0.6;
            }
            
            return { label: posture, confidence };
            
        } catch (error) {
            console.error('Posture analysis error:', error);
            return { label: 'unknown', confidence: 0.5 };
        }
    }
    
    // Analyze energy/fatigue based on facial features
    function analyzeFatigue(landmarks) {
        if (!landmarks || landmarks.length < 468) {
            return { label: 'unknown', confidence: 0.5 };
        }
        
        try {
            // Get fatigue-related landmarks
            const leftEye = landmarks[33];
            const rightEye = landmarks[362];
            const leftEyebrow = landmarks[70];
            const rightEyebrow = landmarks[336];
            const leftEyelid = landmarks[160];
            const rightEyelid = landmarks[387];
            
            // Calculate eye openness (droopy eyes = tired)
            const leftEyeOpenness = calculateEyeOpenness(landmarks, [33, 7, 163, 144, 145, 153, 154, 155, 133, 173, 157, 158, 159, 160, 161, 246]);
            const rightEyeOpenness = calculateEyeOpenness(landmarks, [362, 382, 381, 380, 374, 373, 390, 249, 263, 466, 388, 387, 386, 385, 384, 398]);
            const eyeOpenness = (leftEyeOpenness + rightEyeOpenness) / 2;
            
            // Calculate eyebrow position (lowered eyebrows = tired)
            const leftEyebrowPos = calculateEyebrowPosition(landmarks, [70, 63, 105, 66, 107]);
            const rightEyebrowPos = calculateEyebrowPosition(landmarks, [336, 296, 334, 293, 300]);
            const eyebrowPosition = (leftEyebrowPos + rightEyebrowPos) / 2;
            
            // Calculate eyelid droop
            const leftEyelidDroop = leftEyelid.y - leftEye.y;
            const rightEyelidDroop = rightEyelid.y - rightEye.y;
            const eyelidDroop = (leftEyelidDroop + rightEyelidDroop) / 2;
            
            console.log(`Fatigue metrics: eyeOpenness=${eyeOpenness.toFixed(3)}, eyebrowPosition=${eyebrowPosition.toFixed(3)}, eyelidDroop=${eyelidDroop.toFixed(3)}`);
            
            let fatigue = 'alert';
            let confidence = 0.6;
            
            // Alert: wide eyes, raised eyebrows, no droop
            if (eyeOpenness > 0.15 && eyebrowPosition < 0.35 && eyelidDroop < 0.02) {
                fatigue = 'alert';
                confidence = 0.9;
            } else if (eyeOpenness > 0.1 && eyebrowPosition < 0.4 && eyelidDroop < 0.03) {
                fatigue = 'alert';
                confidence = 0.8;
            } else if (eyeOpenness < 0.08 || eyebrowPosition > 0.45 || eyelidDroop > 0.04) {
                fatigue = 'tired';
                confidence = 0.8;
            } else if (eyeOpenness < 0.05 || eyebrowPosition > 0.5 || eyelidDroop > 0.06) {
                fatigue = 'very tired';
                confidence = 0.9;
            } else {
                fatigue = 'moderate';
                confidence = 0.6;
            }
            
            return { label: fatigue, confidence };
            
        } catch (error) {
            console.error('Fatigue analysis error:', error);
            return { label: 'unknown', confidence: 0.5 };
        }
    }
    
    // Get stable emotion from history
    function getStableEmotion() {
        if (emotionHistory.length === 0) {
            return { emotion: 'neutral', confidence: 0.5 };
        }
        
        // Require at least 2 recent detections for stability
        const recentHistory = emotionHistory.slice(-5);
        const faceDetectedCount = recentHistory.filter(item => item.faceDetected).length;
        
        if (faceDetectedCount < 2) {
            return { emotion: 'neutral', confidence: 0.5 };
        }
        
        // Count emotions in recent history
        const emotionCounts = {};
        recentHistory.forEach(item => {
            if (item.faceDetected && item.confidence > 0.5) { // Lower threshold
                emotionCounts[item.emotion] = (emotionCounts[item.emotion] || 0) + 1;
            }
        });
        
        if (Object.keys(emotionCounts).length === 0) {
            return { emotion: 'neutral', confidence: 0.5 };
        }
        
        // Get most common emotion
        const mostCommonEmotion = Object.keys(emotionCounts).reduce((a, b) => 
            emotionCounts[a] > emotionCounts[b] ? a : b);
        
        const emotionCount = emotionCounts[mostCommonEmotion];
        const totalFrames = faceDetectedCount;
        const confidence = emotionCount / totalFrames;
        
        // Require at least 40% consistency for emotion detection (less strict)
        if (confidence < 0.4) {
            return { emotion: 'neutral', confidence: 0.7 };
        }
        
        return { 
            emotion: mostCommonEmotion, 
            confidence: Math.max(confidence, 0.5)
        };
    }
    
    // Public API
    window.bodyLanguage = {
        async start() {
            console.log('Starting MediaPipe Face Mesh emotion detection...');
            
            // Initialize Face Mesh first
            const meshOk = await initializeFaceMesh();
            if (!meshOk) {
                console.error('Failed to initialize Face Mesh');
                return false;
            }
            
            // Initialize camera
            const cameraOk = await initializeCamera();
            if (!cameraOk) {
                console.error('Failed to initialize camera');
                return false;
            }
            
            console.log('MediaPipe Face Mesh emotion detection started successfully');
            return true;
        },
        
        setWebSocket(ws) {
            websocket = ws;
        }
    };
    
})(); 