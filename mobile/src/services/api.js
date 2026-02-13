/**
 * API Service for Early Intervention AI
 */

import axios from 'axios';
import { API_BASE_URL, API_ENDPOINTS } from '../config/api';

const api = axios.create({
    baseURL: API_BASE_URL,
    timeout: 60000, // 60 seconds for plan generation
    headers: {
        'Content-Type': 'application/json',
    },
});

/**
 * Generate intervention plan
 */
export const generatePlan = async (planData) => {
    try {
        const response = await api.post(API_ENDPOINTS.GENERATE_PLAN, {
            age_months: planData.ageMonths,
            domains: planData.domains,
            notes: planData.notes,
        });
        return response.data;
    } catch (error) {
        console.error('Generate plan error:', error);
        throw new Error(
            error.response?.data?.detail ||
            'Failed to generate plan. Please check your connection and try again.'
        );
    }
};

/**
 * Send chat message
 */
export const sendChatMessage = async (chatData) => {
    try {
        const response = await api.post(API_ENDPOINTS.SEND_CHAT, {
            age_months: chatData.ageMonths,
            domains: chatData.domains,
            notes: chatData.notes,
            plan: chatData.plan,
            messages: chatData.messages,
        });
        return response.data;
    } catch (error) {
        console.error('Send chat error:', error);
        throw new Error(
            error.response?.data?.detail ||
            'Failed to send message. Please check your connection and try again.'
        );
    }
};

/**
 * Health check
 */
export const checkHealth = async () => {
    try {
        const response = await api.get(API_ENDPOINTS.HEALTH);
        return response.data;
    } catch (error) {
        console.error('Health check error:', error);
        return null;
    }
};

export default api;
