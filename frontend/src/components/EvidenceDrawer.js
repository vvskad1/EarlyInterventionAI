import React from 'react';
import {
    Drawer,
    Box,
    Typography,
    IconButton,
    Divider,
    Chip,
    Paper,
} from '@mui/material';
import { Close, Article, CalendarToday, Person } from '@mui/icons-material';

/**
 * EvidenceDrawer Component
 * Displays detailed source information and excerpts
 */
function EvidenceDrawer({ open, onClose, source }) {
    if (!source) return null;

    return (
        <Drawer
            anchor="right"
            open={open}
            onClose={onClose}
            sx={{
                '& .MuiDrawer-paper': {
                    width: { xs: '100%', sm: 400 },
                    p: 3,
                },
            }}
            role="complementary"
            aria-label="Evidence details"
        >
            {/* Header */}
            <Box sx={{ display: 'flex', alignItems: 'flex-start', mb: 3 }}>
                <Box sx={{ flex: 1 }}>
                    <Chip
                        label={`Source ${source.id}`}
                        size="small"
                        color="primary"
                        sx={{ mb: 1 }}
                    />
                    <Typography variant="h6" sx={{ fontWeight: 600, lineHeight: 1.3 }}>
                        {source.title}
                    </Typography>
                </Box>
                <IconButton
                    onClick={onClose}
                    size="small"
                    aria-label="Close evidence drawer"
                    sx={{ ml: 1 }}
                >
                    <Close />
                </IconButton>
            </Box>

            <Divider sx={{ mb: 3 }} />

            {/* Metadata */}
            <Box sx={{ mb: 3 }}>
                {source.authors && (
                    <Box sx={{ display: 'flex', alignItems: 'center', mb: 1.5 }}>
                        <Person sx={{ fontSize: 18, mr: 1, color: 'text.secondary' }} />
                        <Typography variant="body2" color="text.secondary">
                            <strong>Authors:</strong> {source.authors}
                        </Typography>
                    </Box>
                )}

                {source.year && (
                    <Box sx={{ display: 'flex', alignItems: 'center', mb: 1.5 }}>
                        <CalendarToday sx={{ fontSize: 18, mr: 1, color: 'text.secondary' }} />
                        <Typography variant="body2" color="text.secondary">
                            <strong>Year:</strong> {source.year}
                        </Typography>
                    </Box>
                )}
            </Box>

            {/* Excerpt */}
            {source.excerpt && (
                <>
                    <Typography
                        variant="subtitle2"
                        sx={{
                            fontWeight: 600,
                            mb: 1.5,
                            textTransform: 'uppercase',
                            fontSize: '0.75rem',
                            letterSpacing: '0.5px',
                        }}
                    >
                        Retrieved Excerpt
                    </Typography>
                    <Paper
                        elevation={0}
                        sx={{
                            p: 2,
                            bgcolor: 'action.hover',
                            borderLeft: 3,
                            borderColor: 'primary.main',
                            mb: 2,
                        }}
                    >
                        <Typography
                            variant="body2"
                            sx={{
                                lineHeight: 1.7,
                                fontStyle: 'italic',
                                color: 'text.primary',
                            }}
                        >
                            "{source.excerpt}"
                        </Typography>
                    </Paper>
                </>
            )}

            {/* Link */}
            {source.link && (
                <Box sx={{ mt: 2 }}>
                    <Typography
                        component="a"
                        href={source.link}
                        target="_blank"
                        rel="noopener noreferrer"
                        sx={{
                            color: 'primary.main',
                            textDecoration: 'none',
                            fontSize: '0.875rem',
                            '&:hover': {
                                textDecoration: 'underline',
                            },
                        }}
                    >
                        View full source →
                    </Typography>
                </Box>
            )}

            {/* Usage Context */}
            <Box sx={{ mt: 4, pt: 3, borderTop: 1, borderColor: 'divider' }}>
                <Typography
                    variant="caption"
                    color="text.secondary"
                    sx={{ display: 'block', lineHeight: 1.5 }}
                >
                    This source was retrieved from the knowledge base and used to ground
                    the recommendations in this intervention plan. All suggestions are
                    evidence-based and aligned with Early Intervention best practices.
                </Typography>
            </Box>
        </Drawer>
    );
}

export default EvidenceDrawer;
