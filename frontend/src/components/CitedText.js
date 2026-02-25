import React from 'react';
import { Box, Link } from '@mui/material';
import { formatCitations, highlightMeasurables } from '../utils/citationUtils';

/**
 * CitedText Component
 * Renders text with clickable citation superscripts and highlighted measurables
 */
function CitedText({ text, onCitationClick, highlightMeasurable = true }) {
    if (!text) return null;

    // Apply measurable highlighting first
    let processedText = highlightMeasurable ? highlightMeasurables(text) : text;

    // Parse citations
    const parts = formatCitations(processedText, onCitationClick);

    if (!Array.isArray(parts)) {
        // No citations found, render with HTML for measurables
        return (
            <Box
                component="span"
                dangerouslySetInnerHTML={{ __html: processedText }}
                sx={{ display: 'inline' }}
            />
        );
    }

    // Render mixed content with citations
    return (
        <Box component="span" sx={{ display: 'inline' }}>
            {parts.map((part, index) => {
                if (typeof part === 'string') {
                    // Plain text or text with <strong> tags
                    return (
                        <span
                            key={index}
                            dangerouslySetInnerHTML={{ __html: part }}
                        />
                    );
                } else if (part.type === 'citation') {
                    // Render clickable citation(s)
                    return (
                        <sup key={index} style={{ marginLeft: '2px' }}>
                            {part.sourceIds.map((sourceId, i) => (
                                <React.Fragment key={sourceId}>
                                    {i > 0 && ','}
                                    <Link
                                        component="button"
                                        onClick={(e) => {
                                            e.preventDefault();
                                            e.stopPropagation();
                                            onCitationClick(sourceId);
                                        }}
                                        sx={{
                                            fontSize: '0.75em',
                                            fontWeight: 600,
                                            textDecoration: 'none',
                                            color: 'primary.main',
                                            cursor: 'pointer',
                                            '&:hover': {
                                                textDecoration: 'underline',
                                            },
                                            '&:focus': {
                                                outline: '2px solid',
                                                outlineColor: 'primary.main',
                                                outlineOffset: '2px',
                                                borderRadius: '2px',
                                            },
                                        }}
                                        aria-label={`View source ${sourceId}`}
                                        tabIndex={0}
                                    >
                                        [{sourceId}]
                                    </Link>
                                </React.Fragment>
                            ))}
                        </sup>
                    );
                }
                return null;
            })}
        </Box>
    );
}

export default CitedText;
