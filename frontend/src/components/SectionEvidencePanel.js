import React, { useState } from 'react';
import {
    Box,
    Button,
    Collapse,
    Typography,
    List,
    ListItem,
    ListItemButton,
    ListItemText,
    Chip,
} from '@mui/material';
import { ExpandMore, ExpandLess, LibraryBooks } from '@mui/icons-material';

/**
 * SectionEvidencePanel Component
 * Collapsible panel showing sources referenced in a section
 */
function SectionEvidencePanel({ citationIds, sources, onSourceClick }) {
    const [expanded, setExpanded] = useState(false);

    if (!citationIds || citationIds.length === 0) {
        return null;
    }

    const referencedSources = sources.filter(s => citationIds.includes(s.id));

    return (
        <Box sx={{ mt: 2 }}>
            <Button
                onClick={() => setExpanded(!expanded)}
                size="small"
                startIcon={<LibraryBooks />}
                endIcon={expanded ? <ExpandLess /> : <ExpandMore />}
                sx={{
                    textTransform: 'none',
                    color: 'primary.main',
                    fontWeight: 500,
                    fontSize: '0.813rem',
                }}
                aria-expanded={expanded}
                aria-controls="evidence-panel"
            >
                View Supporting Evidence ({citationIds.length} source{citationIds.length > 1 ? 's' : ''})
            </Button>

            <Collapse in={expanded} timeout="auto" unmountOnExit>
                <Box
                    id="evidence-panel"
                    sx={{
                        mt: 1.5,
                        p: 2,
                        bgcolor: 'action.hover',
                        borderRadius: 1,
                        border: 1,
                        borderColor: 'divider',
                    }}
                >
                    <Typography
                        variant="caption"
                        sx={{
                            fontWeight: 600,
                            textTransform: 'uppercase',
                            letterSpacing: '0.5px',
                            color: 'text.secondary',
                            display: 'block',
                            mb: 1,
                        }}
                    >
                        Sources Referenced in This Section
                    </Typography>

                    <List dense disablePadding>
                        {referencedSources.map((source) => (
                            <ListItem
                                key={source.id}
                                disablePadding
                                sx={{ mb: 0.5 }}
                            >
                                <ListItemButton
                                    onClick={() => onSourceClick(source)}
                                    sx={{
                                        borderRadius: 1,
                                        py: 1,
                                        '&:hover': {
                                            bgcolor: 'action.selected',
                                        },
                                    }}
                                    aria-label={`View details for source ${source.id}: ${source.title}`}
                                >
                                    <Chip
                                        label={source.id}
                                        size="small"
                                        sx={{
                                            mr: 1.5,
                                            minWidth: 32,
                                            height: 24,
                                            fontSize: '0.75rem',
                                            fontWeight: 600,
                                        }}
                                        color="primary"
                                        variant="outlined"
                                    />
                                    <ListItemText
                                        primary={source.title}
                                        secondary={source.year}
                                        primaryTypographyProps={{
                                            variant: 'body2',
                                            sx: { fontWeight: 500, fontSize: '0.875rem' },
                                        }}
                                        secondaryTypographyProps={{
                                            variant: 'caption',
                                            sx: { fontSize: '0.75rem' },
                                        }}
                                    />
                                </ListItemButton>
                            </ListItem>
                        ))}
                    </List>

                    {referencedSources.length === 0 && (
                        <Typography variant="body2" color="text.secondary" sx={{ py: 1 }}>
                            No matching sources found.
                        </Typography>
                    )}
                </Box>
            </Collapse>
        </Box>
    );
}

export default SectionEvidencePanel;
