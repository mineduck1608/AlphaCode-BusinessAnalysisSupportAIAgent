export type Conversation = {
    id: string
    name: string
    user_id: string
    created_at: string
    last_updated: string
    status: number
    is_shared: boolean
    summary?: string
    summary_embedding: Float16Array
    share_token: string 
}