/**
 * Application Constants
 */

// WebSocket Configuration
export const WS_CONFIG = {
  BASE_URL: 'wss://9e24ba431b7d.ngrok-free.app',
  CHAT_ENDPOINT: '/ws/chat',
  AUTO_RECONNECT: true,
  RECONNECT_INTERVAL: 3000,
  MAX_RECONNECT_ATTEMPTS: 5,
} as const;

// Get full WebSocket URL
export const getWebSocketUrl = (endpoint: string = WS_CONFIG.CHAT_ENDPOINT) => {
  return `${WS_CONFIG.BASE_URL}${endpoint}`;
};

// Storage Keys
export const STORAGE_KEYS = {
  CHAT_HISTORY: 'chatgpt_clone_history_v1',
  USER_PREFERENCES: 'user_preferences',
} as const;

// UI Constants
export const UI_CONFIG = {
  MESSAGE_SCROLL_BEHAVIOR: 'smooth',
  DEFAULT_GREETING: 'Hi there 👋 How can I help you today?',
} as const;
