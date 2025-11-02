"""Message utilities for formatting and parsing WebSocket messages."""

import json
from typing import Dict, Any, Optional
from datetime import datetime
from enum import Enum


class MessageType(str, Enum):
    """Enum for different message types."""
    TEXT = "text"
    COMMAND = "command"
    ERROR = "error"
    SYSTEM = "system"
    TYPING = "typing"


class Message:
    """Message wrapper for structured WebSocket communication."""

    def __init__(
        self,
        content: str,
        message_type: MessageType = MessageType.TEXT,
        metadata: Optional[Dict[str, Any]] = None
    ):
        """Initialize message.
        
        Args:
            content: Message content
            message_type: Type of message
            metadata: Optional metadata dict
        """
        self.content = content
        self.message_type = message_type
        self.metadata = metadata or {}
        self.timestamp = datetime.now().isoformat()

    def to_json(self) -> str:
        """Convert message to JSON string.
        
        Returns:
            JSON string representation
        """
        return json.dumps({
            "type": self.message_type,
            "content": self.content,
            "metadata": self.metadata,
            "timestamp": self.timestamp
        })

    @classmethod
    def from_json(cls, json_str: str) -> "Message":
        """Parse message from JSON string.
        
        Args:
            json_str: JSON string
            
        Returns:
            Message instance
        """
        try:
            data = json.loads(json_str)
            return cls(
                content=data.get("content", ""),
                message_type=MessageType(data.get("type", MessageType.TEXT)),
                metadata=data.get("metadata", {})
            )
        except (json.JSONDecodeError, ValueError):
            # If parsing fails, treat as plain text
            return cls(content=json_str, message_type=MessageType.TEXT)

    @classmethod
    def text(cls, content: str) -> "Message":
        """Create a text message.
        
        Args:
            content: Message text
            
        Returns:
            Message instance
        """
        return cls(content=content, message_type=MessageType.TEXT)

    @classmethod
    def error(cls, content: str, error_code: Optional[str] = None) -> "Message":
        """Create an error message.
        
        Args:
            content: Error message
            error_code: Optional error code
            
        Returns:
            Message instance
        """
        metadata = {"error_code": error_code} if error_code else {}
        return cls(content=content, message_type=MessageType.ERROR, metadata=metadata)

    @classmethod
    def system(cls, content: str) -> "Message":
        """Create a system message.
        
        Args:
            content: System message
            
        Returns:
            Message instance
        """
        return cls(content=content, message_type=MessageType.SYSTEM)

    @classmethod
    def typing(cls, is_typing: bool = True) -> "Message":
        """Create a typing indicator message.
        
        Args:
            is_typing: Whether agent is typing
            
        Returns:
            Message instance
        """
        return cls(
            content="",
            message_type=MessageType.TYPING,
            metadata={"is_typing": is_typing}
        )
