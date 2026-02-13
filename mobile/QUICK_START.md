# Quick Start Guide

## Prerequisites Check

Before starting, ensure you have:
- ✅ Node.js 18+ installed
- ✅ Android Studio installed
- ✅ ANDROID_HOME environment variable set
- ✅ Backend server accessible

## Fast Setup (5 minutes)

### 1. Navigate to mobile directory
```bash
cd mobile
```

### 2. Install dependencies
```bash
npm install
```

### 3. Update API URL

Edit `src/config/api.js` and set your backend URL:

- **For Android Emulator**: `http://10.0.2.2:8081`
- **For Physical Device**: `http://YOUR_COMPUTER_IP:8081`

To find your IP:
```bash
ipconfig  # Windows
# Look for IPv4 Address
```

### 4. Start Development

```bash
# Terminal 1: Start Metro bundler
npm start

# Terminal 2: Run on Android
npm run android
```

### 5. Build APK (Optional)

**Quick Debug APK:**
```bash
cd android
./gradlew assembleDebug
# APK: android/app/build/outputs/apk/debug/app-debug.apk
```

**Release APK (requires keystore):**
```bash
cd android
./gradlew assembleRelease
# APK: android/app/build/outputs/apk/release/app-release.apk
```

## Common Issues

### "SDK location not found"
```bash
# Create local.properties file in android folder
echo sdk.dir=C:\\Users\\YourUsername\\AppData\\Local\\Android\\Sdk > android/local.properties
```

### "Metro Bundler won't start"
```bash
npx react-native start --reset-cache
```

### "App won't connect to backend"
- ✅ Backend is running on port 8081
- ✅ Using correct IP (not localhost)
- ✅ Firewall allows connections
- ✅ Test: Open `http://YOUR_IP:8081/health` in phone browser

### "Voice not working"
- ✅ Grant microphone permission in app settings
- ✅ Test on physical device (emulator voice may fail)

## What's Next?

1. **Test the app** - Generate a plan, use voice features
2. **Deploy backend** - Use Render, Railway, or AWS
3. **Build release APK** - Follow SETUP_AND_BUILD.md
4. **Distribute** - Share APK or publish to Play Store

## Need Full Instructions?

See `SETUP_AND_BUILD.md` for complete setup and build guide.
