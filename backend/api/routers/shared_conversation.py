from fastapi import APIRouter, HTTPException, status, Query
from typing import List, Optional

from api.services.shared_conversation import SharedConversationService
from api.core import schemas


router = APIRouter(
    prefix="/shared-conversations",
    tags=["shared_conversation"],
)

@router.post("/", response_model=schemas.SharedConversation, status_code=status.HTTP_201_CREATED)
def create_shared_conversation(
        conversation_id: int,
        user_id: Optional[int] = None,
        column: Optional[int] = None
):
    """Tạo mới shared conversation"""
    service = SharedConversationService()
    try:
        shared_conv = service.create_shared_conversation(
            conversation_id=conversation_id,
            user_id=user_id,
            column=column
        )
        return shared_conv
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error creating shared conversation: {str(e)}"
        )


@router.get("/{shared_conv_id}", response_model=schemas.SharedConversation)
def get_shared_conversation(shared_conv_id: int):
    """Lấy shared conversation theo ID"""
    service = SharedConversationService()
    shared_conv = service.get_shared_conversation(shared_conv_id)
    
    if not shared_conv:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Shared conversation not found"
        )
    
    return shared_conv

@router.get("/", response_model=List[schemas.SharedConversation])
def get_all_shared_conversations(
        skip: int = Query(0, ge=0),
        limit: int = Query(100, ge=1, le=1000)
):
    """Lấy tất cả shared conversations (phân trang)"""
    service = SharedConversationService()
    return service.get_all_shared_conversations(skip=skip, limit=limit)


@router.get("/conversation/{conversation_id}", response_model=List[schemas.SharedConversation])
def get_shared_conversations_by_conversation(conversation_id: int):
    """Lấy shared conversations theo conversation_id"""
    service = SharedConversationService()
    shared_convs = service.get_shared_conversations_by_conversation(conversation_id)
    
    if not shared_convs:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No shared conversations found for this conversation"
        )
    
    return shared_convs


@router.get("/user/{user_id}", response_model=List[schemas.SharedConversation])
def get_shared_conversations_by_user(user_id: int):
    """Lấy shared conversations theo user_id"""
    service = SharedConversationService()
    shared_convs = service.get_shared_conversations_by_user(user_id)
    
    if not shared_convs:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No shared conversations found for this user"
        )
    
    return shared_convs


@router.put("/{shared_conv_id}", response_model=schemas.SharedConversation)
def update_shared_conversation(
        shared_conv_id: int,
        user_id: Optional[int] = None,
        column: Optional[int] = None
):
    """Cập nhật shared conversation"""
    service = SharedConversationService()
    
    update_data = {}
    if user_id is not None:
        update_data['user_id'] = user_id
    if column is not None:
        update_data['column'] = column
    
    shared_conv = service.update_shared_conversation(shared_conv_id, **update_data)
    
    if not shared_conv:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Shared conversation not found"
        )
    
    return shared_conv


@router.delete("/{shared_conv_id}", status_code=status.HTTP_200_OK)
def delete_shared_conversation(shared_conv_id: int):
    """Xóa shared conversation (soft delete)"""
    service = SharedConversationService()
    success = service.delete_shared_conversation(shared_conv_id)
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Shared conversation not found"
        )
    
    return {"message": "Shared conversation deleted successfully"}


@router.delete("/conversation/{conversation_id}", status_code=status.HTTP_200_OK)
def delete_shared_conversations_by_conversation(conversation_id: int):
    """Xóa tất cả shared conversations của conversation"""
    service = SharedConversationService()
    success = service.delete_shared_conversations_by_conversation(conversation_id)
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No shared conversations found for this conversation"
        )
    
    return {"message": "All shared conversations for this conversation deleted successfully"}


@router.post("/share/{conversation_id}/to/{user_id}", response_model=schemas.SharedConversation)
def share_conversation_to_user(conversation_id: int, user_id: int):
    """Chia sẻ conversation đến user cụ thể"""
    service = SharedConversationService()
    shared_conv = service.share_conversation_to_user(conversation_id, user_id)
    
    if not shared_conv:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to share conversation"
        )
    
    return shared_conv