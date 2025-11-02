from typing import List, Optional
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession

from api.repositories.conversation import ConversationRepository
from api.core.models import Conversation, ConversationAgent


class ConversationService:
    def __init__(self):
        self.repository = ConversationRepository()

    async def create_conversation(
        self,
        db: AsyncSession,
        name: str,
        user_id: int,
        is_shared: bool = False,
        summary: Optional[str] = None
    ) -> Conversation:
        convo = Conversation(
            name=name,
            user_id=user_id,
            created_at=datetime.utcnow(),
            status=1,
            is_shared=is_shared,
            session="",  # TODO: Generate session
            last_updated=None,
            summary=summary,
            summary_embedding=None  # TODO: Generate embedding
        )
        return await self.repository.create_conversation(db, convo)

    async def get_conversation(self, db: AsyncSession, conversation_id: int) -> Optional[Conversation]:
        return await self.repository.get_conversation(db, conversation_id)

    async def list_conversations(
        self,
        db: AsyncSession,
        skip: int = 0,
        limit: int = 100
    ) -> List[Conversation]:
        return await self.repository.list_conversations(db, skip=skip, limit=limit)
    
    async def get_conversations_by_user_id(
        self,
        db: AsyncSession,
        user_id: int
    ) -> List[Conversation]:
        return await self.repository.get_conversation_by_user_id(db, user_id)

    async def update_conversation(
        self,
        db: AsyncSession,
        conversation_id: int,
        name: Optional[str] = None,
        is_shared: Optional[bool] = None,
        summary: Optional[str] = None
    ) -> Optional[Conversation]:
        convo = await self.repository.get_conversation(db, conversation_id)
        if not convo:
            return None

        if name is not None:
            convo.name = name
        if is_shared is not None:
            convo.is_shared = is_shared
        if summary is not None:
            convo.summary = summary
            # TODO: Update embedding if summary changed

        convo.last_updated = datetime.utcnow()
        return await self.repository.update_conversation(db, convo)

    async def delete_conversation(self, db: AsyncSession, conversation_id: int) -> bool:
        convo = await self.repository.get_conversation(db, conversation_id)
        if not convo:
            return False
        await self.repository.delete_conversation(db, convo)
        return True

    async def create_conversation_agent(
        self,
        db: AsyncSession,
        conversation_id: int,
        agent_id: int,
        is_active: bool = True
    ) -> ConversationAgent:
        ca = ConversationAgent(
            conversation_id=conversation_id,
            agent_id=agent_id,
            is_active=is_active,
            created_at=datetime.utcnow(),
            status=1,
            last_updated=None
        )
        return await self.repository.create_conversation_agent(db, ca)

    async def list_conversation_agents(
        self,
        db: AsyncSession,
        conversation_id: int
    ) -> List[ConversationAgent]:
        return await self.repository.list_conversation_agents_by_conversation(db, conversation_id)

    async def update_conversation_agent(
        self,
        db: AsyncSession,
        ca_id: int,
        is_active: Optional[bool] = None
    ) -> Optional[ConversationAgent]:
        ca = await self.repository.get_conversation_agent(db, ca_id)
        if not ca:
            return None

        if is_active is not None:
            ca.is_active = is_active

        ca.last_updated = datetime.utcnow()
        return await self.repository.update_conversation_agent(db, ca)

    async def delete_conversation_agent(self, db: AsyncSession, ca_id: int) -> bool:
        ca = await self.repository.get_conversation_agent(db, ca_id)
        if not ca:
            return False
        await self.repository.delete_conversation_agent(db, ca)
        return True