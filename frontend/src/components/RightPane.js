import React, { useRef, useEffect } from 'react';
import {
  Box,
  Button,
  Select,
  MenuItem,
  FormControl,
  InputLabel,
  Card,
  CardContent,
  Typography,
  TextField,
  IconButton,
  Paper,
  CircularProgress,
} from '@mui/material';
import { PlayArrowOutlined, Menu, Brightness4, Brightness7, ArrowUpward } from '@mui/icons-material';

/**
 * RightPane Component
 * Main content area with:
 * - Age/Domains controls
 * - Notes field
 * - Generate button
 * - Plan sections (Goals, Strategies, Advice)
 * - Chat messages
 * - Bottom input dock
 */
function RightPane({
  chatTitle,
  ageMonths,
  domains,
  notes,
  plan,
  messages,
  chatMessage,
  isGenerating,
  isSending,
  sidebarOpen,
  themeMode,
  onToggleSidebar,
  onToggleTheme,
  onAgeChange,
  onDomainsChange,
  onNotesChange,
  onGenerate,
  onChatMessageChange,
  onSendMessage,
}) {
  const messagesEndRef = useRef(null);

  // Auto-scroll to bottom when new messages arrive
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      onSendMessage();
    }
  };

  return (
    <Box
      sx={{
        flex: 1,
        height: '100vh',
        display: 'flex',
        flexDirection: 'column',
        overflow: 'hidden',
      }}
    >
      {/* Header Bar */}
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
        {/* Sidebar Toggle */}
        <IconButton
          onClick={onToggleSidebar}
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

        {/* Chat Title */}
        <Typography
          variant="body1"
          sx={{
            flex: 1,
            fontWeight: 600,
            color: 'text.primary',
            overflow: 'hidden',
            textOverflow: 'ellipsis',
            whiteSpace: 'nowrap',
          }}
        >
          {chatTitle || 'Early Intervention AI'}
        </Typography>

        {/* Theme Toggle */}
        <IconButton
          onClick={onToggleTheme}
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

      {/* Scrollable Content Area */}
      <Box
        sx={{
          flex: 1,
          overflow: 'auto',
          p: 2,
          display: 'flex',
          flexDirection: 'column',
          gap: 2,
        }}
      >
          {/* Top Controls Row */}
          <Paper
            elevation={0}
            sx={{
            p: 2.5,
            display: 'flex',
            alignItems: 'center',
            gap: 2,
            flexWrap: 'wrap',
            borderRadius: 3,
            bgcolor: 'background.paper',
            border: '1px solid',
            borderColor: 'divider',
          }}
          >
            {/* Age Dropdown */}
            <FormControl sx={{ minWidth: 140 }} size="small">
            <InputLabel>Age</InputLabel>
            <Select
              value={ageMonths || ''}
              label="Age"
              onChange={(e) => onAgeChange(e.target.value)}
              sx={{
                borderRadius: 2,
                '& .MuiOutlinedInput-notchedOutline': {
                  borderColor: 'divider',
                },
              }}
            >
              {Array.from({ length: 37 }, (_, i) => (
                <MenuItem key={i} value={i}>
                  {i} months
                </MenuItem>
              ))}
            </Select>
          </FormControl>

          {/* Areas of Concern - Multiple Select */}
          <FormControl sx={{ minWidth: 300 }} size="small">
            <InputLabel>Areas of Concern</InputLabel>
            <Select
              multiple
              value={domains || []}
              label="Areas of Concern"
              onChange={(e) => onDomainsChange(e.target.value)}
              renderValue={(selected) => selected.map(d => 
                d.replace('_', ' ').replace(/\b\w/g, l => l.toUpperCase())
              ).join(', ')}
              sx={{
                borderRadius: 2,
                '& .MuiOutlinedInput-notchedOutline': {
                  borderColor: 'divider',
                },
              }}
            >
              <MenuItem value="communication">Communication</MenuItem>
              <MenuItem value="social">Social/Emotional</MenuItem>
              <MenuItem value="fine_motor">Fine Motor</MenuItem>
              <MenuItem value="gross_motor">Gross Motor</MenuItem>
              <MenuItem value="cognitive">Cognitive</MenuItem>
              <MenuItem value="adaptive">Adaptive</MenuItem>
            </Select>
          </FormControl>
        </Paper>

          {/* Notes Field */}
          <Paper
          elevation={0}
          sx={{
            p: 2,
            border: '1px solid',
            borderColor: 'divider',
          }}
          >
            <TextField
              fullWidth
              multiline
              rows={3}
              label="Notes"
              placeholder="Add notes or observations about the child..."
              value={notes || ''}
              onChange={(e) => onNotesChange(e.target.value)}
              sx={{
                '& .MuiOutlinedInput-root': {
                  borderRadius: 2,
                },
              }}
            />
          </Paper>

          {/* Generate Button */}
          <Box sx={{ display: 'flex', justifyContent: 'center', mt: 1 }}>
            <Button
              variant="outlined"
              onClick={onGenerate}
              disabled={!ageMonths || !domains || domains.length === 0 || isGenerating}
              sx={{
                minWidth: 240,
                py: 1.5,
                borderRadius: 3,
                textTransform: 'none',
                fontSize: '1rem',
                fontWeight: 600,
                borderColor: 'divider',
                color: 'text.primary',
                '&:hover': {
                  borderColor: 'text.secondary',
                  bgcolor: 'action.hover',
                },
              }}
            >
              {isGenerating ? <CircularProgress size={24} /> : 'Generate Plan'}
            </Button>
          </Box>

        {/* Plan Sections (shown after Generate) */}
        {plan && (
          <>
            {/* Goals Section */}
            <Card
              elevation={0}
              sx={{
                border: '1px solid',
                borderColor: 'divider',
                borderRadius: 3,
              }}
            >
              <CardContent>
                <Typography
                  variant="h6"
                  sx={{ mb: 2, fontWeight: 700, fontSize: '1.1rem' }}
                >
                  🎯 Goals
                </Typography>
                <Typography
                  variant="body2"
                  sx={{ whiteSpace: 'pre-wrap', lineHeight: 1.6 }}
                >
                  {plan.Goals}
                </Typography>
              </CardContent>
            </Card>

            {/* Strategies Section */}
            <Card
              elevation={0}
              sx={{
                border: '1px solid',
                borderColor: 'divider',
                borderRadius: 3,
              }}
            >
              <CardContent>
                <Typography
                  variant="h6"
                  sx={{ mb: 2, fontWeight: 700, fontSize: '1.1rem' }}
                >
                  ⚡ Strategies
                </Typography>
                <Typography
                  variant="body2"
                  sx={{ whiteSpace: 'pre-wrap', lineHeight: 1.6 }}
                >
                  {plan.Strategies}
                </Typography>
              </CardContent>
            </Card>

            {/* Advice for Parents Section */}
            <Card
              elevation={0}
              sx={{
                border: '1px solid',
                borderColor: 'divider',
                borderRadius: 3,
              }}
            >
              <CardContent>
                <Typography
                  variant="h6"
                  sx={{ mb: 2, fontWeight: 700, fontSize: '1.1rem' }}
                >
                  💡 Advice for Parents
                </Typography>
                <Typography
                  variant="body2"
                  sx={{ whiteSpace: 'pre-wrap', lineHeight: 1.6 }}
                >
                  {plan['Advice for Parents']}
                </Typography>
              </CardContent>
            </Card>
          </>
        )}

        {/* Chat Messages Area */}
        {messages && messages.length > 0 && (
          <Box sx={{ display: 'flex', flexDirection: 'column', gap: 1 }}>
            {messages.map((msg, index) => (
              <Box
                key={index}
                sx={{
                  display: 'flex',
                  justifyContent: msg.role === 'user' ? 'flex-end' : 'flex-start',
                }}
              >
                <Paper
                  elevation={0}
                  sx={{
                    p: 2,
                    maxWidth: '75%',
                    borderRadius: 3,
                    backgroundColor: 'background.paper',
                    border: '1px solid',
                    borderColor: 'divider',
                    color: 'text.primary',
                  }}
                >
                  <Typography
                    variant="body2"
                    sx={{
                      whiteSpace: 'pre-wrap',
                      lineHeight: 1.6,
                      '& strong': { fontWeight: 700 },
                    }}
                    dangerouslySetInnerHTML={{
                      __html: msg.content
                        .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
                        .replace(/---/g, '<hr style="border: none; border-top: 1px solid rgba(255,255,255,0.1); margin: 12px 0;" />')
                        .replace(/\n/g, '<br />'),
                    }}
                  />
                </Paper>
              </Box>
            ))}
            <div ref={messagesEndRef} />
          </Box>
        )}
      </Box>

      {/* Bottom Input Dock (Sticky) */}
      <Box
        sx={{
          position: 'sticky',
          bottom: 0,
          borderTop: '1px solid',
          borderColor: 'divider',
          bgcolor: 'background.default',
          p: 2,
        }}
      >
        <Paper
          elevation={0}
          sx={{
            display: 'flex',
            alignItems: 'center',
            gap: 1,
            p: 1,
            borderRadius: 3,
            border: '1px solid',
            borderColor: 'divider',
            bgcolor: 'background.paper',
          }}
        >
          <TextField
            fullWidth
            placeholder="Send Message"
            value={chatMessage}
            onChange={(e) => onChatMessageChange(e.target.value)}
            onKeyPress={handleKeyPress}
            disabled={isSending}
            variant="standard"
            InputProps={{
              disableUnderline: true,
              sx: { px: 1 },
            }}
          />
          <IconButton
            onClick={onSendMessage}
            disabled={!chatMessage.trim() || isSending}
            sx={{
              width: 32,
              height: 32,
              borderRadius: '50%',
              bgcolor: chatMessage.trim() ? 'text.primary' : 'transparent',
              color: chatMessage.trim() ? 'background.paper' : 'text.disabled',
              transition: 'all 0.2s ease',
              '&:hover': {
                bgcolor: chatMessage.trim() ? 'text.primary' : 'transparent',
                opacity: 0.8,
              },
              '&.Mui-disabled': {
                bgcolor: 'transparent',
                color: 'text.disabled',
              },
            }}
          >
            {isSending ? (
              <CircularProgress size={18} sx={{ color: 'background.paper' }} />
            ) : (
              <ArrowUpward sx={{ fontSize: 20 }} />
            )}
          </IconButton>
        </Paper>
      </Box>
    </Box>
  );
}

export default RightPane;
