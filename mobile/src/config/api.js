/**
 * API Configuration
 * Update this URL to point to your deployed backend
 */

// For local development (Android emulator)
// export const API_BASE_URL = 'http://10.0.2.2:8081';

// For local development (physical device - use your computer's IP)
// export const API_BASE_URL = 'http://192.168.1.100:8081';

// For production
// export const API_BASE_URL = 'https://your-backend-url.com';

export const API_ENDPOINTS = {
    GENERATE_PLAN: '/api/plan',
    SEND_CHAT: '/api/chat',
    HEALTH: '/health',
};
export const API_BASE_URL = 'http://10.0.2.2:8081'; // Emulator