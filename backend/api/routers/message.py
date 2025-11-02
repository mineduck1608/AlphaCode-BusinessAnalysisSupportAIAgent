from fastapi import APIRouter, HTTPException, status, Query
from typing import List, Optional, Dict, Any

from api.services.message import MessageService
from api.core import schemas


router = APIRouter(
    prefix="/messages",
    tags=["message"],
)

@router.post("/", response_model=schemas.Message, status_code=status.HTTP_201_CREATED)
def create_message(
        role: int,
        content: str,
        content_type: int,
        message_type: int,
        conversation_id: Optional[int] = None,
        shared_conversation_id: Optional[int] = None,
        user_id: Optional[int] = None,
        agent_id: Optional[int] = None,
        reaction: Optional[str] = None
):
    """Tạo mới message"""
    service = MessageService()
    try:
        message = service.create_message(
            role=role,
            content=content,
            content_type=content_type,
            message_type=message_type,
            conversation_id=conversation_id,
            shared_conversation_id=shared_conversation_id,
            user_id=user_id,
            agent_id=agent_id,
            reaction=reaction
        )
        return message
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error creating message: {str(e)}"
        )


@router.post("/user", response_model=schemas.Message, status_code=status.HTTP_201_CREATED)
def create_user_message(
        content: str,
        user_id: int,
        conversation_id: int,
        content_type: int = 1,
        message_type: int = 1
):
    """Tạo message từ user"""
    service = MessageService()
    try:
        message = service.create_user_message(
            content=content,
            user_id=user_id,
            conversation_id=conversation_id,
            content_type=content_type,
            message_type=message_type
        )
        return message
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error creating user message: {str(e)}"
        )


@router.post("/agent", response_model=schemas.Message, status_code=status.HTTP_201_CREATED)
def create_agent_message(
        content: str,
        agent_id: int,
        conversation_id: int,
        content_type: int = 1,
        message_type: int = 1
):
    """Tạo message từ agent"""
    service = MessageService()
    try:
        message = service.create_agent_message(
            content=content,
            agent_id=agent_id,
            conversation_id=conversation_id,
            content_type=content_type,
            message_type=message_type
        )
        return message
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error creating agent message: {str(e)}"
        )


@router.get("/{message_id}", response_model=schemas.Message)
def get_message(message_id: int):
    """Lấy message theo ID"""
    service = MessageService()
    message = service.get_message(message_id)
    
    if not message:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Message not found"
        )
    
    return message

@router.get("/", response_model=List[schemas.Message])
def get_all_messages(
        skip: int = Query(0, ge=0),
        limit: int = Query(100, ge=1, le=1000)
):
    """Lấy tất cả messages (phân trang)"""
    service = MessageService()
    return service.get_all_messages(skip=skip, limit=limit)


@router.get("/conversation/{conversation_id}", response_model=List[schemas.Message])
def get_conversation_messages(
        conversation_id: int,
        skip: int = Query(0, ge=0),
        limit: int = Query(100, ge=1, le=1000)
):
    """Lấy messages theo conversation_id"""
    service = MessageService()
    messages = service.get_conversation_messages(conversation_id, skip=skip, limit=limit)
    
    if not messages:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No messages found for this conversation"
        )
    
    return messages


@router.get("/shared-conversation/{shared_conv_id}", response_model=List[schemas.Message])
def get_shared_conversation_messages(
        shared_conv_id: int,
        skip: int = Query(0, ge=0),
        limit: int = Query(100, ge=1, le=1000)
):
    """Lấy messages theo shared_conversation_id"""
    service = MessageService()
    messages = service.get_shared_conversation_messages(shared_conv_id, skip=skip, limit=limit)
    
    if not messages:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No messages found for this shared conversation"
        )
    
    return messages


@router.get("/user/{user_id}", response_model=List[schemas.Message])
def get_user_messages(user_id: int):
    """Lấy messages theo user_id"""
    service = MessageService()
    messages = service.get_user_messages(user_id)
    
    if not messages:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No messages found for this user"
        )
    
    return messages


@router.get("/agent/{agent_id}", response_model=List[schemas.Message])
def get_agent_messages(agent_id: int):
    """Lấy messages theo agent_id"""
    service = MessageService()
    messages = service.get_agent_messages(agent_id)
    
    if not messages:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No messages found for this agent"
        )
    
    return messages


@router.put("/{message_id}", response_model=schemas.Message)
def update_message(
        message_id: int,
        content: Optional[str] = None,
        reaction: Optional[str] = None,
        content_type: Optional[int] = None,
        message_type: Optional[int] = None
):
    """Cập nhật message"""
    service = MessageService()
    
    update_data = {}
    if content is not None:
        update_data['content'] = content
    if reaction is not None:
        update_data['reaction'] = reaction
    if content_type is not None:
        update_data['content_type'] = content_type
    if message_type is not None:
        update_data['message_type'] = message_type
    
    message = service.update_message(message_id, **update_data)
    
    if not message:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Message not found"
        )
    
    return message


@router.patch("/{message_id}/reaction", response_model=schemas.Message)
def update_message_reaction(message_id: int, reaction: str):
    """Cập nhật reaction cho message"""
    service = MessageService()
    message = service.update_message_reaction(message_id, reaction)
    
    if not message:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Message not found"
        )
    
    return message


@router.delete("/{message_id}", status_code=status.HTTP_200_OK)
def delete_message(message_id: int):
    """Xóa message (soft delete)"""
    service = MessageService()
    success = service.delete_message(message_id)
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Message not found"
        )
    
    return {"message": "Message deleted successfully"}


@router.delete("/conversation/{conversation_id}", status_code=status.HTTP_200_OK)
def delete_conversation_messages(conversation_id: int):
    """Xóa tất cả messages của conversation"""
    service = MessageService()
    success = service.delete_conversation_messages(conversation_id)
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No messages found for this conversation"
        )
    
    return {"message": "All messages for this conversation deleted successfully"}


@router.delete("/shared-conversation/{shared_conv_id}", status_code=status.HTTP_200_OK)
def delete_shared_conversation_messages(shared_conv_id: int):
    """Xóa tất cả messages của shared conversation"""
    service = MessageService()
    success = service.delete_shared_conversation_messages(shared_conv_id)
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No messages found for this shared conversation"
        )
    
    return {"message": "All messages for this shared conversation deleted successfully"}


@router.get("/conversation/{conversation_id}/with-relations", response_model=List[schemas.Message])
def get_conversation_with_relations(conversation_id: int):
    """Lấy messages với thông tin user và agent"""
    service = MessageService()
    messages = service.get_conversation_with_relations(conversation_id)
    
    if not messages:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No messages found for this conversation"
        )
    
    return messages


@router.get("/conversation/{conversation_id}/statistics", response_model=Dict[str, Any])
def get_conversation_statistics(conversation_id: int):
    """Lấy thống kê messages trong conversation"""
    service = MessageService()
    statistics = service.get_conversation_statistics(conversation_id)
    
    return statistics
