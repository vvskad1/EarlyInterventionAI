/**
 * API Helper Functions
 * Handles all communication with the FastAPI backend
 */

const API_BASE_URL = 'http://localhost:8081';

/**
 * Upload knowledge base file (.txt or .md)
 * @param {File} file - The file to upload
 * @returns {Promise<Object>} Response with ok status and kb_file path
 */
export async function uploadKB(file) {
  const formData = new FormData();
  formData.append('file', file);

  const response = await fetch(`${API_BASE_URL}/api/rag/upload`, {
    method: 'POST',
    body: formData,
  });

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || 'Failed to upload knowledge base');
  }

  return response.json();
}

/**
 * Generate intervention plan
 * @param {Object} data - Plan request data
 * @param {number} data.age_months - Child's age in months (0-36)
 * @param {string[]} data.domains - Array of development domains
 * @param {string} data.notes - Additional notes about the child (optional)
 * @param {string} data.extra_info - Additional context (optional)
 * @returns {Promise<Object>} Response with Goals, Strategies, and Advice for Parents
 */
export async function generatePlan(data) {
  const response = await fetch(`${API_BASE_URL}/api/plan`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(data),
  });

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || 'Failed to generate plan');
  }

  return response.json();
}

/**
 * Send chat message
 * @param {string} message - User's message
 * @param {string|null} sessionId - Session ID for conversation continuity (optional)
 * @param {Object} extras - Additional context (optional)
 * @param {number} extras.age_months - Child's age in months
 * @param {string[]} extras.domains - Array of development domains
 * @param {string} extras.notes - Notes about the child
 * @returns {Promise<Object>} Response with AI response and session_id
 */
export async function sendChat(message, sessionId = null, extras = {}) {
  const body = {
    message,
    ...(sessionId && { session_id: sessionId }),
    ...extras,
  };

  const response = await fetch(`${API_BASE_URL}/api/chat`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(body),
  });

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || 'Failed to send chat message');
  }

  return response.json();
}
