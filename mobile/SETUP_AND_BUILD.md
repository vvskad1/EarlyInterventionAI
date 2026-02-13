# React Native Mobile App - Setup & Build Guide

## Complete Setup Instructions

### Step 1: Initialize React Native Project

```bash
cd mobile

# Install React Native CLI globally (if not already installed)
npm install -g react-native-cli

# Initialize the React Native app
npx react-native init EarlyInterventionAI --directory .

# Install all dependencies
npm install
```

### Step 2: Android Studio Setup

1. **Install Android Studio**
   - Download from https://developer.android.com/studio
   - Install Android SDK (API Level 33 or higher)
   - Set up ANDROID_HOME environment variable

2. **Configure Environment Variables**
   
   Windows:
   ```
   ANDROID_HOME = C:\Users\YourUsername\AppData\Local\Android\Sdk
   PATH += %ANDROID_HOME%\platform-tools
   PATH += %ANDROID_HOME%\tools
   ```

3. **Accept Android SDK Licenses**
   ```bash
   cd %ANDROID_HOME%/tools/bin
   sdkmanager --licenses
   ```

### Step 3: Configure Android Permissions

The app requires microphone permission. This is already configured in the generated code, but verify:

**android/app/src/main/AndroidManifest.xml**:
```xml
<uses-permission android:name="android.permission.INTERNET" />
<uses-permission android:name="android.permission.RECORD_AUDIO" />
```

### Step 4: Update Backend API URL

Edit `src/config/api.js`:

```javascript
// For Android Emulator (localhost)
export const API_BASE_URL = 'http://10.0.2.2:8081';

// For Physical Device (use your computer's IP)
export const API_BASE_URL = 'http://YOUR_COMPUTER_IP:8081';

// For Production
export const API_BASE_URL = 'https://your-deployed-backend.com';
```

Find your computer's IP:
```bash
# Windows
ipconfig

# Look for "IPv4 Address" under your network adapter
```

### Step 5: Link Native Modules

```bash
# Link vector icons
npx react-native link react-native-vector-icons

# For iOS (macOS only)
cd ios && pod install && cd ..
```

### Step 6: Run the App

**Android:**
```bash
# Start Metro bundler
npm start

# In another terminal, run on Android
npm run android

# Or manually
npx react-native run-android
```

**iOS (macOS only):**
```bash
npm run ios
```

### Step 7: Build APK

#### Debug APK (for testing)

```bash
cd android
./gradlew assembleDebug

# APK location:
# android/app/build/outputs/apk/debug/app-debug.apk
```

#### Release APK (for distribution)

1. **Generate Signing Key:**

```bash
cd android/app
keytool -genkeypair -v -storetype PKCS12 -keystore my-release-key.keystore -alias my-key-alias -keyalg RSA -keysize 2048 -validity 10000

# Remember the password you set!
```

2. **Configure Gradle:**

Create `android/gradle.properties` (add these lines):
```properties
MYAPP_RELEASE_STORE_FILE=my-release-key.keystore
MYAPP_RELEASE_KEY_ALIAS=my-key-alias
MYAPP_RELEASE_STORE_PASSWORD=YOUR_PASSWORD
MYAPP_RELEASE_KEY_PASSWORD=YOUR_PASSWORD
```

3. **Update `android/app/build.gradle`:**

```gradle
android {
    ...
    signingConfigs {
        release {
            if (project.hasProperty('MYAPP_RELEASE_STORE_FILE')) {
                storeFile file(MYAPP_RELEASE_STORE_FILE)
                storePassword MYAPP_RELEASE_STORE_PASSWORD
                keyAlias MYAPP_RELEASE_KEY_ALIAS
                keyPassword MYAPP_RELEASE_KEY_PASSWORD
            }
        }
    }
    buildTypes {
        release {
            ...
            signingConfig signingConfigs.release
        }
    }
}
```

4. **Build Release APK:**

```bash
cd android
./gradlew assembleRelease

# APK location:
# android/app/build/outputs/apk/release/app-release.apk
```

### Step 8: Install APK on Device

```bash
# Via ADB
adb install android/app/build/outputs/apk/release/app-release.apk

# Or transfer the APK file to your device and install manually
```

## Troubleshooting

### Metro Bundler Issues
```bash
# Clear cache
npx react-native start --reset-cache
```

### Build Failures
```bash
# Clean build
cd android
./gradlew clean
cd ..
npm run android
```

### Voice Recognition Not Working
- Ensure microphone permissions are granted in Android settings
- Test on a physical device (emulator voice may not work well)

### Cannot Connect to Backend
- Check firewall settings
- Ensure backend is running: `http://YOUR_IP:8081/health`
- Use `http://10.0.2.2:8081` for Android Emulator
- Use actual IP address for physical devices

## Project Structure

```
mobile/
├── android/              # Android native code
├── ios/                  # iOS native code  
├── src/
│   ├── components/       # Reusable UI components
│   │   ├── ChildProfileForm.js
│   │   ├── ChatMessages.js
│   │   ├── PlanDisplay.js
│   │   └── VoiceControls.js
│   ├── config/           # Configuration
│   │   ├── api.js
│   │   └── theme.js
│   ├── navigation/       # Navigation setup
│   │   └── AppNavigator.js
│   ├── screens/          # Screen components
│   │   ├── ChatListScreen.js
│   │   └── ChatScreen.js
│   ├── services/         # Business logic
│   │   ├── api.js
│   │   ├── storage.js
│   │   └── voice.js
│   └── utils/            # Helper functions
│       └── helpers.js
├── App.js                # Entry point
└── package.json          # Dependencies
```

## Dependencies

Key libraries used:
- `react-native-paper` - Material Design UI components
- `@react-navigation` - Navigation
- `@react-native-voice/voice` - Speech-to-text
- `react-native-tts` - Text-to-speech
- `axios` - API requests
- `@react-native-async-storage` - Local storage

## Next Steps

1. Deploy backend to cloud (Render, Railway, AWS)
2. Update API_BASE_URL to production URL
3. Build release APK
4. Test on multiple devices
5. Submit to Google Play Store (optional)

## Support

For issues or questions about React Native setup:
- React Native Docs: https://reactnative.dev/docs/getting-started
- React Native Paper: https://callstack.github.io/react-native-paper/
