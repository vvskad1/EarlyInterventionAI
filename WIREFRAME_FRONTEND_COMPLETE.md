# Wireframe Frontend - Complete ✅

## Implementation Summary

The wireframe-specific frontend is now fully implemented with:

### Architecture
- **Dark Monochrome Theme**: `#0F1115` background, `#12141A` paper surfaces
- **280px Fixed Sidebar**: Radio-style chat history selection
- **Session-Based State**: localStorage persistence (max 25 sessions)
- **UUID Session IDs**: Proper session tracking with backend

### Components Created
1. ✅ **theme.js** - Dark mode MUI theme with outlined variants
2. ✅ **Sidebar.js** - 280px left column with "New chat" button + radio list
3. ✅ **RightPane.js** - Age/Domain controls, Generate button, three plan cards, chat area with PlayArrow send button
4. ✅ **App.js** - Session management, localStorage hooks, unified state

### Key Features
- Session titles: `"{age} month old – {domain}"`
- Radio selection for chat history (one active at a time)
- Sticky bottom chat input with PlayArrowOutlined triangle icon
- Three plan sections: Goals, Strategies, Advice for Parents
- Auto-scroll chat messages
- Snackbar notifications for errors

## Testing Instructions

### 1. Start Backend (Port 8080)
```powershell
cd "c:\Users\STSC\Desktop\Therapy AI\v1_code"
.venv\Scripts\activate
$env:PORT="8080"; uvicorn app.main:app --reload --port 8080
```

**Note**: The wireframe frontend expects backend on port **8080** (not 8081).

### 2. Start Frontend
```powershell
cd "c:\Users\STSC\Desktop\Therapy AI\v1_code\frontend"
npm start
```

Opens at `http://localhost:3000`

### 3. Test Flow
1. ✅ Click "New chat" - creates new session
2. ✅ Select Age (0-36 months) from dropdown
3. ✅ Select Domain from dropdown (6 options)
4. ✅ Click "Generate" (240px width button)
5. ✅ Verify three outlined cards appear: Goals, Strategies, Advice
6. ✅ Type message in bottom input field
7. ✅ Click PlayArrow triangle button to send
8. ✅ Verify chat bubbles (user right-aligned, AI left-aligned)
9. ✅ Click "New chat" again - creates second session
10. ✅ Use radio buttons in sidebar to switch between sessions
11. ✅ Refresh page - sessions should persist from localStorage

### 4. Visual Verification
- [ ] Dark background (`#0F1115`)
- [ ] Sidebar exactly 280px width
- [ ] All components use outlined variant (not filled)
- [ ] Radio circles in chat history (not checkboxes)
- [ ] PlayArrow triangle icon for send (not paper plane)
- [ ] Chat history truncates long titles with ellipsis
- [ ] Bottom input is sticky (doesn't scroll with chat)
- [ ] Session titles show age + domain

## File Structure
```
frontend/src/
├── App.js                    # Main app, session management (223 lines)
├── theme.js                  # Dark monochrome MUI theme
├── api.js                    # API helpers (port 8080)
├── components/
│   ├── Sidebar.js            # 280px left column
│   └── RightPane.js          # Main content area
├── index.js
└── index.css
```

## Backend Compatibility
- Endpoint: `POST http://localhost:8080/api/plan`
- Endpoint: `POST http://localhost:8080/api/chat`
- Backend uses `session_id` for chat continuity
- Frontend generates UUID, backend maintains in-memory store

## localStorage Schema
```json
{
  "ei_sessions": [
    {
      "id": "uuid-v4-string",
      "title": "12 month old – Language",
      "age_months": 12,
      "domain": "language",
      "plan": {
        "Goals": "...",
        "Strategies": "...",
        "Advice for Parents": "..."
      },
      "messages": [
        {"role": "user", "content": "..."},
        {"role": "assistant", "content": "..."}
      ]
    }
  ]
}
```

## Differences from Gradient Frontend (v1)
| Feature | Gradient Design | Wireframe Design |
|---------|----------------|------------------|
| Theme | Light + purple-violet gradient | Dark monochrome (#0F1115) |
| Layout | Vertical single page, 3 sections | Horizontal 2-column (280px + flex) |
| Chat History | None (single session) | Radio list, up to 25 sessions |
| Components | Filled buttons/cards | Outlined buttons/cards |
| Send Icon | Paper plane (Send) | Triangle (PlayArrowOutlined) |
| Knowledge Upload | Separate card | Removed (not in wireframe) |
| Persistence | None | localStorage for all sessions |
| Port | 8081 | 8080 |

## Next Steps (Optional Enhancements)
- [ ] Add session delete button (trash icon per session)
- [ ] Add session rename functionality
- [ ] Add export chat as PDF/markdown
- [ ] Add keyboard shortcuts (Ctrl+N for new chat)
- [ ] Add dark/light mode toggle
- [ ] Add session search/filter
- [ ] Add loading skeleton for plan cards
- [ ] Add markdown rendering in chat messages

---
**Status**: Frontend fully functional and ready for demo ✅
**Last Updated**: Current session
