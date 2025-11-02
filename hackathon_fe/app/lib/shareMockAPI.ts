/**
 * Mock API for Share Conversation Feature
 */

export type ShareableConversation = {
  id: string;
  name: string;
  session: string;
  created_at: string;
  last_updated: string;
  is_shared: boolean;
  share_url?: string;
  message_count: number;
};

export type SharedLink = {
  id: string;
  conversation_id: string;
  share_url: string;
  created_at: string;
  expires_at?: string;
  view_count: number;
};

// Mock data
const mockConversations: ShareableConversation[] = [
  {
    id: "conv-1",
    name: "Project ideas discussion",
    session: "sess-abc123",
    created_at: new Date().toISOString(),
    last_updated: new Date().toISOString(),
    is_shared: false,
    message_count: 15,
  },
  {
    id: "conv-2",
    name: "Study notes - React Hooks",
    session: "sess-def456",
    created_at: new Date(Date.now() - 86400000).toISOString(),
    last_updated: new Date(Date.now() - 3600000).toISOString(),
    is_shared: true,
    share_url: "https://alphacode.app/share/abc123xyz",
    message_count: 28,
  },
];

const mockSharedLinks: SharedLink[] = [];

/**
 * Generate share link for a conversation
 */
export const generateShareLink = async (
  conversationId: string
): Promise<SharedLink> => {
  // Simulate API delay
  await new Promise((resolve) => setTimeout(resolve, 500));

  const conversation = mockConversations.find((c) => c.id === conversationId);
  if (!conversation) {
    throw new Error("Conversation not found");
  }

  const shareLink: SharedLink = {
    id: `share-${Date.now()}`,
    conversation_id: conversationId,
    share_url: `https://alphacode.app/share/${Math.random()
      .toString(36)
      .substring(7)}`,
    created_at: new Date().toISOString(),
    expires_at: new Date(Date.now() + 30 * 24 * 60 * 60 * 1000).toISOString(), // 30 days
    view_count: 0,
  };

  mockSharedLinks.push(shareLink);
  conversation.is_shared = true;
  conversation.share_url = shareLink.share_url;

  return shareLink;
};

/**
 * Revoke share link
 */
export const revokeShareLink = async (
  conversationId: string
): Promise<boolean> => {
  await new Promise((resolve) => setTimeout(resolve, 300));

  const conversation = mockConversations.find((c) => c.id === conversationId);
  if (!conversation) {
    throw new Error("Conversation not found");
  }

  conversation.is_shared = false;
  conversation.share_url = undefined;

  const linkIndex = mockSharedLinks.findIndex(
    (l) => l.conversation_id === conversationId
  );
  if (linkIndex !== -1) {
    mockSharedLinks.splice(linkIndex, 1);
  }

  return true;
};

/**
 * Get shared conversations
 */
export const getSharedConversations = async (): Promise<
  ShareableConversation[]
> => {
  await new Promise((resolve) => setTimeout(resolve, 300));
  return mockConversations.filter((c) => c.is_shared);
};

/**
 * Get all conversations (for share dialog)
 */
export const getAllConversations = async (): Promise<
  ShareableConversation[]
> => {
  await new Promise((resolve) => setTimeout(resolve, 300));
  return mockConversations;
};

/**
 * Copy to clipboard utility
 */
export const copyToClipboard = async (text: string): Promise<boolean> => {
  try {
    await navigator.clipboard.writeText(text);
    return true;
  } catch (error) {
    console.error("Failed to copy to clipboard:", error);
    return false;
  }
};
