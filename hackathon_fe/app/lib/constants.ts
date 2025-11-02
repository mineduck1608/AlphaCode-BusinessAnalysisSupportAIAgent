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
  DEFAULT_GREETING: `👋 Chào mừng đến với Requirements Engineering Assistant!

Tôi sẽ giúp bạn phân tích và quản lý requirements từ các nguồn đầu vào khác nhau.

📝 Để bắt đầu, hãy nhập user stories hoặc requirements của bạn. Bạn có thể:
• Dán nhiều stories cùng lúc (sử dụng "Story:" để phân tách)
• Upload file SRS hoặc document
• Nhập trực tiếp requirements

💡 Ví dụ input mẫu:
Story: Export Analytics Report
As a user, I want to quickly export analytics data to a CSV report that loads fast.
Acceptance Criteria:
- Report is downloadable
- Contains user activity metrics

Story: Admin Report Access
As an admin, I want to see all user reports.
Acceptance Criteria:
- View list of all reports
- Access sensitive data

Tôi sẽ tự động phân tích, phát hiện vấn đề, ưu tiên hóa và tạo báo cáo cho bạn!`,
} as const;
