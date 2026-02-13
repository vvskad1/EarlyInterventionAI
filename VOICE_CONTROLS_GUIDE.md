# Voice Control Features

## Overview
The Early Intervention AI now includes voice control features using the Web Speech API:
- 🎤 **Speech-to-Text**: Speak your messages instead of typing
- 🔊 **Text-to-Speech**: Have responses read aloud automatically

## Features

### 1. Speech-to-Text (Microphone Button)
- **Click** the microphone icon (🎤) to start voice input
- Speak your message clearly
- **Click again** when done speaking
- The message will **automatically send** when you stop recording
- Text appears in real-time as you speak

**Visual Indicators:**
- Grey mic icon = ready to listen (click to start)
- Red pulsing mic icon = actively listening (click to stop & send)

**How to Use:**
1. Click the microphone button to start
2. Speak your message (pauses are OK)
3. Click the microphone again to stop
4. Message automatically sends
5. AI responds (and reads aloud if speaker is enabled)

### 2. Text-to-Speech (Speaker Button)
- Click the speaker icon (🔊) to toggle auto-read mode
- When enabled (blue icon), AI responses will be read aloud automatically
- When disabled (grey icon), responses are text-only
- Perfect for hands-free use during home visits

**Visual Indicators:**
- Blue speaker icon = auto-read ON
- Grey speaker icon = auto-read OFF

## Browser Compatibility

### Fully Supported (Recommended):
- ✅ Google Chrome (desktop & mobile)
- ✅ Microsoft Edge
- ✅ Safari (macOS & iOS)

### Partial Support:
- ⚠️ Firefox (speech recognition may not work)
- ⚠️ Opera

### Requirements:
- **HTTPS required in production** (works on localhost for development)
- Microphone permission (browser will prompt on first use)

## Use Cases for EI Providers

### During Home Visits:
- Hands-free documentation while interacting with children
- Quick voice notes during observations
- Listen to guidance while demonstrating activities

### On-the-Go:
- Voice input while driving between appointments
- Quick consultation without typing
- Accessibility for providers with motor difficulties

### Multilingual Support:
- Currently optimized for English (en-US)
- Can be configured for other languages if needed

## Privacy & Security

- All voice processing happens **locally in your browser**
- No audio is sent to external services
- No voice data is stored
- Web Speech API uses browser's built-in capabilities

## Troubleshooting

### Microphone Not Working:
1. Check browser permissions (click lock icon in address bar)
2. Ensure microphone is not being used by another app
3. Try refreshing the page
4. Use Chrome/Edge for best compatibility

### Speech Not Being Read Aloud:
1. Check system volume
2. Toggle speaker icon off and on again
3. Try a different browser if issues persist

### Poor Recognition Accuracy:
1. Speak clearly and at normal pace
2. Reduce background noise
3. Use a better microphone if available
4. Speak in shorter sentences

## Technical Notes

- Uses Web Speech API (SpeechRecognition & SpeechSynthesis)
- No additional dependencies required
- Gracefully degrades if browser doesn't support it
- Voice controls will be hidden if not supported

## Future Enhancements

Potential improvements:
- Multi-language support
- Custom voice selection for TTS
- Adjustable speech rate
- Voice command shortcuts (e.g., "Generate plan")
- Offline voice recognition (browser-dependent)
