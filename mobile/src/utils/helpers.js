/**
 * Utility functions
 */

import uuid from 'react-native-uuid';

/**
 * Generate UUID
 */
export const generateUUID = () => {
    return uuid.v4();
};

/**
 * Format date for display
 */
export const formatDate = (date) => {
    const d = new Date(date);
    return d.toLocaleDateString('en-US', {
        month: 'short',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
    });
};

/**
 * Format domain name for display
 */
export const formatDomain = (domain) => {
    return domain
        .replace('_', ' ')
        .replace(/\b\w/g, l => l.toUpperCase());
};

/**
 * Validate age input
 */
export const validateAge = (age) => {
    const numAge = parseInt(age, 10);
    if (isNaN(numAge) || numAge < 0 || numAge > 36) {
        return null;
    }
    return numAge;
};

/**
 * Create new chat object
 */
export const createNewChat = () => {
    return {
        id: generateUUID(),
        title: 'New Chat',
        age_months: null,
        domains: [],
        notes: '',
        plan: null,
        messages: [],
        createdAt: new Date().toISOString(),
        updatedAt: new Date().toISOString(),
    };
};

/**
 * Update chat timestamp
 */
export const updateChatTimestamp = (chat) => {
    return {
        ...chat,
        updatedAt: new Date().toISOString(),
    };
};
