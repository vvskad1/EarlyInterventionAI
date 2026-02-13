import React, { useState, useEffect, useMemo } from 'react';
import { Box, ThemeProvider, CssBaseline, Snackbar, Alert, IconButton, AppBar, Toolbar, Typography } from '@mui/material';
import { Brightness4, Brightness7 } from '@mui/icons-material';
import { createAppTheme } from './theme';
import Sidebar from './components/Sidebar';
import RightPane from './components/RightPane';
import { generatePlan, sendChat } from './api';

// Generate a new UUID v4
function generateUUID() {
  return 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, function (c) {
    const r = (Math.random() * 16) | 0;
    const v = c === 'x' ? r : (r & 0x3) | 0x8;
    return v.toString(16);
  });
}

// LocalStorage keys
const STORAGE_KEY = 'ei_chats';
const THEME_KEY = 'ei_theme_mode';
const MAX_CHATS = 25;

/**
 * New data structure:
 * Chat {
 *   id: string,
 *   title: string,
 *   conversations: [
 *     {
 *       id: string,
 *       age_months: number,
 *       domain: string,
 *       plan: { Goals, Strategies, "Advice for Parents" },
 *       messages: [{role, content}]
 *     }
 *   ]
 * }
 */

function App() {
  // State Management
  const [chats, setChats] = useState([]);
  const [activeChatId, setActiveChatId] = useState(null);
  const [activeConversationId, setActiveConversationId] = useState(null);
  const [chatMessage, setChatMessage] = useState('');
  const [isGenerating, setIsGenerating] = useState(false);
  const [isSending, setIsSending] = useState(false);
  const [themeMode, setThemeMode] = useState('dark');
  const [snackbar, setSnackbar] = useState({ open: false, message: '', severity: 'info' });

  // Create theme based on mode
  const theme = useMemo(() => createAppTheme(themeMode), [themeMode]);

  // Load theme preference on mount
  useEffect(() => {
    const savedTheme = localStorage.getItem(THEME_KEY);
    if (savedTheme) {
      setThemeMode(savedTheme);
    }
  }, []);

  // Load chats from localStorage on mount
  useEffect(() => {
    const stored = localStorage.getItem(STORAGE_KEY);
    if (stored) {
      try {
        const parsed = JSON.parse(stored);
        setChats(parsed);
        if (parsed.length > 0) {
          setActiveChatId(parsed[0].id);
          if (parsed[0].conversations && parsed[0].conversations.length > 0) {
            setActiveConversationId(parsed[0].conversations[0].id);
          }
        }
      } catch (e) {
        console.error('Failed to parse chats:', e);
        createNewChat();
      }
    } else {
      createNewChat();
    }
  }, []);

  // Save chats to localStorage whenever they change
  useEffect(() => {
    if (chats.length > 0) {
      localStorage.setItem(STORAGE_KEY, JSON.stringify(chats));
    }
  }, [chats]);

  // Get active chat and conversation
  const activeChat = chats.find((c) => c.id === activeChatId);
  const activeConversation = activeChat?.conversations?.find((conv) => conv.id === activeConversationId);

  // Toggle theme mode
  const toggleTheme = () => {
    const newMode = themeMode === 'dark' ? 'light' : 'dark';
    setThemeMode(newMode);
    localStorage.setItem(THEME_KEY, newMode);
  };

  // Create new chat
  const createNewChat = () => {
    const newChat = {
      id: generateUUID(),
      title: 'New chat',
      conversations: [],
    };
    setChats((prev) => {
      const updated = [newChat, ...prev];
      return updated.slice(0, MAX_CHATS);
    });
    setActiveChatId(newChat.id);
    setActiveConversationId(null);
    setChatMessage('');
  };

  // Select chat
  const selectChat = (chatId) => {
    setActiveChatId(chatId);
    const chat = chats.find((c) => c.id === chatId);
    if (chat && chat.conversations && chat.conversations.length > 0) {
      setActiveConversationId(chat.conversations[0].id);
    } else {
      setActiveConversationId(null);
    }
    setChatMessage('');
  };

  // Rename chat
  const renameChat = (chatId, newTitle) => {
    setChats((prev) =>
      prev.map((c) => (c.id === chatId ? { ...c, title: newTitle } : c))
    );
  };

  // Delete chat
  const deleteChat = (chatId) => {
    setChats((prev) => {
      const updated = prev.filter((c) => c.id !== chatId);
      // If deleting active chat, select first remaining
      if (chatId === activeChatId && updated.length > 0) {
        setActiveChatId(updated[0].id);
        if (updated[0].conversations && updated[0].conversations.length > 0) {
          setActiveConversationId(updated[0].conversations[0].id);
        } else {
          setActiveConversationId(null);
        }
      }
      return updated;
    });
  };

  // Update active chat
  const updateChat = (updates) => {
    setChats((prev) =>
      prev.map((c) => (c.id === activeChatId ? { ...c, ...updates } : c))
    );
  };

  // Update active conversation
  const updateConversation = (updates) => {
    setChats((prev) =>
      prev.map((c) =>
        c.id === activeChatId
          ? {
              ...c,
              conversations: c.conversations.map((conv) =>
                conv.id === activeConversationId ? { ...conv, ...updates } : conv
              ),
            }
          : c
      )
    );
  };

  // Select conversation (subchat)
  const selectConversation = (conversationId) => {
    setActiveConversationId(conversationId);
    setChatMessage('');
  };

  // Generate plan handler - creates a new conversation
  const handleGenerate = async () => {
    if (!activeChat) {
      showSnackbar('No active chat', 'warning');
      return;
    }

    // Create new conversation with temp values for age/domain selection
    const newConversation = {
      id: generateUUID(),
      age_months: null,
      domain: null,
      plan: null,
      messages: [],
    };

    // Add conversation to active chat
    setChats((prev) =>
      prev.map((c) =>
        c.id === activeChatId
          ? { ...c, conversations: [newConversation, ...(c.conversations || [])] }
          : c
      )
    );
    setActiveConversationId(newConversation.id);
    showSnackbar('New conversation created. Select age and domain to generate plan.', 'info');
  };

  // Actually generate the plan after age/domain are set
  const handleGeneratePlan = async (ageMonths, domain) => {
    if (!ageMonths || !domain) {
      showSnackbar('Please select age and domain', 'warning');
      return;
    }

    setIsGenerating(true);

    try {
      const result = await generatePlan({
        age_months: ageMonths,
        domain: domain,
      });

      // Update conversation with plan
      updateConversation({
        age_months: ageMonths,
        domain: domain,
        plan: result,
      });

      // Update chat title if it's still "New chat"
      if (activeChat.title === 'New chat' || activeChat.title === 'Untitled chat') {
        const title = `${ageMonths} month old – ${domain
          .replace('_', ' ')
          .replace(/\b\w/g, (l) => l.toUpperCase())}`;
        updateChat({ title });
      }

      showSnackbar('Plan generated successfully', 'success');
    } catch (error) {
      showSnackbar(error.message, 'error');
    } finally {
      setIsGenerating(false);
    }
  };

  // Send chat message
  const handleSendMessage = async () => {
    if (!chatMessage.trim() || !activeConversation) {
      return;
    }

    const userMessage = chatMessage.trim();
    setChatMessage('');

    // Add user message immediately
    const updatedMessages = [...(activeConversation.messages || []), { role: 'user', content: userMessage }];
    updateConversation({ messages: updatedMessages });

    setIsSending(true);

    try {
      const result = await sendChat({
        message: userMessage,
        session_id: activeConversation.id,
        age_months: activeConversation.age_months,
        domain: activeConversation.domain,
      });

      // Add AI response
      updateConversation({
        messages: [...updatedMessages, { role: 'assistant', content: result.response }],
      });
    } catch (error) {
      showSnackbar(error.message, 'error');
      // Restore original messages on error
      updateConversation({ messages: activeConversation.messages });
      setChatMessage(userMessage);
    } finally {
      setIsSending(false);
    }
  };

  // Update conversation fields (age/domain)
  const handleUpdateConversation = (field, value) => {
    if (!activeConversation) return;
    
    const updates = { [field]: value };
    updateConversation(updates);

    // Auto-generate plan if both age and domain are set
    if (field === 'age_months' || field === 'domain') {
      const conv = { ...activeConversation, ...updates };
      if (conv.age_months && conv.domain && !conv.plan) {
        handleGeneratePlan(conv.age_months, conv.domain);
      }
    }
  };

  const showSnackbar = (message, severity = 'info') => {
    setSnackbar({ open: true, message, severity });
  };

  const handleCloseSnackbar = () => {
    setSnackbar({ ...snackbar, open: false });
  };

  return (
    <ThemeProvider theme={theme}>
      <CssBaseline />
      <Box sx={{ display: 'flex', flexDirection: 'column', height: '100vh', overflow: 'hidden' }}>
        {/* Top Header */}
        <AppBar position="static" elevation={0} sx={{ bgcolor: 'background.paper', borderBottom: 1, borderColor: 'divider' }}>
          <Toolbar sx={{ minHeight: 56 }}>
            <Typography variant="h6" sx={{ flexGrow: 1, fontWeight: 600, color: 'text.primary' }}>
              Early Intervention AI
            </Typography>
            <IconButton onClick={toggleTheme} color="inherit" sx={{ color: 'text.primary' }}>
              {themeMode === 'dark' ? <Brightness7 /> : <Brightness4 />}
            </IconButton>
          </Toolbar>
        </AppBar>

        {/* Main Content */}
        <Box sx={{ display: 'flex', flex: 1, overflow: 'hidden', p: 2, gap: 2 }}>
          {/* Left Sidebar */}
          <Sidebar
            chats={chats}
            activeChatId={activeChatId}
            activeConversationId={activeConversationId}
            onNewChat={createNewChat}
            onSelectChat={selectChat}
            onSelectConversation={selectConversation}
            onRenameChat={renameChat}
            onDeleteChat={deleteChat}
          />

          {/* Right Pane */}
          {activeChat && activeConversation && (
            <RightPane
              ageMonths={activeConversation.age_months}
              domain={activeConversation.domain}
              plan={activeConversation.plan}
              messages={activeConversation.messages || []}
              chatMessage={chatMessage}
              isGenerating={isGenerating}
              isSending={isSending}
              onAgeChange={(value) => handleUpdateConversation('age_months', value !== '' ? parseInt(value) : null)}
              onDomainChange={(value) => handleUpdateConversation('domain', value !== '' ? value : null)}
              onGenerate={handleGenerate}
              onChatMessageChange={setChatMessage}
              onSendMessage={handleSendMessage}
            />
          )}

          {/* Empty state when no conversation */}
          {activeChat && !activeConversation && (
            <Box
              sx={{
                flex: 1,
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                color: 'text.secondary',
              }}
            >
              <Typography variant="h6">Click "Generate" to create a new conversation</Typography>
            </Box>
          )}
        </Box>

        {/* Snackbar for notifications */}
        <Snackbar
          open={snackbar.open}
          autoHideDuration={4000}
          onClose={handleCloseSnackbar}
          anchorOrigin={{ vertical: 'bottom', horizontal: 'center' }}
        >
          <Alert onClose={handleCloseSnackbar} severity={snackbar.severity} sx={{ width: '100%' }}>
            {snackbar.message}
          </Alert>
        </Snackbar>
      </Box>
    </ThemeProvider>
  );
}

export default App;
