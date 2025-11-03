# Lazy Loading Implementation

## Overview
Implemented infinite scroll/lazy loading for both conversations and messages to improve performance and user experience.

## Backend Changes

### 1. Conversation API (`backend/api/routers/conversation.py`)
- ✅ Added `skip` and `limit` parameters to `/conversations/user/{user_id}` endpoint
- ✅ Default: `limit=20` conversations per page

### 2. Conversation Service (`backend/api/services/conversation.py`)
- ✅ Updated `get_conversations_by_user_id()` to accept pagination parameters
- ✅ Pass `skip` and `limit` to repository layer

### 3. Conversation Repository (`backend/api/repositories/conversation.py`)
- ✅ Updated `get_conversation_by_user_id()` with pagination
- ✅ Added `.order_by(Conversation.created_at.desc())` for newest first
- ✅ Added `.offset(skip).limit(limit)` for pagination

### 4. Message API (`backend/api/routers/message.py`)
- ✅ Already had pagination support with `skip` and `limit` parameters
- ✅ Default: `limit=100` (kept existing implementation)

## Frontend Changes

### 1. Conversation API (`hackathon_fe/app/api/conversationApi.ts`)
- ✅ Updated `getByUserId()` to accept `skip` and `limit` parameters
- ✅ Default: `skip=0, limit=20`

### 2. Message API (`hackathon_fe/app/api/messageApi.ts`)
- ✅ Updated `getByConversationId()` to accept `skip` and `limit` parameters
- ✅ Default: `skip=0, limit=50`

### 3. ChatSidebar Component (`hackathon_fe/app/components/chat/ChatSidebar.tsx`)
- ✅ Added infinite scroll for conversations
- ✅ Implemented Intersection Observer for scroll detection
- ✅ State management:
  - `hasMore`: Track if more conversations available
  - `page`: Current page number
  - `loadingConversations`: Loading state
- ✅ `lastConversationRef`: Ref callback for last conversation element
- ✅ Loads 20 conversations per page
- ✅ Auto-loads next page when scrolling to bottom
- ✅ Shows loading spinner while fetching
- ✅ Fixed duplicate conversation handling

### 4. ChatMessageList Component (`hackathon_fe/app/components/chat/ChatMessageList.tsx`)
- ✅ Added infinite scroll for messages
- ✅ Implemented Intersection Observer for top scroll detection
- ✅ New props:
  - `loadingMore`: Loading state for pagination
  - `hasMore`: Track if more messages available
  - `onLoadMore`: Callback to load more messages
- ✅ `topSentinelRef`: Sentinel element at top for scroll detection
- ✅ Shows loading spinner when fetching older messages
- ✅ Loads 50 messages per page

### 5. ChatLayout Component (`hackathon_fe/app/components/chat/ChatLayout.tsx`)
- ✅ Added message pagination state:
  - `hasMoreMessages`: Track if more messages available
  - `loadingMessages`: Loading state
  - `messagePage`: Current page number
  - `MESSAGES_PER_PAGE = 50`
- ✅ Implemented `loadMoreMessages()` callback
- ✅ Messages loaded in reverse order (oldest first)
- ✅ Prepends older messages to beginning of list
- ✅ Resets pagination when switching conversations
- ✅ Passes pagination props to ChatMessageList

## How It Works

### Conversations (Sidebar)
1. Initially loads 20 conversations
2. User scrolls down in sidebar
3. When last conversation becomes visible (Intersection Observer)
4. Automatically fetches next 20 conversations
5. Appends to existing list
6. Continues until no more conversations

### Messages (Chat)
1. Initially loads 50 most recent messages
2. User scrolls up to see older messages
3. When top sentinel becomes visible (Intersection Observer)
4. Automatically fetches next 50 older messages
5. Prepends to beginning of list
6. Maintains scroll position
7. Continues until no more messages

## Benefits

- ✅ **Performance**: Only loads data when needed
- ✅ **UX**: Smooth infinite scroll experience
- ✅ **Scalability**: Handles large conversations/message lists
- ✅ **Network**: Reduces initial load time and bandwidth
- ✅ **Memory**: Lower memory footprint
- ✅ **Responsive**: Loading indicators show fetch progress

## Configuration

### Backend
- Conversations per page: 20 (configurable in router)
- Messages per page: 50-100 (configurable in router)

### Frontend
- Conversations per page: 20 (`ITEMS_PER_PAGE` in ChatSidebar)
- Messages per page: 50 (`MESSAGES_PER_PAGE` in ChatLayout)

## Testing

### Test Conversations Lazy Loading
1. Create 30+ conversations
2. Open sidebar
3. Scroll down
4. Verify automatic loading of more conversations
5. Check loading spinner appears

### Test Messages Lazy Loading
1. Open conversation with 100+ messages
2. Scroll to top
3. Verify automatic loading of older messages
4. Check loading spinner at top
5. Verify scroll position maintained

## Future Improvements

- [ ] Virtual scrolling for thousands of items
- [ ] Prefetch next page in background
- [ ] Cache loaded pages in memory
- [ ] Add "Load More" button as fallback
- [ ] Bidirectional infinite scroll for messages
- [ ] Skeleton loaders instead of spinners
