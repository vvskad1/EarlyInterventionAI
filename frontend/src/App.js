import React, { useState, useEffect, useMemo } from 'react';
import { Box, ThemeProvider, CssBaseline, Snackbar, Alert, IconButton, Typography } from '@mui/material';
import { Brightness4, Brightness7, Menu } from '@mui/icons-material';
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
 * Data Structure:
 * chats = [
 *   {
 *     id: 'uuid',
 *     title: 'New Chat',
 *     age_months: null,
 *     domains: [],
 *     notes: '',
 *     plan: {...},
 *     messages: [{role, content}]
 *   }
 * ]
 */

function App() {
  // State Management
  const [chats, setChats] = useState([]);
  const [activeChatId, setActiveChatId] = useState(null);
  const [chatMessage, setChatMessage] = useState('');
  const [isGenerating, setIsGenerating] = useState(false);
  const [isSending, setIsSending] = useState(false);
  const [themeMode, setThemeMode] = useState('dark');
  const [sidebarOpen, setSidebarOpen] = useState(true);
  const [snackbar, setSnackbar] = useState({ open: false, message: '', severity: 'info' });

  // Create theme based on mode
  const theme = useMemo(() => createAppTheme(themeMode), [themeMode]);

  // Load chats and theme from localStorage on mount
  useEffect(() => {
    // Load theme
    const storedTheme = localStorage.getItem(THEME_KEY);
    if (storedTheme) {
      setThemeMode(storedTheme);
    }

    // Load chats
    const stored = localStorage.getItem(STORAGE_KEY);
    if (stored) {
      try {
        const parsed = JSON.parse(stored);
        
        // Migrate old data structure: convert domain (string) to domains (array)
        const migratedChats = parsed.map(chat => {
          if (chat.domain && !chat.domains) {
            // Old format: has domain but not domains
            return {
              ...chat,
              domains: [chat.domain],
              notes: chat.notes || '',
            };
          }
          // Ensure domains and notes exist
          return {
            ...chat,
            domains: chat.domains || [],
            notes: chat.notes || '',
          };
        });
        
        setChats(migratedChats);
        // Set first chat as active
        if (migratedChats.length > 0) {
          setActiveChatId(migratedChats[0].id);
        }
      } catch (e) {
        console.error('Failed to parse chats:', e);
      }
    }
    // Create initial chat if none exist
    if (!stored || stored === '[]') {
      // Will be created by following useEffect
    }
  }, []);

  // Create initial chat if none exist (after mount)
  useEffect(() => {
    if (chats.length === 0) {
      createNewChat();
    }
  }, [chats.length]);

  // Save chats to localStorage whenever they change
  useEffect(() => {
    if (chats.length > 0) {
      localStorage.setItem(STORAGE_KEY, JSON.stringify(chats));
    }
  }, [chats]);

  // Get active chat
  const activeChat = chats.find((c) => c.id === activeChatId);

  // Theme toggle
  const toggleTheme = () => {
    const newMode = themeMode === 'dark' ? 'light' : 'dark';
    setThemeMode(newMode);
    localStorage.setItem(THEME_KEY, newMode);
  };

  // Sidebar toggle
  const toggleSidebar = () => {
    setSidebarOpen(!sidebarOpen);
  };

  // Create new chat
  const createNewChat = () => {
    const newChat = {
      id: generateUUID(),
      title: 'New Chat',
      createdAt: Date.now(),
      age_months: null,
      domains: [],
      notes: '',
      plan: null,
      messages: [],
    };
    
    setChats((prev) => {
      const updated = [newChat, ...prev];
      return updated.slice(0, MAX_CHATS);
    });
    setActiveChatId(newChat.id);
    setChatMessage('');
  };

  // Select chat
  const selectChat = (chatId) => {
    setActiveChatId(chatId);
    setChatMessage('');
  };

  // Rename chat
  const renameChat = (chatId, newTitle) => {
    setChats((prev) =>
      prev.map((chat) => (chat.id === chatId ? { ...chat, title: newTitle } : chat))
    );
  };

  // Delete chat
  const deleteChat = (chatId) => {
    setChats((prev) => {
      const filtered = prev.filter((c) => c.id !== chatId);
      // If we deleted the active chat, select another
      if (chatId === activeChatId) {
        if (filtered.length > 0) {
          setActiveChatId(filtered[0].id);
        } else {
          setActiveChatId(null);
        }
      }
      return filtered;
    });
  };

  // Update active chat
  const updateChat = (updates) => {
    setChats((prev) =>
      prev.map((chat) =>
        chat.id === activeChatId ? { ...chat, ...updates } : chat
      )
    );
  };

  // Generate plan handler
  const handleGenerate = async () => {
    // Get current chat
    const chat = activeChat;

    if (!chat) {
      showSnackbar('No active chat', 'warning');
      return;
    }

    console.log('Current chat:', chat);
    console.log('Domains:', chat.domains, 'Type:', typeof chat.domains, 'IsArray:', Array.isArray(chat.domains));
    
    if (!chat.age_months || !chat.domains || chat.domains.length === 0) {
      showSnackbar('Please select age and at least one area of concern', 'warning');
      return;
    }

    setIsGenerating(true);

    try {
      // Ensure domains is an array and has values
      const domainsArray = Array.isArray(chat.domains) ? chat.domains : [];
      
      if (domainsArray.length === 0) {
        showSnackbar('Please select at least one area of concern', 'warning');
        setIsGenerating(false);
        return;
      }
      
      const payload = {
        age_months: chat.age_months,
        domains: domainsArray,
        notes: chat.notes || null,
      };
      console.log('Sending plan request:', payload);
      
      const result = await generatePlan(payload);

      // Format the plan as a message
      const formattedMessage = `**🎯 Goals**\n\n${result.Goals}\n\n---\n\n**⚡ Strategies**\n\n${result.Strategies}\n\n---\n\n**💡 Advice for Parents**\n\n${result['Advice for Parents'] || result.Advice_for_Parents}`;

      // Add the plan as an AI message
      const updatedMessages = [
        ...chat.messages,
        {
          role: 'assistant',
          content: formattedMessage,
        },
      ];

      // Update chat with messages and title
      const domainsText = chat.domains.map(d => d.replace('_', ' ').replace(/\b\w/g, (l) => l.toUpperCase())).join(', ');
      const title = `${chat.age_months} month old – ${domainsText}`;

      updateChat({
        plan: result,
        title: title,
        messages: updatedMessages,
      });

      showSnackbar('Plan generated successfully', 'success');
    } catch (error) {
      showSnackbar(error.message, 'error');
    } finally {
      setIsGenerating(false);
    }
  };

  // Send chat message handler
  const handleSendMessage = async () => {
    if (!chatMessage.trim() || !activeChatId) return;

    const chat = activeChat;
    if (!chat) return;

    const userMessage = chatMessage.trim();
    setChatMessage('');

    // Add user message immediately
    const updatedMessages = [...chat.messages, { role: 'user', content: userMessage }];
    updateChat({ messages: updatedMessages });

    setIsSending(true);

    try {
      const result = await sendChat(userMessage, chat.id, {
        age_months: chat.age_months,
        domains: chat.domains,
        notes: chat.notes,
      });

      // Add AI response
      updateChat({
        messages: [...updatedMessages, { role: 'assistant', content: result.response }],
      });
    } catch (error) {
      showSnackbar(error.message, 'error');
      // Restore original messages on error
      updateChat({ messages: chat.messages });
      setChatMessage(userMessage);
    } finally {
      setIsSending(false);
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
      <Box sx={{ display: 'flex', height: '100vh', overflow: 'hidden' }}>
        {/* Theme Toggle - Top Right */}
        {/* Left Sidebar */}
        {sidebarOpen && (
          <Sidebar
            chats={chats}
            activeChatId={activeChatId}
            onNewChat={createNewChat}
            onSelectChat={selectChat}
            onRenameChat={renameChat}
            onDeleteChat={deleteChat}
          />
        )}

        {/* Right Pane */}
        {activeChat ? (
          <RightPane
            chatTitle={activeChat.title}
            ageMonths={activeChat.age_months}
            domains={activeChat.domains}
            notes={activeChat.notes}
            plan={activeChat.plan}
            messages={activeChat.messages}
            chatMessage={chatMessage}
            isGenerating={isGenerating}
            isSending={isSending}
            sidebarOpen={sidebarOpen}
            themeMode={themeMode}
            onToggleSidebar={toggleSidebar}
            onToggleTheme={toggleTheme}
            onAgeChange={(value) => updateChat({ age_months: value !== '' ? parseInt(value) : null })}
            onDomainsChange={(values) => updateChat({ domains: values })}
            onNotesChange={(value) => updateChat({ notes: value })}
            onGenerate={handleGenerate}
            onChatMessageChange={setChatMessage}
            onSendMessage={handleSendMessage}
          />
        ) : (
          <Box
            sx={{
              flex: 1,
              display: 'flex',
              flexDirection: 'column',
              overflow: 'hidden',
            }}
          >
            {/* Header Bar for Empty State */}
            <Box
              sx={{
                display: 'flex',
                alignItems: 'center',
                gap: 2,
                px: 2,
                py: 1.5,
                borderBottom: '1px solid',
                borderColor: 'divider',
                bgcolor: 'background.paper',
              }}
            >
              <IconButton
                onClick={toggleSidebar}
                size="small"
                sx={{
                  color: 'text.secondary',
                  '&:hover': {
                    bgcolor: 'action.hover',
                  },
                }}
              >
                <Menu />
              </IconButton>
              <Typography
                variant="body1"
                sx={{
                  flex: 1,
                  fontWeight: 600,
                  color: 'text.primary',
                }}
              >
                Early Intervention AI
              </Typography>
              <IconButton
                onClick={toggleTheme}
                size="small"
                sx={{
                  color: 'text.secondary',
                  '&:hover': {
                    bgcolor: 'action.hover',
                  },
                }}
              >
                {themeMode === 'dark' ? <Brightness7 fontSize="small" /> : <Brightness4 fontSize="small" />}
              </IconButton>
            </Box>
            
            {/* Empty State Content */}
            <Box
              sx={{
                flex: 1,
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                p: 4,
              }}
            >
              <Box sx={{ textAlign: 'center', maxWidth: 400 }}>
                <Typography variant="h5" gutterBottom>
                  Welcome to Early Intervention AI
                </Typography>
                <Typography variant="body1" color="text.secondary">
                  Create a new chat or select an existing one to get started
                </Typography>
              </Box>
            </Box>
          </Box>
        )}

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
