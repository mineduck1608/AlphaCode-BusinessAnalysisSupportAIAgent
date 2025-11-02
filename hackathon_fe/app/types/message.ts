export type Message = {
    id: string
    shared_conversation_id: string
    conversation_id: string
    user_id: string
    agent_id: string
    role: number
    reaction: string
    created_at: string
    last_updated: string
    status: number
    content: string
    content_type: number
    message_type: number
}
