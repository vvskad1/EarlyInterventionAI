/**
 * Storage Service for persisting chat data
 */

import AsyncStorage from '@react-native-async-storage/async-storage';

const STORAGE_KEYS = {
    CHATS: '@ei_chats',
    THEME: '@ei_theme',
};

const MAX_CHATS = 25;

/**
 * Get all chats
 */
export const getChats = async () => {
    try {
        const chatsJson = await AsyncStorage.getItem(STORAGE_KEYS.CHATS);
        return chatsJson ? JSON.parse(chatsJson) : [];
    } catch (error) {
        console.error('Error loading chats:', error);
        return [];
    }
};

/**
 * Save all chats
 */
export const saveChats = async (chats) => {
    try {
        // Limit to MAX_CHATS
        const limitedChats = chats.slice(0, MAX_CHATS);
        await AsyncStorage.setItem(STORAGE_KEYS.CHATS, JSON.stringify(limitedChats));
        return true;
    } catch (error) {
        console.error('Error saving chats:', error);
        return false;
    }
};

/**
 * Add or update a chat
 */
export const saveChat = async (chat) => {
    try {
        const chats = await getChats();
        const existingIndex = chats.findIndex(c => c.id === chat.id);

        if (existingIndex >= 0) {
            chats[existingIndex] = chat;
        } else {
            chats.unshift(chat); // Add to beginning
        }

        await saveChats(chats);
        return true;
    } catch (error) {
        console.error('Error saving chat:', error);
        return false;
    }
};

/**
 * Delete a chat
 */
export const deleteChat = async (chatId) => {
    try {
        const chats = await getChats();
        const filtered = chats.filter(c => c.id !== chatId);
        await saveChats(filtered);
        return true;
    } catch (error) {
        console.error('Error deleting chat:', error);
        return false;
    }
};

/**
 * Clear all chats
 */
export const clearAllChats = async () => {
    try {
        await AsyncStorage.removeItem(STORAGE_KEYS.CHATS);
        return true;
    } catch (error) {
        console.error('Error clearing chats:', error);
        return false;
    }
};

/**
 * Get theme preference
 */
export const getTheme = async () => {
    try {
        const theme = await AsyncStorage.getItem(STORAGE_KEYS.THEME);
        return theme || 'light';
    } catch (error) {
        console.error('Error loading theme:', error);
        return 'light';
    }
};

/**
 * Save theme preference
 */
export const saveTheme = async (theme) => {
    try {
        await AsyncStorage.setItem(STORAGE_KEYS.THEME, theme);
        return true;
    } catch (error) {
        console.error('Error saving theme:', error);
        return false;
    }
};
