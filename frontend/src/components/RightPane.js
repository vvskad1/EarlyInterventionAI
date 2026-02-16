import React, { useRef, useEffect } from 'react';
import {
  Box,
  Button,
  Card,
  CardContent,
  Typography,
  TextField,
  IconButton,
  Paper,
  CircularProgress,
  Container,
  Grid,
  Checkbox,
  FormControlLabel,
} from '@mui/material';
import { Menu, Brightness4, Brightness7, ArrowUpward } from '@mui/icons-material';
import VoiceControls from './VoiceControls';

/**
 * RightPane Component
 * Main content area with:
 * - Age/Domains controls
 * - Notes field
 * - Generate button
 * - Plan sections (Goals, Strategies, Advice)
 * - Chat messages
 * - Bottom input dock with voice controls
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
  autoSpeak,
  onToggleSidebar,
  onToggleTheme,
  onAgeChange,
  onDomainsChange,
  onNotesChange,
  onGenerate,
  onChatMessageChange,
  onSendMessage,
  onAutoSpeakChange,
  isSpeaking = false,
  onStopSpeech,
}) {
  const messagesEndRef = useRef(null);
  const planResultsRef = useRef(null);

  // Auto-scroll to bottom when new messages arrive
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  // Scroll to plan results when plan is generated
  useEffect(() => {
    if (plan && planResultsRef.current) {
      planResultsRef.current.scrollIntoView({ behavior: 'smooth', block: 'start' });
    }
  }, [plan]);

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      onSendMessage();
    }
  };

  // Handle voice transcript from speech-to-text
  const handleTranscript = (transcript) => {
    onChatMessageChange(transcript);
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
          py: 3,
        }}
      >
        <Container maxWidth="md" sx={{ px: { xs: 2, sm: 3 } }}>
          <Box sx={{ display: 'flex', flexDirection: 'column', gap: 3 }}>
            {/* Context Header */}
            <Box sx={{ mb: 1 }}>
              <Typography
                variant="h5"
                sx={{
                  fontWeight: 700,
                  color: 'text.primary',
                  mb: 0.5,
                }}
              >
                Early Intervention Plan
              </Typography>
              <Typography
                variant="body2"
                sx={{
                  color: 'text.secondary',
                  lineHeight: 1.5,
                }}
              >
                Provide a few details to generate a personalized support plan.
              </Typography>
            </Box>

            {/* Child Profile Card */}
            <Card
              variant="outlined"
              sx={{
                borderRadius: 2,
                borderColor: '#C9C4BC',
                borderWidth: 1.5,
                boxShadow: '0 2px 4px rgba(0,0,0,0.08)',
              }}
            >
              <CardContent sx={{ p: 2.5 }}>
                <Typography
                  variant="subtitle2"
                  sx={{
                    fontWeight: 700,
                    textTransform: 'uppercase',
                    letterSpacing: '1px',
                    fontSize: '0.75rem',
                    mb: 2.5,
                    opacity: 0.7,
                  }}
                >
                  Child Profile
                </Typography>

                <Grid container spacing={2}>
                  {/* Age Text Input */}
                  <Grid item xs={12}>
                    <TextField
                      fullWidth
                      size="small"
                      label="Age (0-36 months)"
                      type="number"
                      value={ageMonths || ''}
                      onChange={(e) => {
                        const value = e.target.value;
                        if (value === '') {
                          onAgeChange('');
                        } else {
                          const numValue = parseInt(value);
                          if (numValue >= 0 && numValue <= 36) {
                            onAgeChange(numValue);
                          }
                        }
                      }}
                      inputProps={{
                        min: 0,
                        max: 36,
                        style: { fontSize: '0.875rem' }
                      }}
                      sx={{
                        '& .MuiInputBase-root': {
                          py: 0.5,
                        },
                      }}
                      helperText="Enter child's age in months"
                    />
                  </Grid>

                  {/* Areas of Concern - Checkboxes */}
                  <Grid item xs={12}>
                    <Box
                      sx={{
                        border: '1px solid',
                        borderColor: 'divider',
                        borderRadius: 1,
                        p: 2,
                        backgroundColor: 'background.paper',
                      }}
                    >
                      <Typography
                        variant="caption"
                        sx={{
                          fontSize: '0.75rem',
                          fontWeight: 600,
                          color: 'text.secondary',
                          mb: 1.5,
                          display: 'block',
                          textTransform: 'uppercase',
                          letterSpacing: '0.5px'
                        }}
                      >
                        Areas of Concern
                      </Typography>
                      <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 1, alignItems: 'center' }}>
                        <FormControlLabel
                          control={
                            <Checkbox
                              checked={(domains || []).includes('communication')}
                              onChange={(e) => {
                                const newDomains = e.target.checked
                                  ? [...(domains || []), 'communication']
                                  : (domains || []).filter(d => d !== 'communication');
                                onDomainsChange(newDomains);
                              }}
                              size="small"
                              sx={{
                                '&.Mui-checked': {
                                  color: 'primary.main',
                                },
                              }}
                            />
                          }
                          label={
                            <Typography sx={{ fontSize: '0.875rem', fontWeight: 500, color: 'text.secondary' }}>
                              Communication
                            </Typography>
                          }
                        />
                        <FormControlLabel
                          control={
                            <Checkbox
                              checked={(domains || []).includes('social')}
                              onChange={(e) => {
                                const newDomains = e.target.checked
                                  ? [...(domains || []), 'social']
                                  : (domains || []).filter(d => d !== 'social');
                                onDomainsChange(newDomains);
                              }}
                              size="small"
                              sx={{
                                '&.Mui-checked': {
                                  color: 'primary.main',
                                },
                              }}
                            />
                          }
                          label={
                            <Typography sx={{ fontSize: '0.875rem', fontWeight: 500, color: 'text.secondary' }}>
                              Social/Emotional
                            </Typography>
                          }
                        />
                        <FormControlLabel
                          control={
                            <Checkbox
                              checked={(domains || []).includes('fine_motor')}
                              onChange={(e) => {
                                const newDomains = e.target.checked
                                  ? [...(domains || []), 'fine_motor']
                                  : (domains || []).filter(d => d !== 'fine_motor');
                                onDomainsChange(newDomains);
                              }}
                              size="small"
                              sx={{
                                '&.Mui-checked': {
                                  color: 'primary.main',
                                },
                              }}
                            />
                          }
                          label={
                            <Typography sx={{ fontSize: '0.875rem', fontWeight: 500, color: 'text.secondary' }}>
                              Fine Motor
                            </Typography>
                          }
                        />
                        <FormControlLabel
                          control={
                            <Checkbox
                              checked={(domains || []).includes('gross_motor')}
                              onChange={(e) => {
                                const newDomains = e.target.checked
                                  ? [...(domains || []), 'gross_motor']
                                  : (domains || []).filter(d => d !== 'gross_motor');
                                onDomainsChange(newDomains);
                              }}
                              size="small"
                              sx={{
                                '&.Mui-checked': {
                                  color: 'primary.main',
                                },
                              }}
                            />
                          }
                          label={
                            <Typography sx={{ fontSize: '0.875rem', fontWeight: 500, color: 'text.secondary' }}>
                              Gross Motor
                            </Typography>
                          }
                        />
                        <FormControlLabel
                          control={
                            <Checkbox
                              checked={(domains || []).includes('cognitive')}
                              onChange={(e) => {
                                const newDomains = e.target.checked
                                  ? [...(domains || []), 'cognitive']
                                  : (domains || []).filter(d => d !== 'cognitive');
                                onDomainsChange(newDomains);
                              }}
                              size="small"
                              sx={{
                                '&.Mui-checked': {
                                  color: 'primary.main',
                                },
                              }}
                            />
                          }
                          label={
                            <Typography sx={{ fontSize: '0.875rem', fontWeight: 500, color: 'text.secondary' }}>
                              Cognitive
                            </Typography>
                          }
                        />
                        <FormControlLabel
                          control={
                            <Checkbox
                              checked={(domains || []).includes('adaptive')}
                              onChange={(e) => {
                                const newDomains = e.target.checked
                                  ? [...(domains || []), 'adaptive']
                                  : (domains || []).filter(d => d !== 'adaptive');
                                onDomainsChange(newDomains);
                              }}
                              size="small"
                              sx={{
                                '&.Mui-checked': {
                                  color: 'primary.main',
                                },
                              }}
                            />
                          }
                          label={
                            <Typography sx={{ fontSize: '0.875rem', fontWeight: 500, color: 'text.secondary' }}>
                              Adaptive
                            </Typography>
                          }
                        />
                      </Box>
                    </Box>
                  </Grid>
                </Grid>
              </CardContent>
            </Card>

            {/* Observations Card */}
            <Card
              variant="outlined"
              sx={{
                borderRadius: 2,
                borderColor: '#C9C4BC',
                borderWidth: 1.5,
                boxShadow: '0 2px 4px rgba(0,0,0,0.08)',
              }}
            >
              <CardContent sx={{ p: 4.5 }}>
                <Typography
                  variant="subtitle2"
                  sx={{
                    fontWeight: 700,
                    textTransform: 'uppercase',
                    letterSpacing: '1px',
                    fontSize: '0.75rem',
                    mb: 0.5,
                    opacity: 0.7,
                  }}
                >
                  Observations <Box component="span" sx={{ fontWeight: 500, textTransform: 'none', opacity: 0.5, fontSize: '0.7rem' }}>(Optional)</Box>
                </Typography>

                <Typography
                  variant="body2"
                  sx={{
                    color: 'text.secondary',
                    mb: 2.5,
                    fontSize: '0.875rem',
                  }}
                >
                  Share anything you've noticed — behaviors, strengths, recent changes…
                </Typography>

                <TextField
                  fullWidth
                  multiline
                  rows={6}
                  placeholder="Example: Responds well to music, struggles with transitions, prefers visual cues…"
                  value={notes || ''}
                  onChange={(e) => onNotesChange(e.target.value)}
                />
              </CardContent>
            </Card>

            {/* Primary Action Zone */}
            <Box
              sx={{
                display: 'flex',
                flexDirection: 'column',
                alignItems: 'center',
                gap: 1.5,
                py: 1,
              }}
            >
              <Button
                variant="contained"
                onClick={onGenerate}
                disabled={!ageMonths || !domains || domains.length === 0 || isGenerating}
                sx={{
                  minWidth: 280,
                  py: 1.75,
                  px: 4,
                  borderRadius: 2,
                  textTransform: 'none',
                  fontSize: '1rem',
                  fontWeight: 600,
                  boxShadow: '0 2px 8px rgba(79,138,139,0.3)',
                  '&:hover': {
                    boxShadow: '0 4px 12px rgba(79,138,139,0.4)',
                  },
                }}
              >
                {isGenerating ? <CircularProgress size={24} sx={{ color: 'inherit' }} /> : 'Generate Plan'}
              </Button>

              <Typography
                variant="caption"
                sx={{
                  color: 'text.primary',
                  opacity: 0.6,
                  textAlign: 'center',
                  maxWidth: 400,
                  fontSize: '0.75rem',
                  lineHeight: 1.4,
                  fontWeight: 500,
                }}
              >
                This supports — not replaces — professional evaluation
              </Typography>
            </Box>

            {/* Plan Results Display */}
            {plan && (
              <Box ref={planResultsRef} sx={{ mt: 3 }}>
                <Typography
                  variant="h6"
                  sx={{
                    fontWeight: 700,
                    mb: 2.5,
                    fontSize: '1.1rem',
                    color: 'text.primary',
                  }}
                >
                  Intervention Plan
                </Typography>

                {/* Goals Section */}
                <Card
                  variant="outlined"
                  sx={{
                    mb: 2,
                    borderRadius: 2,
                    borderColor: 'divider',
                    borderWidth: 1.5,
                    boxShadow: '0 2px 4px rgba(0,0,0,0.08)',
                  }}
                >
                  <CardContent sx={{ p: 2.5 }}>
                    <Typography
                      variant="subtitle2"
                      sx={{
                        fontWeight: 700,
                        textTransform: 'uppercase',
                        letterSpacing: '1px',
                        fontSize: '0.75rem',
                        mb: 1.5,
                        color: 'primary.main',
                      }}
                    >
                      🎯 Goals
                    </Typography>
                    <Typography
                      variant="body2"
                      sx={{
                        lineHeight: 1.7,
                        whiteSpace: 'pre-wrap',
                      }}
                    >
                      {plan.Goals}
                    </Typography>
                  </CardContent>
                </Card>

                {/* Strategies Section */}
                <Card
                  variant="outlined"
                  sx={{
                    mb: 2,
                    borderRadius: 2,
                    borderColor: 'divider',
                    borderWidth: 1.5,
                    boxShadow: '0 2px 4px rgba(0,0,0,0.08)',
                  }}
                >
                  <CardContent sx={{ p: 2.5 }}>
                    <Typography
                      variant="subtitle2"
                      sx={{
                        fontWeight: 700,
                        textTransform: 'uppercase',
                        letterSpacing: '1px',
                        fontSize: '0.75rem',
                        mb: 1.5,
                        color: 'primary.main',
                      }}
                    >
                      🔧 Strategies
                    </Typography>
                    <Typography
                      variant="body2"
                      sx={{
                        lineHeight: 1.7,
                        whiteSpace: 'pre-wrap',
                      }}
                    >
                      {plan.Strategies}
                    </Typography>
                  </CardContent>
                </Card>

                {/* Advice for Parents Section */}
                <Card
                  variant="outlined"
                  sx={{
                    mb: 2,
                    borderRadius: 2,
                    borderColor: 'divider',
                    borderWidth: 1.5,
                    boxShadow: '0 2px 4px rgba(0,0,0,0.08)',
                  }}
                >
                  <CardContent sx={{ p: 2.5 }}>
                    <Typography
                      variant="subtitle2"
                      sx={{
                        fontWeight: 700,
                        textTransform: 'uppercase',
                        letterSpacing: '1px',
                        fontSize: '0.75rem',
                        mb: 1.5,
                        color: 'primary.main',
                      }}
                    >
                      💡 Advice for Parents
                    </Typography>
                    <Typography
                      variant="body2"
                      sx={{
                        lineHeight: 1.7,
                        whiteSpace: 'pre-wrap',
                      }}
                    >
                      {plan['Advice for Parents'] || plan.Advice_for_Parents}
                    </Typography>
                  </CardContent>
                </Card>
              </Box>
            )}

            {/* Chat Messages Area */}
            {messages && messages.length > 0 && (
              <Box sx={{ display: 'flex', flexDirection: 'column', gap: 1.5, mt: 2 }}>
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
                        borderRadius: msg.role === 'user' ? '18px 18px 4px 18px' : '18px 18px 18px 4px',
                        backgroundColor: msg.role === 'user'
                          ? (themeMode === 'dark' ? '#2A4A3A' : '#D9FDD3')
                          : 'background.paper',
                        border: '1px solid',
                        borderColor: msg.role === 'user'
                          ? (themeMode === 'dark' ? '#3A5A4A' : '#C1E9BC')
                          : 'divider',
                        color: 'text.primary',
                        boxShadow: msg.role === 'user' ? '0 1px 2px rgba(0,0,0,0.05)' : '0 1px 3px rgba(0,0,0,0.08)',
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
        </Container>
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
          {/* Voice Controls */}
          <VoiceControls
            onTranscript={handleTranscript}
            autoSpeak={autoSpeak}
            onAutoSpeakChange={onAutoSpeakChange}
            disabled={isSending}
            onSendMessage={onSendMessage}
            isSpeaking={isSpeaking}
            onStopSpeech={onStopSpeech}
          />

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
