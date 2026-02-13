import React, { useState } from 'react';
import {
  Box,
  Button,
  Typography,
  List,
  ListItemButton,
  ListItemText,
  Radio,
  IconButton,
  TextField,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Menu,
  MenuItem,
} from '@mui/material';
import { MoreVert, Edit, Delete, Add } from '@mui/icons-material';

/**
 * Sidebar Component - ChatGPT-like design
 * - New chat button at top
 * - List of chats with expand/collapse for conversations
 * - Rename and delete options
 */
function Sidebar({
  chats,
  activeChatId,
  activeConversationId,
  onNewChat,
  onSelectChat,
  onSelectConversation,
  onRenameChat,
  onDeleteChat,
}) {
  const [renameDialogOpen, setRenameDialogOpen] = useState(false);
  const [renameChatId, setRenameChatId] = useState(null);
  const [renameValue, setRenameValue] = useState('');
  const [menuAnchor, setMenuAnchor] = useState(null);
  const [menuChatId, setMenuChatId] = useState(null);
  const [deleteConfirmOpen, setDeleteConfirmOpen] = useState(false);
  const [deleteChatId, setDeleteChatId] = useState(null);

  const handleMenuOpen = (event, chatId) => {
    event.stopPropagation();
    setMenuAnchor(event.currentTarget);
    setMenuChatId(chatId);
  };

  const handleMenuClose = () => {
    setMenuAnchor(null);
    setMenuChatId(null);
  };

  const handleRenameClick = () => {
    const chat = chats.find((c) => c.id === menuChatId);
    if (chat) {
      setRenameValue(chat.title);
      setRenameChatId(menuChatId);
      setRenameDialogOpen(true);
    }
    handleMenuClose();
  };

  const handleRenameSubmit = () => {
    if (renameValue.trim() && renameChatId) {
      onRenameChat(renameChatId, renameValue.trim());
    }
    setRenameDialogOpen(false);
    setRenameChatId(null);
    setRenameValue('');
  };

  const handleDeleteClick = () => {
    setDeleteChatId(menuChatId);
    setDeleteConfirmOpen(true);
    handleMenuClose();
  };

  const handleDeleteConfirm = () => {
    if (deleteChatId) {
      onDeleteChat(deleteChatId);
    }
    setDeleteConfirmOpen(false);
    setDeleteChatId(null);
  };

  return (
    <Box
      sx={{
        width: 280,
        height: '100%',
        borderRight: 1,
        borderColor: 'divider',
        display: 'flex',
        flexDirection: 'column',
        bgcolor: 'background.paper',
      }}
    >
      {/* Title Bar */}
      <Box
        sx={{
          p: 2,
          borderBottom: 1,
          borderColor: 'divider',
        }}
      >
        <Typography variant="h6" sx={{ fontWeight: 600, mb: 2 }}>
          Chats
        </Typography>
        <Button
          variant="outlined"
          fullWidth
          startIcon={<Add />}
          onClick={onNewChat}
          sx={{ textTransform: 'none' }}
        >
          New chat
        </Button>
      </Box>

      {/* Chat List */}
      <List
        sx={{
          flex: 1,
          overflow: 'auto',
          p: 1,
        }}
      >
        {chats.map((chat) => (
          <Box key={chat.id} sx={{ mb: 0.5 }}>
            {/* Chat Item */}
            <ListItemButton
              selected={chat.id === activeChatId}
              onClick={() => onSelectChat(chat.id)}
              sx={{
                borderRadius: 1,
                pr: 1,
                '&.Mui-selected': {
                  bgcolor: 'action.selected',
                },
              }}
            >
              <ListItemText
                primary={chat.title}
                primaryTypographyProps={{
                  noWrap: true,
                  sx: { fontWeight: chat.id === activeChatId ? 600 : 400 },
                }}
              />
              <IconButton
                size="small"
                onClick={(e) => handleMenuOpen(e, chat.id)}
                sx={{ ml: 1 }}
              >
                <MoreVert fontSize="small" />
              </IconButton>
            </ListItemButton>

            {/* Conversations (subchats) - shown when chat is active */}
            {chat.id === activeChatId && chat.conversations && chat.conversations.length > 0 && (
              <List sx={{ pl: 2, py: 0 }}>
                {chat.conversations.map((conv, idx) => (
                  <ListItemButton
                    key={conv.id}
                    selected={conv.id === activeConversationId}
                    onClick={() => onSelectConversation(conv.id)}
                    sx={{
                      borderRadius: 1,
                      py: 0.5,
                      minHeight: 32,
                    }}
                  >
                    <Radio
                      checked={conv.id === activeConversationId}
                      size="small"
                      sx={{ p: 0, mr: 1 }}
                    />
                    <ListItemText
                      primary={`Conversation ${idx + 1}`}
                      primaryTypographyProps={{
                        variant: 'body2',
                        noWrap: true,
                      }}
                    />
                  </ListItemButton>
                ))}
              </List>
            )}
          </Box>
        ))}
      </List>

      {/* Context Menu */}
      <Menu
        anchorEl={menuAnchor}
        open={Boolean(menuAnchor)}
        onClose={handleMenuClose}
      >
        <MenuItem onClick={handleRenameClick}>
          <Edit fontSize="small" sx={{ mr: 1 }} />
          Rename
        </MenuItem>
        <MenuItem onClick={handleDeleteClick}>
          <Delete fontSize="small" sx={{ mr: 1 }} />
          Delete
        </MenuItem>
      </Menu>

      {/* Rename Dialog */}
      <Dialog open={renameDialogOpen} onClose={() => setRenameDialogOpen(false)} maxWidth="xs" fullWidth>
        <DialogTitle>Rename chat</DialogTitle>
        <DialogContent>
          <TextField
            autoFocus
            fullWidth
            value={renameValue}
            onChange={(e) => setRenameValue(e.target.value)}
            onKeyPress={(e) => {
              if (e.key === 'Enter') {
                handleRenameSubmit();
              }
            }}
            sx={{ mt: 1 }}
          />
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setRenameDialogOpen(false)}>Cancel</Button>
          <Button onClick={handleRenameSubmit} variant="contained">
            Save
          </Button>
        </DialogActions>
      </Dialog>

      {/* Delete Confirmation Dialog */}
      <Dialog open={deleteConfirmOpen} onClose={() => setDeleteConfirmOpen(false)} maxWidth="xs">
        <DialogTitle>Delete chat?</DialogTitle>
        <DialogContent>
          <Typography>This will permanently delete this chat and all its conversations.</Typography>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setDeleteConfirmOpen(false)}>Cancel</Button>
          <Button onClick={handleDeleteConfirm} color="error" variant="contained">
            Delete
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
}

export default Sidebar;
