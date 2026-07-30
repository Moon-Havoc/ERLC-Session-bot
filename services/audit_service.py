"""Audit service for logging internal events."""

from __future__ import annotations

from typing import Optional, List
from datetime import datetime
import json

from database import AuditLog, AuditLogRepository, database
from services.event_service import event_service, Event, EVENT_SESSION_STARTED, EVENT_SESSION_ENDED, EVENT_VOTE_ADDED, EVENT_BOOST_ADDED
from utils.logger import get_logger

logger = get_logger(__name__)


class AuditService:
    """Service for audit logging of internal events."""
    
    def __init__(self) -> None:
        """Initialize audit service."""
        self.audit_repo = AuditLogRepository(database)
        self._initialized = False
    
    async def initialize(self) -> None:
        """Initialize audit service and register event listeners."""
        if self._initialized:
            return
        
        # Register event listeners
        await event_service.subscribe(EVENT_SESSION_STARTED, self._on_session_started, priority=5)
        await event_service.subscribe(EVENT_SESSION_ENDED, self._on_session_ended, priority=5)
        await event_service.subscribe(EVENT_VOTE_ADDED, self._on_vote_added, priority=5)
        await event_service.subscribe(EVENT_BOOST_ADDED, self._on_boost_added, priority=5)
        
        self._initialized = True
        logger.info("Audit service initialized")
    
    async def _on_session_started(self, event: Event) -> None:
        """Handle session started event."""
        try:
            guild_id = event.data.get("guild_id")
            session_id = event.data.get("session_id")
            host_id = event.data.get("host_id")
            server_code = event.data.get("server_code")
            
            if not guild_id or not session_id:
                return
            
            # Create audit log entry
            metadata = {
                "server_code": server_code,
                "host_id": host_id
            }
            
            log = AuditLog(
                guild_id=guild_id,
                session_id=session_id,
                event_type=EVENT_SESSION_STARTED,
                user_id=host_id,
                timestamp=datetime.utcnow(),
                metadata=json.dumps(metadata)
            )
            
            await self.audit_repo.create(log)
            logger.debug(f"Audit log: session_started for session {session_id}")
        except Exception as e:
            logger.error(f"Error auditing session_started event: {e}")
    
    async def _on_session_ended(self, event: Event) -> None:
        """Handle session ended event."""
        try:
            guild_id = event.data.get("guild_id")
            session_id = event.data.get("session_id")
            host_id = event.data.get("host_id")
            duration = event.data.get("duration")
            
            if not guild_id or not session_id:
                return
            
            # Create audit log entry
            metadata = {
                "host_id": host_id,
                "duration": duration
            }
            
            log = AuditLog(
                guild_id=guild_id,
                session_id=session_id,
                event_type=EVENT_SESSION_ENDED,
                user_id=host_id,
                timestamp=datetime.utcnow(),
                metadata=json.dumps(metadata)
            )
            
            await self.audit_repo.create(log)
            logger.debug(f"Audit log: session_ended for session {session_id}")
        except Exception as e:
            logger.error(f"Error auditing session_ended event: {e}")
    
    async def _on_vote_added(self, event: Event) -> None:
        """Handle vote added event."""
        try:
            guild_id = event.data.get("guild_id")
            session_id = event.data.get("session_id")
            user_id = event.data.get("user_id")
            vote_count = event.data.get("vote_count")
            
            if not guild_id:
                return
            
            # Create audit log entry
            metadata = {
                "vote_count": vote_count
            }
            
            log = AuditLog(
                guild_id=guild_id,
                session_id=session_id,
                event_type=EVENT_VOTE_ADDED,
                user_id=user_id,
                timestamp=datetime.utcnow(),
                metadata=json.dumps(metadata)
            )
            
            await self.audit_repo.create(log)
            logger.debug(f"Audit log: vote_added by user {user_id}")
        except Exception as e:
            logger.error(f"Error auditing vote_added event: {e}")
    
    async def _on_boost_added(self, event: Event) -> None:
        """Handle boost added event."""
        try:
            guild_id = event.data.get("guild_id")
            session_id = event.data.get("session_id")
            user_id = event.data.get("user_id")
            note = event.data.get("note")
            boost_count = event.data.get("boost_count")
            
            if not guild_id:
                return
            
            # Create audit log entry
            metadata = {
                "note": note,
                "boost_count": boost_count
            }
            
            log = AuditLog(
                guild_id=guild_id,
                session_id=session_id,
                event_type=EVENT_BOOST_ADDED,
                user_id=user_id,
                timestamp=datetime.utcnow(),
                metadata=json.dumps(metadata)
            )
            
            await self.audit_repo.create(log)
            logger.debug(f"Audit log: boost_added by user {user_id}")
        except Exception as e:
            logger.error(f"Error auditing boost_added event: {e}")
    
    async def get_audit_logs(self, guild_id: int, limit: int = 100) -> List[AuditLog]:
        """Get audit logs for a guild."""
        try:
            return await self.audit_repo.get_by_guild(guild_id, limit)
        except Exception as e:
            logger.error(f"Error getting audit logs: {e}")
            return []
    
    async def get_session_audit_logs(self, session_id: int, limit: int = 100) -> List[AuditLog]:
        """Get audit logs for a specific session."""
        try:
            return await self.audit_repo.get_by_session(session_id, limit)
        except Exception as e:
            logger.error(f"Error getting session audit logs: {e}")
            return []
    
    async def get_user_audit_logs(self, guild_id: int, user_id: int, limit: int = 100) -> List[AuditLog]:
        """Get audit logs for a specific user."""
        try:
            return await self.audit_repo.get_by_user(guild_id, user_id, limit)
        except Exception as e:
            logger.error(f"Error getting user audit logs: {e}")
            return []
    
    async def get_event_audit_logs(self, guild_id: int, event_type: str, limit: int = 100) -> List[AuditLog]:
        """Get audit logs for a specific event type."""
        try:
            return await self.audit_repo.get_by_event_type(guild_id, event_type, limit)
        except Exception as e:
            logger.error(f"Error getting event audit logs: {e}")
            return []
