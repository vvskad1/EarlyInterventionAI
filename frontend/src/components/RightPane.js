import React, { useRef, useEffect, useState } from 'react';
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
  Chip,
} from '@mui/material';
import { Menu, Brightness4, Brightness7, ArrowUpward, VerifiedUser } from '@mui/icons-material';
import VoiceControls from './VoiceControls';
import CitedText from './CitedText';
import EvidenceDrawer from './EvidenceDrawer';
import SectionEvidencePanel from './SectionEvidencePanel';
import {
  parseSources,
  extractCitations,
  calculateConfidence,
  parseBulletPoints,
} from '../utils/citationUtils';

/**
 * Parse Intervention_Plan markdown into sections
 * Extracts Goals, Strategies, Advice, and Sources from markdown format
 */
function parseInterventionPlan(markdownContent) {
  if (!markdownContent) return null;

  // Extract sections using regex
  const sections = {};

  // Match ### 🎯 Goals ... (content until next ###)
  const goalsMatch = markdownContent.match(/###\s*🎯\s*Goals\s*\n(.*?)(?=###|$)/s);
  if (goalsMatch) sections.Goals = goalsMatch[1].trim();

  // Match ### 🔧 Strategies
  const strategiesMatch = markdownContent.match(/###\s*🔧\s*Strategies\s*\n(.*?)(?=###|$)/s);
  if (strategiesMatch) sections.Strategies = strategiesMatch[1].trim();

  // Match ### 💡 Advice for Parents
  const adviceMatch = markdownContent.match(/###\s*💡\s*Advice for Parents\s*\n(.*?)(?=###|$)/s);
  if (adviceMatch) sections['Advice for Parents'] = adviceMatch[1].trim();

  // Match ### 📚 Sources
  const sourcesMatch = markdownContent.match(/###\s*📚\s*Sources\s*\n(.*?)(?=###|$)/s);
  if (sourcesMatch) sections.Sources = sourcesMatch[1].trim();

  return sections;
}

/**
 * Render chat message content with interactive citations
 * Preserves formatting while making citations clickable
 */
function renderChatMessage(content, onCitationClick) {
  if (!content) return null;

  // Split by newlines to preserve structure
  const lines = content.split('\n');
  const elements = [];

  lines.forEach((line, idx) => {
    if (!line.trim()) {
      // Empty line - add spacing
      elements.push(<Box key={`space-${idx}`} sx={{ height: '0.5em' }} />);
      return;
    }

    // Check for horizontal rule
    if (line.trim() === '---') {
      elements.push(
        <Box
          key={`hr-${idx}`}
          sx={{
            borderTop: '1px solid',
            borderColor: 'divider',
            opacity: 0.3,
            my: 1.5,
          }}
        />
      );
      return;
    }

    // Check for numbered list item (1. 2. etc.)
    const numberedMatch = line.match(/^(\d+)\.\s+(.+)$/);
    if (numberedMatch) {
      const number = numberedMatch[1];
      const text = numberedMatch[2];
      // Convert **text** to <strong>text</strong> for bold formatting
      const formattedText = text.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');

      elements.push(
        <Box key={`num-${idx}`} sx={{ display: 'flex', gap: 1, mb: 1 }}>
          <Typography variant="body2" sx={{ fontWeight: 600, minWidth: '24px' }}>
            {number}.
          </Typography>
          <Typography variant="body2" sx={{ flex: 1, lineHeight: 1.6 }}>
            <CitedText
              text={formattedText}
              onCitationClick={onCitationClick}
              highlightMeasurable={false}
            />
          </Typography>
        </Box>
      );
      return;
    }

    // Regular line - apply CitedText with bold formatting support
    const formattedLine = line.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');

    elements.push(
      <Typography
        key={`line-${idx}`}
        variant="body2"
        component="div"
        sx={{ mb: 0.5, lineHeight: 1.6 }}
      >
        <CitedText
          text={formattedLine}
          onCitationClick={onCitationClick}
          highlightMeasurable={false}
        />
      </Typography>
    );
  });

  return elements;
}

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

  // Evidence drawer state
  const [drawerOpen, setDrawerOpen] = useState(false);
  const [selectedSource, setSelectedSource] = useState(null);

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

  const isStructuredPlan = Boolean(
    plan &&
    Array.isArray(plan.goals) &&
    Array.isArray(plan.strategies) &&
    Array.isArray(plan.advice) &&
    Array.isArray(plan.sources)
  );

  // Backward compatibility: parse legacy markdown plan if present
  const parsedPlan = !isStructuredPlan && plan?.Intervention_Plan
    ? parseInterventionPlan(plan.Intervention_Plan)
    : null;

  // Normalize sources for evidence panel + drawer
  const sources = isStructuredPlan
    ? (plan.sources || []).map((source) => ({
      id: source.id,
      title: source.title,
      authors: source.title,
      year: '',
      excerpt: source.excerpt || '',
      link: '',
    }))
    : (parsedPlan?.Sources ? parseSources(parsedPlan.Sources) : []);

  const goalCitationIds = isStructuredPlan
    ? [...new Set((plan.goals || []).map((goal) => goal.source).filter(Boolean))]
    : extractCitations(parsedPlan?.Goals || '');

  const strategyCitationIds = isStructuredPlan
    ? [...new Set((plan.strategies || []).map((strategy) => strategy.source).filter(Boolean))]
    : extractCitations(parsedPlan?.Strategies || '');

  const adviceCitationIds = isStructuredPlan
    ? [...new Set((plan.advice || []).map((item) => item.source).filter(Boolean))]
    : extractCitations(parsedPlan?.['Advice for Parents'] || parsedPlan?.Advice_for_Parents || '');

  // Calculate confidence
  const confidence = (isStructuredPlan || parsedPlan)
    ? calculateConfidence({
      goals: isStructuredPlan ? (plan.goals || []).map((goal) => `${goal.text} (Source ${goal.source})`).join('\n') : (parsedPlan?.Goals || ''),
      strategies: isStructuredPlan ? (plan.strategies || []).map((strategy) => `${strategy.name} (Source ${strategy.source})`).join('\n') : (parsedPlan?.Strategies || ''),
      advice: isStructuredPlan ? (plan.advice || []).map((item) => `${item.text} (Source ${item.source})`).join('\n') : (parsedPlan?.['Advice for Parents'] || ''),
    }, sources)
    : null;

  const safetyAlert = plan?.safety_alert || null;

  // Handle citation click
  const handleCitationClick = (sourceId) => {
    const source = sources.find(s => s.id === sourceId);
    if (source) {
      setSelectedSource(source);
      setDrawerOpen(true);
    } else {
      // Fallback: Create placeholder source for citations without details
      setSelectedSource({
        id: sourceId,
        title: `Source ${sourceId}`,
        authors: 'From knowledge base',
        year: '',
        excerpt: 'This source was referenced from the retrieved RAG context. Full source details are available in the intervention plan Sources section.',
        link: ''
      });
      setDrawerOpen(true);
    }
  };

  // Handle source click from evidence panel
  const handleSourceClick = (source) => {
    setSelectedSource(source);
    setDrawerOpen(true);
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
            {(isStructuredPlan || parsedPlan) && (
              <Box ref={planResultsRef} sx={{ mt: 3 }}>
                {safetyAlert && safetyAlert.level !== 'routine' && (
                  <Card
                    variant="outlined"
                    sx={{
                      mb: 2,
                      borderRadius: 2,
                      borderColor: safetyAlert.level === 'urgent' ? 'error.main' : 'warning.main',
                      borderWidth: 2,
                      bgcolor: safetyAlert.level === 'urgent' ? 'error.lighter' : 'warning.lighter',
                    }}
                  >
                    <CardContent sx={{ p: 2.5 }}>
                      <Typography variant="subtitle1" sx={{ fontWeight: 700, mb: 1 }}>
                        {safetyAlert.level === 'urgent' ? '🚨 Urgent Medical Concern' : '⚠️ Regression Concern'}
                      </Typography>
                      <Typography variant="body2" sx={{ mb: 1 }}>
                        {safetyAlert.message}
                      </Typography>
                      <Typography variant="body2" sx={{ fontWeight: 600 }}>
                        Recommended action: {safetyAlert.recommended_action}
                      </Typography>
                    </CardContent>
                  </Card>
                )}

                <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', mb: 2.5 }}>
                  <Typography
                    variant="h6"
                    sx={{
                      fontWeight: 700,
                      fontSize: '1.1rem',
                      color: 'text.primary',
                    }}
                  >
                    Intervention Plan
                  </Typography>

                  {/* Confidence Badge */}
                  {confidence && (
                    <Chip
                      icon={<VerifiedUser />}
                      label={confidence.label}
                      color={confidence.color}
                      size="small"
                      sx={{ fontWeight: 600 }}
                    />
                  )}
                </Box>

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
                        fontSize: '1rem',
                        mb: 1.5,
                        color: 'primary.main',
                      }}
                    >
                      🎯 Goals
                    </Typography>
                    <Box component="ul" sx={{ pl: 3, m: 0, listStyleType: 'disc' }}>
                      {(isStructuredPlan
                        ? (plan.goals || []).map((goal) => `${goal.text} (Source ${goal.source})`)
                        : parseBulletPoints(parsedPlan?.Goals || '')
                      ).map((bullet, idx) => (
                        <Typography
                          key={idx}
                          component="li"
                          variant="body2"
                          sx={{ lineHeight: 1.7, mb: 1.5, display: 'list-item' }}
                        >
                          <CitedText
                            text={bullet}
                            onCitationClick={handleCitationClick}
                            highlightMeasurable={true}
                          />
                        </Typography>
                      ))}
                    </Box>

                    <SectionEvidencePanel
                      citationIds={goalCitationIds}
                      sources={sources}
                      onSourceClick={handleSourceClick}
                    />
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
                        fontSize: '1rem',
                        mb: 1.5,
                        color: 'primary.main',
                      }}
                    >
                      🔧 Strategies
                    </Typography>
                    {isStructuredPlan ? (
                      <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
                        {(plan.strategies || []).map((strategy, idx) => (
                          <Box key={idx} sx={{ p: 1.5, border: '1px solid', borderColor: 'divider', borderRadius: 1.5 }}>
                            <Typography variant="subtitle2" sx={{ fontWeight: 700, mb: 1 }}>
                              {`Strategy ${idx + 1}: ${strategy.name}`}
                            </Typography>
                            <Box component="ul" sx={{ pl: 2.5, m: 0, mb: 1 }}>
                              {(strategy.description || []).map((item, itemIdx) => (
                                <Typography key={itemIdx} component="li" variant="body2" sx={{ lineHeight: 1.6, mb: 0.6 }}>
                                  {item}
                                </Typography>
                              ))}
                            </Box>
                            <Typography variant="body2" sx={{ fontWeight: 600, mb: 0.5 }}>
                              Examples:
                            </Typography>
                            <Box component="ul" sx={{ pl: 2.5, m: 0, mb: 1 }}>
                              {(strategy.examples || []).map((example, exampleIdx) => (
                                <Typography key={exampleIdx} component="li" variant="body2" sx={{ lineHeight: 1.6, mb: 0.4 }}>
                                  {example}
                                </Typography>
                              ))}
                            </Box>
                            <Typography variant="body2" sx={{ mb: 0.5 }}>
                              <strong>Routine:</strong> {strategy.routine}
                            </Typography>
                            <Typography variant="body2" color="text.secondary">
                              <CitedText
                                text={`(Source ${strategy.source})`}
                                onCitationClick={handleCitationClick}
                                highlightMeasurable={false}
                              />
                            </Typography>
                          </Box>
                        ))}
                      </Box>
                    ) : (
                      <Box component="ul" sx={{ pl: 3, m: 0, listStyleType: 'disc' }}>
                        {parseBulletPoints(parsedPlan?.Strategies || '').map((bullet, idx) => (
                          <Typography
                            key={idx}
                            component="li"
                            variant="body2"
                            sx={{ lineHeight: 1.7, mb: 1.5, display: 'list-item' }}
                          >
                            <CitedText
                              text={bullet}
                              onCitationClick={handleCitationClick}
                              highlightMeasurable={true}
                            />
                          </Typography>
                        ))}
                      </Box>
                    )}

                    <SectionEvidencePanel
                      citationIds={strategyCitationIds}
                      sources={sources}
                      onSourceClick={handleSourceClick}
                    />
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
                        fontSize: '1rem',
                        mb: 1.5,
                        color: 'primary.main',
                      }}
                    >
                      💡 Advice for Parents
                    </Typography>
                    <Box component="ul" sx={{ pl: 3, m: 0, listStyleType: 'disc' }}>
                      {(isStructuredPlan
                        ? (plan.advice || []).map((item) => `${item.text} (Source ${item.source})`)
                        : parseBulletPoints(parsedPlan?.['Advice for Parents'] || parsedPlan?.Advice_for_Parents || '')
                      ).map((bullet, idx) => (
                        <Typography
                          key={idx}
                          component="li"
                          variant="body2"
                          sx={{ lineHeight: 1.7, mb: 1.5, display: 'list-item' }}
                        >
                          <CitedText
                            text={bullet}
                            onCitationClick={handleCitationClick}
                            highlightMeasurable={true}
                          />
                        </Typography>
                      ))}
                    </Box>

                    <SectionEvidencePanel
                      citationIds={adviceCitationIds}
                      sources={sources}
                      onSourceClick={handleSourceClick}
                    />
                  </CardContent>
                </Card>

                {/* Sources Section (if present) */}
                {(isStructuredPlan ? sources.length > 0 : parsedPlan?.Sources) && (
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
                          fontSize: '1rem',
                          mb: 1.5,
                          color: 'primary.main',
                        }}
                      >
                        📚 Sources
                      </Typography>
                      {isStructuredPlan ? (
                        <Box sx={{ display: 'flex', flexDirection: 'column', gap: 1.25 }}>
                          {sources.map((source) => (
                            <Box key={source.id}>
                              <Typography variant="body2" sx={{ fontWeight: 600, color: 'text.primary' }}>
                                {`- Source ${source.id}: ${source.title}`}
                              </Typography>
                              {source.excerpt && (
                                <Typography variant="body2" sx={{ pl: 2, color: 'text.secondary', fontStyle: 'italic' }}>
                                  {`"${source.excerpt}"`}
                                </Typography>
                              )}
                            </Box>
                          ))}
                        </Box>
                      ) : (
                        <Typography
                          variant="body2"
                          sx={{
                            lineHeight: 1.7,
                            whiteSpace: 'pre-wrap',
                            fontSize: '0.85rem',
                            color: 'text.secondary',
                          }}
                        >
                          {parsedPlan.Sources}
                        </Typography>
                      )}
                    </CardContent>
                  </Card>
                )}
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
                      width: '100%',
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
                      {msg.role === 'user' ? (
                        <Typography
                          variant="body2"
                          sx={{
                            whiteSpace: 'pre-wrap',
                            lineHeight: 1.6,
                            wordBreak: 'break-word',
                          }}
                        >
                          {msg.content}
                        </Typography>
                      ) : (
                        <Box>
                          {renderChatMessage(msg.content, handleCitationClick)}
                        </Box>
                      )}
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

        {/* Evidence Drawer for Source Details */}
        <EvidenceDrawer
          open={drawerOpen}
          onClose={() => setDrawerOpen(false)}
          source={selectedSource}
        />
      </Box>
    </Box>
  );
}

export default RightPane;
