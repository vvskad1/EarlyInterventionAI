# 🚀 Quick Setup Guide - EI GenAI Studio Frontend

## Step 1: Install Dependencies

```powershell
cd frontend
npm install
```

This will install:
- React 18
- Material-UI (MUI) v5
- Emotion (styling engine for MUI)
- MUI Icons

## Step 2: Start Backend Server

Make sure your FastAPI backend is running:

```powershell
# From the v1_code directory
cd "C:\Users\STSC\Desktop\Therapy AI\v1_code"
.venv\Scripts\activate
uvicorn app.main:app --reload --port 8081
```

✅ Backend should be running at: **http://localhost:8081**

## Step 3: Start Frontend

In a new terminal:

```powershell
cd "C:\Users\STSC\Desktop\Therapy AI\v1_code\frontend"
npm start
```

✅ Frontend will open at: **http://localhost:3000**

## 🎨 What You'll See

### Header
- Purple gradient with "EI GenAI Studio" title
- Blue accent bar
- Clean, modern design

### Left Column (Desktop)
1. **Knowledge Base Upload Card**
   - Upload .txt or .md files
   - Real-time upload feedback

2. **Intervention Plan Generator**
   - Age input (0-36 months)
   - Domain dropdown (6 options)
   - Extra info text area
   - Generate button with gradient
   - Beautiful result cards with:
     - 🎯 Goals (blue background)
     - ⚡ Strategies (orange background)
     - 💡 Advice for Parents (green background)

### Right Column (Desktop)
**AI Chat Assistant**
- Optional age/domain context fields
- Scrollable chat history
- User messages: Purple bubbles on right
- AI messages: White bubbles on left
- Session persistence (localStorage)
- Reset button to start new conversation

### Mobile View
- Stacks vertically
- Upload → Plan → Chat
- Fully responsive and touch-friendly

## 🧪 Testing the App

### Test 1: Upload Knowledge Base
1. Click "Choose File"
2. Select the `kb/knowledge_base.txt` from backend
3. See success message

### Test 2: Generate Plan
1. Age: `24`
2. Domain: `Communication`
3. Extra info: `struggles with two-word combinations`
4. Click "Generate Plan"
5. Wait 3-5 seconds
6. See structured results

### Test 3: Chat
1. (Optional) Set Age: `18`, Domain: `Communication`
2. Type: `How can I help my child follow directions?`
3. Press Enter or click Send
4. See AI response with FGRBI manual references
5. Type follow-up: `What about during mealtime?`
6. See contextual response

## 🎯 Key Features

✅ **Real-time validation** - Form fields validate before submission  
✅ **Loading states** - Spinners show during API calls  
✅ **Error handling** - Snackbar alerts for errors  
✅ **Session memory** - Chat persists across page refreshes  
✅ **Responsive design** - Works on all screen sizes  
✅ **Smooth animations** - Fade-in effects for better UX  
✅ **Auto-scroll** - Chat scrolls to latest message  

## 🔧 Customization

### Change Colors
Edit gradient in `src/App.js`:

```javascript
// Header gradient
background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)'

// Accent bar
background: 'linear-gradient(90deg, #4facfe 0%, #00f2fe 100%)'
```

### Change API URL
Edit `src/api.js`:

```javascript
const API_BASE_URL = 'http://localhost:8081';
```

### Modify Domains
Edit domains array in `src/App.js`:

```javascript
const domains = [
  'communication',
  'social',
  'fine_motor',
  'gross_motor',
  'cognitive',
  'adaptive',
];
```

## 📱 Screenshots Features

- **Rounded cards** with soft shadows (elevation: 2)
- **Gradient buttons** with hover effects
- **Color-coded results** (Goals: blue, Strategies: orange, Advice: green)
- **Chat bubbles** with smooth animations
- **Custom scrollbar** styling
- **Inter font** from Google Fonts

## 🐛 Troubleshooting

**Problem: npm install fails**
```powershell
# Clear cache and retry
npm cache clean --force
npm install
```

**Problem: Port 3000 already in use**
```powershell
# Use different port
set PORT=3001 && npm start
```

**Problem: CORS errors**
- Backend CORS is already enabled for all origins
- Make sure backend is running first

**Problem: API calls fail**
- Check backend console for errors
- Verify backend is on port 8081
- Check browser console (F12) for details

## 🎬 Demo Flow

1. **Start both servers** (backend on 8081, frontend on 3000)
2. **Upload KB** - Show file upload working
3. **Generate Plan** - Demo with 24-month communication example
4. **Show Results** - Highlight the three color-coded cards
5. **Start Chat** - Ask about following directions
6. **Continue Chat** - Ask follow-up about mealtime
7. **Show Session** - Refresh page, chat history persists

## 📦 Production Build

```powershell
npm run build
```

Creates optimized build in `build/` folder ready for deployment.

## 🎉 You're Done!

Your EI GenAI Studio is ready to use!

- Beautiful Material-UI interface ✅
- Connected to FastAPI backend ✅
- RAG-powered responses ✅
- Session memory ✅
- Fully responsive ✅

Enjoy! 🚀
