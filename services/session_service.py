"""Session service for managing training and practice sessions."""

from typing import Optional, List
from datetime import datetime

from database import (
    Session, SessionParticipant, SessionStatus,
    SessionRepository, SessionParticipantRepository, database
)
from services.api_service import api_service
from utils.logger import get_logger

logger = get_logger(__name__)


class SessionService:
    """Service for managing sessions."""
    
    def __init__(self) -> None:
        """Initialize session service."""
        self.session_repository = SessionRepository(database)
        self.participant_repository = SessionParticipantRepository(database)
    
    async def create_session(
        self,
        guild_id: int,
        host_id: int,
        session_type: str,
        title: str,
        description: Optional[str] = None,
        scheduled_time: Optional[datetime] = None,
        max_participants: Optional[int] = None,
        channel_id: Optional[int] = None
    ) -> Optional[Session]:
        """Create a new session."""
        try:
            session = Session(
                guild_id=guild_id,
                host_id=host_id,
                session_type=session_type,
                title=title,
                description=description,
                scheduled_time=scheduled_time,
                max_participants=max_participants,
                channel_id=channel_id,
                status=SessionStatus.ACTIVE
            )
            
            created_session = await self.session_repository.create(session)
            
            # Sync to API if available
            if api_service.is_available():
                await api_service.sync_session({
                    "id": created_session.id,
                    "guild_id": created_session.guild_id,
                    "host_id": created_session.host_id,
                    "session_type": created_session.session_type,
                    "title": created_session.title,
                    "status": created_session.status.value
                })
            
            logger.info(f"Created session {created_session.id} for guild {guild_id}")
            return created_session
        except Exception as e:
            logger.error(f"Error creating session: {e}")
            return None
    
    async def get_session(self, session_id: int) -> Optional[Session]:
        """Get session by ID."""
        try:
            return await self.session_repository.get_by_id(session_id)
        except Exception as e:
            logger.error(f"Error getting session {session_id}: {e}")
            return None
    
    async def get_guild_sessions(self, guild_id: int, limit: int = 50) -> List[Session]:
        """Get sessions for a guild."""
        try:
            return await self.session_repository.get_by_guild(guild_id, limit)
        except Exception as e:
            logger.error(f"Error getting sessions for guild {guild_id}: {e}")
            return []
    
    async def get_active_sessions(self, guild_id: int) -> List[Session]:
        """Get all active sessions for a guild."""
        try:
            return await self.session_repository.get_active_sessions(guild_id)
        except Exception as e:
            logger.error(f"Error getting active sessions for guild {guild_id}: {e}")
            return []
    
    async def update_session(
        self,
        session_id: int,
        title: Optional[str] = None,
        description: Optional[str] = None,
        scheduled_time: Optional[datetime] = None,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
        status: Optional[SessionStatus] = None,
        max_participants: Optional[int] = None,
        current_participants: Optional[int] = None,
        message_id: Optional[int] = None,
        channel_id: Optional[int] = None
    ) -> Optional[Session]:
        """Update session details."""
        try:
            session = await self.session_repository.get_by_id(session_id)
            if not session:
                logger.warning(f"Session {session_id} not found")
                return None
            
            # Update provided fields
            if title is not None:
                session.title = title
            if description is not None:
                session.description = description
            if scheduled_time is not None:
                session.scheduled_time = scheduled_time
            if start_time is not None:
                session.start_time = start_time
            if end_time is not None:
                session.end_time = end_time
            if status is not None:
                session.status = status
            if max_participants is not None:
                session.max_participants = max_participants
            if current_participants is not None:
                session.current_participants = current_participants
            if message_id is not None:
                session.message_id = message_id
            if channel_id is not None:
                session.channel_id = channel_id
            
            updated_session = await self.session_repository.update(session)
            
            # Sync to API if available
            if api_service.is_available():
                await api_service.sync_session({
                    "id": updated_session.id,
                    "guild_id": updated_session.guild_id,
                    "host_id": updated_session.host_id,
                    "session_type": updated_session.session_type,
                    "title": updated_session.title,
                    "status": updated_session.status.value
                })
            
            logger.info(f"Updated session {session_id}")
            return updated_session
        except Exception as e:
            logger.error(f"Error updating session {session_id}: {e}")
            return None
    
    async def delete_session(self, session_id: int) -> bool:
        """Delete a session."""
        try:
            result = await self.session_repository.delete(session_id)
            if result:
                logger.info(f"Deleted session {session_id}")
            return result
        except Exception as e:
            logger.error(f"Error deleting session {session_id}: {e}")
            return False
    
    async def start_session(self, session_id: int) -> Optional[Session]:
        """Start a session."""
        return await self.update_session(
            session_id,
            start_time=datetime.utcnow(),
            status=SessionStatus.ACTIVE
        )
    
    async def end_session(self, session_id: int) -> Optional[Session]:
        """End a session."""
        return await self.update_session(
            session_id,
            end_time=datetime.utcnow(),
            status=SessionStatus.COMPLETED
        )
    
    async def cancel_session(self, session_id: int) -> Optional[Session]:
        """Cancel a session."""
        return await self.update_session(
            session_id,
            status=SessionStatus.CANCELLED
        )
    
    async def add_participant(
        self,
        session_id: int,
        user_id: int
    ) -> Optional[SessionParticipant]:
        """Add participant to session."""
        try:
            participant = SessionParticipant(
                session_id=session_id,
                user_id=user_id
            )
            
            created_participant = await self.participant_repository.add_participant(participant)
            
            # Update session participant count
            session = await self.session_repository.get_by_id(session_id)
            if session:
                await self.update_session(session_id, current_participants=session.current_participants + 1)
            
            logger.info(f"Added user {user_id} to session {session_id}")
            return created_participant
        except Exception as e:
            logger.error(f"Error adding participant to session {session_id}: {e}")
            return None
    
    async def remove_participant(
        self,
        session_id: int,
        user_id: int
    ) -> bool:
        """Remove participant from session."""
        try:
            result = await self.participant_repository.remove_participant(session_id, user_id)
            
            if result:
                # Update session participant count
                session = await self.session_repository.get_by_id(session_id)
                if session:
                    new_count = max(0, session.current_participants - 1)
                    await self.update_session(session_id, current_participants=new_count)
                
                logger.info(f"Removed user {user_id} from session {session_id}")
            
            return result
        except Exception as e:
            logger.error(f"Error removing participant from session {session_id}: {e}")
            return False
    
    async def get_participants(self, session_id: int) -> List[SessionParticipant]:
        """Get all participants for a session."""
        try:
            return await self.participant_repository.get_participants(session_id)
        except Exception as e:
            logger.error(f"Error getting participants for session {session_id}: {e}")
            return []
    
    async def is_participant(self, session_id: int, user_id: int) -> bool:
        """Check if user is a participant in session."""
        participants = await self.get_participants(session_id)
        return any(p.user_id == user_id for p in participants)
    
    async def get_user_sessions(self, user_id: int, guild_id: int) -> List[Session]:
        """Get sessions where user is a participant."""
        try:
            # Get all guild sessions
            sessions = await self.get_guild_sessions(guild_id)
            
            # Filter sessions where user is a participant
            user_sessions = []
            for session in sessions:
                if await self.is_participant(session.id, user_id):
                    user_sessions.append(session)
            
            return user_sessions
        except Exception as e:
            logger.error(f"Error getting sessions for user {user_id}: {e}")
            return []
    
    async def cleanup_old_sessions(self, days: int = 30) -> int:
        """Clean up old completed/cancelled sessions."""
        try:
            from datetime import timedelta
            cutoff_date = datetime.utcnow() - timedelta(days=days)
            
            # Get sessions for cleanup (this would need a new repository method)
            # For now, this is a placeholder for future implementation
            logger.info(f"Session cleanup placeholder - would clean sessions older than {days} days")
            return 0
        except Exception as e:
            logger.error(f"Error cleaning up old sessions: {e}")
            return 0
