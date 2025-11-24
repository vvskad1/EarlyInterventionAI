# EI GenAI Studio - React Frontend

Beautiful, responsive React frontend for the Early Intervention GenAI API.

## Features

✨ **Elegant Material-UI Design** - Modern, professional interface with gradient accents  
📤 **Knowledge Base Upload** - Upload .txt/.md files to enhance AI responses  
🎯 **Intervention Plan Generator** - Create personalized plans with structured output  
💬 **AI Chat Assistant** - Conversational interface with session memory  
📱 **Fully Responsive** - Beautiful on desktop, tablet, and mobile  
🎨 **Calming Color Palette** - Blue-violet gradients with soft shadows  

## Quick Start

### Prerequisites
- Node.js 16+ installed
- Backend server running on `http://localhost:8081`

### Installation

```bash
cd frontend
npm install
npm start
```

The app will open at **http://localhost:3000**

## Project Structure

```
frontend/
├── public/
│   └── index.html          # HTML template
├── src/
│   ├── App.js              # Main application component
│   ├── api.js              # API helper functions
│   ├── index.js            # React entry point
│   └── index.css           # Global styles
├── package.json
└── README.md
```

## Usage

### 1. Upload Knowledge Base
- Click "Choose File" in the Knowledge Base Upload card
- Select a `.txt` or `.md` file
- File is automatically uploaded to the backend

### 2. Generate Intervention Plan
- Enter child's age (0-36 months)
- Select development domain
- Optionally add additional context
- Click "Generate Plan"
- View structured results with Goals, Strategies, and Advice

### 3. Chat with AI Assistant
- Optionally set age and domain for context-aware responses
- Type your question in the chat input
- Press Enter or click Send
- Conversation history is maintained with session memory
- Click refresh icon to start a new session

## API Integration

The frontend connects to these backend endpoints:

- `POST /api/rag/upload` - Upload knowledge base file
- `POST /api/plan` - Generate intervention plan
- `POST /api/chat` - Send chat message

All API calls are handled through `src/api.js` helper functions.

## Configuration

To change the backend API URL, edit `API_BASE_URL` in `src/api.js`:

```javascript
const API_BASE_URL = 'http://localhost:8081';
```

## Design System

### Color Palette
- **Primary Gradient**: `#667eea` → `#764ba2`
- **Accent Gradient**: `#4facfe` → `#00f2fe`
- **Background**: `#f5f7fa`
- **Card Background**: `#ffffff`
- **Text Primary**: Default MUI text colors
- **Text Secondary**: Gray tones

### Typography
- **Font Family**: Inter (Google Fonts)
- **Heading Weight**: 600
- **Body Weight**: 400

### Components
- **Border Radius**: 8-12px for cards, 8px for inputs
- **Elevation**: 2 for cards
- **Spacing**: Consistent 8px grid system (MUI default)

## Responsive Breakpoints

- **Desktop**: 2-column layout (Plan + Chat side-by-side)
- **Tablet/Mobile**: Stacked single-column layout

## Browser Support

- Chrome (latest)
- Firefox (latest)
- Safari (latest)
- Edge (latest)

## Build for Production

```bash
npm run build
```

Creates optimized production build in the `build/` folder.

## Deployment

The built app can be deployed to:
- **Vercel**: `vercel deploy`
- **Netlify**: Drag & drop `build/` folder
- **GitHub Pages**: Use `gh-pages` package
- **Any static hosting**: Upload `build/` contents

## Troubleshooting

**CORS errors?**
- Ensure backend has CORS enabled for `http://localhost:3000`
- Check backend is running on port 8081

**API not responding?**
- Verify backend server is running: `uvicorn app.main:app --reload --port 8081`
- Check API_BASE_URL in `src/api.js`

**Styling issues?**
- Clear browser cache
- Delete `node_modules` and run `npm install` again

## License

MIT License - Built for Early Intervention Professionals

## Support

For issues or questions, refer to the main project documentation.
