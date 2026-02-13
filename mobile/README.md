# Early Intervention AI - React Native Mobile App

Mobile application for generating early intervention plans for children aged 0-36 months.

## Features

- 🎯 AI-powered intervention plan generation
- 💬 Chat interface for follow-up questions
- 🎤 Voice-to-text input
- 🔊 Text-to-speech responses
- 📱 Native Android/iOS experience
- 💾 Local chat history storage

## Prerequisites

- Node.js >= 18
- React Native development environment
- Android Studio (for Android)
- Xcode (for iOS, macOS only)
- Python backend server running

## Installation

```bash
# Install dependencies
npm install

# iOS specific (macOS only)
cd ios && pod install && cd ..
```

## Configuration

Update the API endpoint in `src/config/api.js`:

```javascript
export const API_BASE_URL = 'http://YOUR_BACKEND_URL:8081';
```

## Running the App

### Android

```bash
npm run android
```

### iOS

```bash
npm run ios
```

## Building APK

### Debug APK

```bash
cd android
./gradlew assembleDebug
# APK location: android/app/build/outputs/apk/debug/app-debug.apk
```

### Release APK

1. Generate keystore:
```bash
keytool -genkeypair -v -storetype PKCS12 -keystore my-release-key.keystore -alias my-key-alias -keyalg RSA -keysize 2048 -validity 10000
```

2. Configure signing in `android/app/build.gradle`

3. Build:
```bash
cd android
./gradlew assembleRelease
# APK location: android/app/build/outputs/apk/release/app-release.apk
```

## Project Structure

```
mobile/
├── src/
│   ├── screens/        # Main app screens
│   ├── components/     # Reusable components
│   ├── services/       # API and business logic
│   ├── navigation/     # Navigation configuration
│   ├── utils/          # Helper functions
│   └── config/         # App configuration
├── android/            # Android native code
├── ios/               # iOS native code
└── App.js             # Entry point
```

## Permissions

The app requires the following permissions:

- `RECORD_AUDIO` - For voice input
- `INTERNET` - For API communication
- `WRITE_EXTERNAL_STORAGE` - For storing chat history (Android < 10)

## License

Proprietary
