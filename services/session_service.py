"""Session service for managing training and practice sessions."""

from __future__ import annotations

from typing import Optional, List, Dict, Any
from datetime import datetime, timedelta
import asyncio

from database import (
    Session, SessionStatus, SessionVote, SessionBoost,
    SessionRepository, SessionVoteRepository, SessionBoostRepository, database
)
from services.api_service import api_service
from services.event_service import event_service, EVENT_SESSION_STARTED, EVENT_SESSION_ENDED, EVENT_VOTE_ADDED, EVENT_BOOST_ADDED
from utils.logger import get_logger

logger = get_logger(__name__)


class SessionService:
    """Service for managing sessions with lifecycle control."""
    
    def __init__(self) -> None:
        """Initialize session service."""
        self.session_repository = SessionRepository(database)
        self.vote_repository = SessionVoteRepository(database)
        self.boost_repository = SessionBoostRepository(database)
        self._active_sessions: dict[int, Session] = {}  # guild_id -> session
        self._update_tasks: dict[int, asyncio.Task] = {}  # guild_id -> update task
        self._lock = asyncio.Lock()
    
    async def create_session(
        self,
        guild_id: int,
        host_id: int,
        server_code: str,
        notes: Optional[str] = None,
        session_channel_id: Optional[int] = None
    ) -> Optional[Session]:
        """Create a new session (only one active session per guild)."""
        try:
            # Check for existing active session
            existing = await self.get_active_session(guild_id)
            if existing:
                logger.warning(f"Active session already exists for guild {guild_id}")
                return None
            
            session = Session(
                guild_id=guild_id,
                host_id=host_id,
                server_code=server_code,
                notes=notes,
                started_at=datetime.utcnow(),
                status=SessionStatus.ACTIVE,
                session_channel_id=session_channel_id,
                vote_count=0,
                boost_count=0
            )
            
            created_session = await self.session_repository.create(session)
            
            # Cache active session
            async with self._lock:
                self._active_sessions[guild_id] = created_session
            
            # Start background updater
            await self._start_session_updater(guild_id)
            
            # Sync to API if available
            if api_service.is_available():
                await api_service.sync_session({
                    "id": created_session.id,
                    "guild_id": created_session.guild_id,
                    "host_id": created_session.host_id,
                    "server_code": created_session.server_code,
                    "status": created_session.status.value
                })
            
            # Publish session_started event
            await event_service.publish(EVENT_SESSION_STARTED, {
                "session_id": created_session.id,
                "guild_id": created_session.guild_id,
                "host_id": created_session.host_id,
                "server_code": created_session.server_code
            })
            
            logger.info(f"Created session {created_session.id} for guild {guild_id}")
            return created_session
        except Exception as e:
            logger.error(f"Error creating session: {e}")
            return None
    
    async def get_active_session(self, guild_id: int) -> Optional[Session]:
        """Get the active session for a guild."""
        try:
            # Check cache first
            async with self._lock:
                if guild_id in self._active_sessions:
                    cached = self._active_sessions[guild_id]
                    if cached.is_active:
                        return cached
                    else:
                        # Remove inactive session from cache
                        del self._active_sessions[guild_id]
            
            # Check database
            session = await self.session_repository.get_active_session(guild_id)
            if session:
                async with self._lock:
                    self._active_sessions[guild_id] = session
            return session
        except Exception as e:
            logger.error(f"Error getting active session for guild {guild_id}: {e}")
            return None
    
    async def has_active_session(self, guild_id: int) -> bool:
        """Check if guild has an active session."""
        return await self.get_active_session(guild_id) is not None
    
    async def end_session(self, guild_id: int) -> Optional[Session]:
        """End the active session for a guild."""
        try:
            session = await self.get_active_session(guild_id)
            if not session:
                logger.warning(f"No active session found for guild {guild_id}")
                return None
            
            # Calculate duration
            if session.started_at:
                duration = int((datetime.utcnow() - session.started_at).total_seconds())
            else:
                duration = 0
            
            # Update session
            session.ended_at = datetime.utcnow()
            session.status = SessionStatus.ENDED
            session.duration = duration
            
            updated_session = await self.session_repository.update(session)
            
            # Stop background updater
            await self._stop_session_updater(guild_id)
            
            # Remove from cache
            async with self._lock:
                if guild_id in self._active_sessions:
                    del self._active_sessions[guild_id]
            
            # Sync to API if available
            if api_service.is_available():
                await api_service.sync_session({
                    "id": updated_session.id,
                    "guild_id": updated_session.guild_id,
                    "host_id": updated_session.host_id,
                    "server_code": updated_session.server_code,
                    "status": updated_session.status.value,
                    "duration": duration
                })
            
            # Publish session_ended event
            await event_service.publish(EVENT_SESSION_ENDED, {
                "session_id": updated_session.id,
                "guild_id": updated_session.guild_id,
                "host_id": updated_session.host_id,
                "duration": duration
            })
            
            logger.info(f"Ended session {updated_session.id} for guild {guild_id}")
            return updated_session
        except Exception as e:
            logger.error(f"Error ending session for guild {guild_id}: {e}")
            return None
    
    async def update_session_message(
        self,
        guild_id: int,
        message_id: int,
        channel_id: int
    ) -> Optional[Session]:
        """Update session message and channel IDs."""
        try:
            session = await self.get_active_session(guild_id)
            if not session:
                return None
            
            session.session_message_id = message_id
            session.session_channel_id = channel_id
            updated = await self.session_repository.update(session)
            
            # Update cache
            async with self._lock:
                self._active_sessions[guild_id] = updated
            
            return updated
        except Exception as e:
            logger.error(f"Error updating session message: {e}")
            return None
    
    async def increment_vote_count(self, guild_id: int) -> Optional[Session]:
        """Increment vote count for active session."""
        try:
            session = await self.get_active_session(guild_id)
            if not session:
                return None
            
            session.vote_count += 1
            updated = await self.session_repository.update(session)
            
            # Update cache
            async with self._lock:
                self._active_sessions[guild_id] = updated
            
            return updated
        except Exception as e:
            logger.error(f"Error incrementing vote count: {e}")
            return None
    
    async def increment_boost_count(self, guild_id: int) -> Optional[Session]:
        """Increment boost count for active session."""
        try:
            session = await self.get_active_session(guild_id)
            if not session:
                return None
            
            session.boost_count += 1
            updated = await self.session_repository.update(session)
            
            # Update cache
            async with self._lock:
                self._active_sessions[guild_id] = updated
            
            return updated
        except Exception as e:
            logger.error(f"Error incrementing boost count: {e}")
            return None
    
    async def get_session_by_id(self, session_id: int) -> Optional[Session]:
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
    
    async def restore_sessions(self) -> int:
        """Restore active sessions from database on startup."""
        try:
            active_sessions = await self.session_repository.get_all_active_sessions()
            restored_count = 0
            
            for session in active_sessions:
                # Cache the session
                async with self._lock:
                    self._active_sessions[session.guild_id] = session
                
                # Start background updater
                await self._start_session_updater(session.guild_id)
                restored_count += 1
                logger.info(f"Restored active session {session.id} for guild {session.guild_id}")
            
            logger.info(f"Restored {restored_count} active sessions")
            return restored_count
        except Exception as e:
            logger.error(f"Error restoring sessions: {e}")
            return 0
    
    async def _start_session_updater(self, guild_id: int) -> None:
        """Start background task to update session embeds."""
        if guild_id in self._update_tasks:
            return  # Already running
        
        async def update_loop():
            while True:
                try:
                    session = await self.get_active_session(guild_id)
                    if not session or not session.is_active:
                        # Session ended, stop updater
                        await self._stop_session_updater(guild_id)
                        break
                    
                    # Calculate current duration
                    if session.started_at:
                        current_duration = int((datetime.utcnow() - session.started_at).total_seconds())
                        if current_duration != session.duration:
                            session.duration = current_duration
                            await self.session_repository.update(session)
                    
                    # Note: The actual embed update is handled by the cog
                    # The service only updates the data
                    logger.debug(f"Updated session {session.id} duration: {session.duration_str}")
                    
                    await asyncio.sleep(60)  # Update every 60 seconds
                except asyncio.CancelledError:
                    break
                except Exception as e:
                    logger.error(f"Error in session updater for guild {guild_id}: {e}")
                    await asyncio.sleep(60)  # Continue despite errors
        
        task = asyncio.create_task(update_loop())
        async with self._lock:
            self._update_tasks[guild_id] = task
    
    async def _stop_session_updater(self, guild_id: int) -> None:
        """Stop background task for a guild."""
        async with self._lock:
            if guild_id in self._update_tasks:
                task = self._update_tasks[guild_id]
                task.cancel()
                del self._update_tasks[guild_id]
                try:
                    await task
                except asyncio.CancelledError:
                    pass
    
    async def shutdown(self) -> None:
        """Cleanup all background tasks."""
        async with self._lock:
            for guild_id, task in self._update_tasks.items():
                task.cancel()
            self._update_tasks.clear()
        
        # Wait for tasks to complete
        await asyncio.sleep(0.1)
    
    # Voting and Boosting Methods
    
    async def vote(self, guild_id: int, user_id: int) -> Optional[Session]:
        """Record a vote for the active session."""
        try:
            session = await self.get_active_session(guild_id)
            if not session:
                logger.warning(f"No active session found for guild {guild_id}")
                return None
            
            # Check if user already voted
            existing_vote = await self.vote_repository.get_user_vote(session.id, user_id)
            if existing_vote:
                logger.info(f"User {user_id} already voted for session {session.id}")
                return session
            
            # Create vote record
            vote = SessionVote(
                guild_id=guild_id,
                session_id=session.id,
                user_id=user_id
            )
            await self.vote_repository.create(vote)
            
            # Update session vote count
            session.vote_count += 1
            updated_session = await self.session_repository.update(session)
            
            # Update cache
            async with self._lock:
                self._active_sessions[guild_id] = updated_session
            
            # Publish vote_added event
            await event_service.publish(EVENT_VOTE_ADDED, {
                "session_id": session.id,
                "guild_id": guild_id,
                "user_id": user_id,
                "vote_count": updated_session.vote_count
            })
            
            logger.info(f"User {user_id} voted for session {session.id}")
            return updated_session
        except Exception as e:
            logger.error(f"Error recording vote: {e}")
            return None
    
    async def boost(self, guild_id: int, user_id: int, note: Optional[str] = None) -> Optional[Session]:
        """Record a boost for the active session."""
        try:
            session = await self.get_active_session(guild_id)
            if not session:
                logger.warning(f"No active session found for guild {guild_id}")
                return None
            
            # Create boost record
            boost = SessionBoost(
                guild_id=guild_id,
                session_id=session.id,
                user_id=user_id,
                note=note
            )
            await self.boost_repository.create(boost)
            
            # Update session boost count
            session.boost_count += 1
            updated_session = await self.session_repository.update(session)
            
            # Update cache
            async with self._lock:
                self._active_sessions[guild_id] = updated_session
            
            # Publish boost_added event
            await event_service.publish(EVENT_BOOST_ADDED, {
                "session_id": session.id,
                "guild_id": guild_id,
                "user_id": user_id,
                "note": note,
                "boost_count": updated_session.boost_count
            })
            
            logger.info(f"User {user_id} boosted session {session.id}")
            return updated_session
        except Exception as e:
            logger.error(f"Error recording boost: {e}")
            return None
    
    async def has_user_voted(self, guild_id: int, user_id: int) -> bool:
        """Check if user has voted for the active session."""
        try:
            session = await self.get_active_session(guild_id)
            if not session:
                return False
            
            vote = await self.vote_repository.get_user_vote(session.id, user_id)
            return vote is not None
        except Exception as e:
            logger.error(f"Error checking user vote: {e}")
            return False
    
    async def get_vote_count(self, guild_id: int) -> int:
        """Get vote count for the active session."""
        try:
            session = await self.get_active_session(guild_id)
            if not session:
                return 0
            
            return await self.vote_repository.get_vote_count(session.id)
        except Exception as e:
            logger.error(f"Error getting vote count: {e}")
            return 0
    
    async def get_boost_count(self, guild_id: int) -> int:
        """Get boost count for the active session."""
        try:
            session = await self.get_active_session(guild_id)
            if not session:
                return 0
            
            return await self.boost_repository.get_boost_count(session.id)
        except Exception as e:
            logger.error(f"Error getting boost count: {e}")
            return 0
    
    async def get_session_statistics(self, guild_id: int) -> Dict[str, Any]:
        """Get comprehensive statistics for the active session."""
        try:
            session = await self.get_active_session(guild_id)
            if not session:
                return {}
            
            vote_count = await self.vote_repository.get_vote_count(session.id)
            boost_count = await self.boost_repository.get_boost_count(session.id)
            
            return {
                "session_id": session.id,
                "guild_id": session.guild_id,
                "host_id": session.host_id,
                "server_code": session.server_code,
                "status": session.status.value,
                "vote_count": vote_count,
                "boost_count": boost_count,
                "duration": session.duration,
                "duration_str": session.duration_str,
                "started_at": session.started_at.isoformat() if session.started_at else None,
                "ended_at": session.ended_at.isoformat() if session.ended_at else None
            }
        except Exception as e:
            logger.error(f"Error getting session statistics: {e}")
            return {}
    
    async def record_vote(self, guild_id: int, user_id: int) -> bool:
        """Record a vote (alias for vote method)."""
        session = await self.vote(guild_id, user_id)
        return session is not None
    
    async def record_boost(self, guild_id: int, user_id: int, note: Optional[str] = None) -> bool:
        """Record a boost (alias for boost method)."""
        session = await self.boost(guild_id, user_id, note)
        return session is not None
    
    async def shutdown(self) -> None:
        """Cleanup all background tasks."""
        async with self._lock:
            for guild_id, task in self._update_tasks.items():
                task.cancel()
            self._update_tasks.clear()
        
        # Wait for tasks to complete
        await asyncio.sleep(0.1)
