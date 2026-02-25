/**
 * Citation and Evidence Display Utilities
 */

/**
 * Parse sources section into structured array
 * Format: 
 * - Source 1: [Title]
 *   > "excerpt text"
 */
export function parseSources(sourcesText) {
    if (!sourcesText) return [];

    const lines = sourcesText.split('\n');
    const sources = [];
    let currentSource = null;

    lines.forEach(line => {
        const trimmed = line.trim();

        // Check if line is a source title
        const sourceMatch = trimmed.match(/^-?\s*Source\s+(\d+):\s*(.+)$/i);
        if (sourceMatch) {
            // Save previous source if exists
            if (currentSource) {
                sources.push(currentSource);
            }

            const id = parseInt(sourceMatch[1]);
            const title = sourceMatch[2].trim();

            // Try to extract author/year from title
            const authorYearMatch = title.match(/^(.*?),?\s*(\d{4})$/);

            currentSource = {
                id,
                title: authorYearMatch ? authorYearMatch[1] : title,
                authors: title, // Use full title as authors
                year: authorYearMatch ? authorYearMatch[2] : '',
                excerpt: '',
                link: ''
            };
        }
        // Check if line is an excerpt (blockquote)
        else if (trimmed.match(/^>\s*"(.+)"$/)) {
            const excerptMatch = trimmed.match(/^>\s*"(.+)"$/);
            if (excerptMatch && currentSource) {
                currentSource.excerpt = excerptMatch[1];
            }
        }
    });

    // Add last source
    if (currentSource) {
        sources.push(currentSource);
    }

    return sources;
}

/**
 * Extract citation numbers from text
 * Returns array of source IDs referenced
 */
export function extractCitations(text) {
    if (!text) return [];

    const citations = new Set();
    const regex = /\(Source\s+(\d+)(?:,\s*Source\s+(\d+))*\)/gi;

    let match;
    while ((match = regex.exec(text)) !== null) {
        // Get first source number
        citations.add(parseInt(match[1]));

        // Check for additional sources in same citation
        const multiMatch = match[0].match(/Source\s+(\d+)/gi);
        multiMatch.forEach(m => {
            const num = parseInt(m.match(/\d+/)[0]);
            citations.add(num);
        });
    }

    return Array.from(citations).sort((a, b) => a - b);
}

/**
 * Convert "(Source X)" citations to clickable superscript
 * Returns React elements
 */
export function formatCitations(text, onCitationClick) {
    if (!text) return null;

    const parts = [];
    let lastIndex = 0;
    const regex = /\(Source\s+(\d+)(?:,\s*Source\s+(\d+))*\)/gi;

    let match;
    while ((match = regex.exec(text)) !== null) {
        // Add text before citation
        if (match.index > lastIndex) {
            parts.push(text.substring(lastIndex, match.index));
        }

        // Extract all source numbers from this citation
        const sourceNums = [];
        const multiMatch = match[0].match(/Source\s+(\d+)/gi);
        multiMatch.forEach(m => {
            sourceNums.push(parseInt(m.match(/\d+/)[0]));
        });

        // Create superscript citation links
        parts.push({
            type: 'citation',
            sourceIds: sourceNums,
            originalText: match[0]
        });

        lastIndex = regex.lastIndex;
    }

    // Add remaining text
    if (lastIndex < text.length) {
        parts.push(text.substring(lastIndex));
    }

    return parts;
}

/**
 * Highlight measurable elements in text
 * Bolds durations, frequencies, timeframes
 */
export function highlightMeasurables(text) {
    if (!text) return text;

    const patterns = [
        // Durations: "10 seconds", "5 minutes"
        /(\d+\s+(?:second|minute|hour)s?)/gi,
        // Frequencies: "3 out of 5", "4/5"
        /(\d+\s+(?:out of|of|\/)\s+\d+(?:\s+(?:trial|opportunit|attempt|time)s?)?)/gi,
        // Timeframes: "2 consecutive weeks", "1 week"
        /(\d+\s+(?:consecutive\s+)?(?:week|day|month)s?)/gi,
    ];

    let result = text;
    patterns.forEach(pattern => {
        result = result.replace(pattern, '<strong>$1</strong>');
    });

    return result;
}

/**
 * Calculate evidence confidence level
 * Based on citation count and distribution
 */
export function calculateConfidence(sections, sources) {
    const totalCitations = Object.values(sections).reduce((sum, section) => {
        return sum + extractCitations(section).length;
    }, 0);

    const uniqueSources = new Set();
    Object.values(sections).forEach(section => {
        extractCitations(section).forEach(id => uniqueSources.add(id));
    });

    const availableSources = sources.length;
    const usedSources = uniqueSources.size;

    if (usedSources >= availableSources * 0.8 && totalCitations >= 5) {
        return { level: 'high', label: 'Evidence Grounded', color: 'success' };
    } else if (totalCitations >= 3) {
        return { level: 'medium', label: 'Partial Evidence', color: 'warning' };
    } else {
        return { level: 'low', label: 'Limited Evidence', color: 'error' };
    }
}

/**
 * Parse bullet points from markdown text
 * Returns array of bullet content strings
 */
export function parseBulletPoints(text) {
    if (!text) return [];

    const lines = text.split('\n');
    const bullets = [];
    let currentBullet = '';

    lines.forEach(line => {
        const trimmed = line.trim();

        // Check if line starts with bullet marker
        if (trimmed.match(/^[*\-•]\s+/)) {
            // Save previous bullet if exists
            if (currentBullet) {
                bullets.push(currentBullet.trim());
            }
            // Start new bullet (remove marker)
            currentBullet = trimmed.replace(/^[*\-•]\s*/, '');
        } else if (currentBullet && trimmed) {
            // Continue current bullet (multi-line support)
            currentBullet += ' ' + trimmed;
        }
    });

    // Add last bullet
    if (currentBullet) {
        bullets.push(currentBullet.trim());
    }

    return bullets.filter(Boolean);
}
