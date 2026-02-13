import React, { useState } from 'react';
import {
  Box,
  Button,
  List,
  ListItemButton,
  ListItemText,
  Typography,
  IconButton,
  TextField,
  Menu,
  MenuItem,
} from '@mui/material';
import {
  Add,
  MoreVert,
  Edit,
  Delete,
  Check,
  Close,
} from '@mui/icons-material';

/**
 * Sidebar Component
 * Shows flat list of chats
 */
function Sidebar({
  chats,
  activeChatId,
  onNewChat,
  onSelectChat,
  onRenameChat,
  onDeleteChat,
}) {
  const [editingChatId, setEditingChatId] = useState(null);
  const [editValue, setEditValue] = useState('');
  const [menuAnchor, setMenuAnchor] = useState(null);
  const [menuTarget, setMenuTarget] = useState(null);

  // Open context menu
  const handleMenuOpen = (event, target) => {
    event.stopPropagation();
    setMenuAnchor(event.currentTarget);
    setMenuTarget(target);
  };

  const handleMenuClose = () => {
    setMenuAnchor(null);
    setMenuTarget(null);
  };

  // Start editing
  const startEditChat = (chat) => {
    setEditingChatId(chat.id);
    setEditValue(chat.title);
    handleMenuClose();
  };

  // Save edit
  const saveEditChat = () => {
    if (editValue.trim() && editingChatId) {
      onRenameChat(editingChatId, editValue.trim());
    }
    setEditingChatId(null);
    setEditValue('');
  };

  // Cancel edit
  const cancelEdit = () => {
    setEditingChatId(null);
    setEditValue('');
  };

  // Delete handler
  const handleDeleteChat = () => {
    if (menuTarget && window.confirm('Delete this chat and all its conversations?')) {
      onDeleteChat(menuTarget.id);
    }
    handleMenuClose();
  };

  return (
    <Box
      sx={{
        width: 280,
        borderRight: 1,
        borderColor: 'divider',
        display: 'flex',
        flexDirection: 'column',
        bgcolor: 'background.paper',
        height: '100vh',
      }}
    >
      {/* Header */}
      <Box
        sx={{
          p: 2,
          borderBottom: 1,
          borderColor: 'divider',
          display: 'flex',
          flexDirection: 'column',
          gap: 1.5,
        }}
      >
        <Typography variant="h6" sx={{ fontWeight: 700, fontSize: '1.1rem' }}>
          Early Intervention AI
        </Typography>
        <Button
          variant="outlined"
          startIcon={<Add />}
          onClick={onNewChat}
          fullWidth
          sx={{
            textTransform: 'none',
            borderRadius: 2,
            py: 1,
            fontWeight: 500,
            borderColor: 'divider',
            color: 'text.primary',
            '&:hover': {
              borderColor: 'text.secondary',
              bgcolor: 'action.hover',
            },
          }}
        >
          New chat
        </Button>
      </Box>

      {/* Chat History */}
      <Box sx={{ flex: 1, overflow: 'auto', p: 1.5 }}>
        <Typography
          variant="caption"
          sx={{
            px: 1,
            py: 1,
            color: 'text.secondary',
            textTransform: 'uppercase',
            fontWeight: 600,
            fontSize: '0.7rem',
            letterSpacing: '0.5px',
          }}
        >
          Recent
        </Typography>

        <List dense sx={{ pt: 0.5 }}>
          {chats && chats.map((chat) => (
            <ListItemButton
              key={chat.id}
              selected={chat.id === activeChatId}
              onClick={() => onSelectChat(chat.id)}
              sx={{
                borderRadius: 2,
                mb: 0.5,
                px: 1.5,
                py: 1,
                display: 'flex',
                alignItems: 'center',
                gap: 1,
                transition: 'all 0.2s ease',
                '&:hover': {
                  bgcolor: 'action.hover',
                },
                '&.Mui-selected': {
                  bgcolor: 'action.selected',
                  '&:hover': {
                    bgcolor: 'action.selected',
                  },
                },
              }}
            >
              {/* Title or Edit Field */}
              {editingChatId === chat.id ? (
                <Box sx={{ flex: 1, display: 'flex', gap: 0.5 }} onClick={(e) => e.stopPropagation()}>
                  <TextField
                    size="small"
                    value={editValue}
                    onChange={(e) => setEditValue(e.target.value)}
                    onKeyPress={(e) => {
                      if (e.key === 'Enter') saveEditChat();
                      if (e.key === 'Escape') cancelEdit();
                    }}
                    autoFocus
                    sx={{ flex: 1 }}
                  />
                  <IconButton size="small" onClick={saveEditChat}>
                    <Check fontSize="small" />
                  </IconButton>
                  <IconButton size="small" onClick={cancelEdit}>
                    <Close fontSize="small" />
                  </IconButton>
                </Box>
              ) : (
                <>
                  <ListItemText
                    primary={chat.title}
                    primaryTypographyProps={{
                      noWrap: true,
                      fontSize: '0.875rem',
                      fontWeight: 500,
                    }}
                    sx={{ flex: 1 }}
                  />
                  <IconButton
                    size="small"
                    onClick={(e) => handleMenuOpen(e, { id: chat.id, data: chat })}
                    sx={{
                      opacity: 0.7,
                      transition: 'opacity 0.2s',
                      '&:hover': {
                        opacity: 1,
                        bgcolor: 'action.hover',
                      },
                    }}
                  >
                    <MoreVert fontSize="small" />
                  </IconButton>
                </>
              )}
            </ListItemButton>
          ))}
        </List>
      </Box>

      {/* Context Menu */}
      <Menu anchorEl={menuAnchor} open={Boolean(menuAnchor)} onClose={handleMenuClose}>
        <MenuItem onClick={() => startEditChat(menuTarget?.data)}>
          <Edit fontSize="small" sx={{ mr: 1 }} />
          Rename
        </MenuItem>
        <MenuItem onClick={handleDeleteChat} sx={{ color: 'error.main' }}>
          <Delete fontSize="small" sx={{ mr: 1 }} />
          Delete
        </MenuItem>
      </Menu>
    </Box>
  );
}

export default Sidebar;
