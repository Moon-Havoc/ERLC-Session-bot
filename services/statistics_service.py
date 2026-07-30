"""Statistics service for tracking session metrics."""

from __future__ import annotations

from typing import Optional, List, Dict, Any
from datetime import datetime
import json

from database import (
    HostStatistics, GuildStatistics,
    HostStatisticsRepository, GuildStatisticsRepository, database
)
from services.event_service import event_service, Event, EVENT_SESSION_STARTED, EVENT_SESSION_ENDED, EVENT_VOTE_ADDED, EVENT_BOOST_ADDED
from utils.logger import get_logger

logger = get_logger(__name__)


class StatisticsService:
    """Service for tracking and calculating session statistics."""
    
    def __init__(self) -> None:
        """Initialize statistics service."""
        self.host_stats_repo = HostStatisticsRepository(database)
        self.guild_stats_repo = GuildStatisticsRepository(database)
        self._initialized = False
    
    async def initialize(self) -> None:
        """Initialize statistics service and register event listeners."""
        if self._initialized:
            return
        
        # Register event listeners
        await event_service.subscribe(EVENT_SESSION_STARTED, self._on_session_started, priority=10)
        await event_service.subscribe(EVENT_SESSION_ENDED, self._on_session_ended, priority=10)
        await event_service.subscribe(EVENT_VOTE_ADDED, self._on_vote_added, priority=10)
        await event_service.subscribe(EVENT_BOOST_ADDED, self._on_boost_added, priority=10)
        
        self._initialized = True
        logger.info("Statistics service initialized")
    
    async def _on_session_started(self, event: Event) -> None:
        """Handle session started event."""
        try:
            guild_id = event.data.get("guild_id")
            host_id = event.data.get("host_id")
            
            if not guild_id or not host_id:
                return
            
            # Update host statistics
            host_stats = await self.host_stats_repo.get_or_create(guild_id, host_id)
            host_stats.sessions_hosted += 1
            host_stats.last_hosted = datetime.utcnow()
            await self.host_stats_repo.update(host_stats)
            
            logger.debug(f"Updated host stats for {host_id} on session start")
        except Exception as e:
            logger.error(f"Error handling session_started event: {e}")
    
    async def _on_session_ended(self, event: Event) -> None:
        """Handle session ended event."""
        try:
            guild_id = event.data.get("guild_id")
            host_id = event.data.get("host_id")
            duration = event.data.get("duration", 0)
            
            if not guild_id or not host_id:
                return
            
            # Update host statistics
            host_stats = await self.host_stats_repo.get_or_create(guild_id, host_id)
            host_stats.total_hosted_time += duration
            await self.host_stats_repo.update(host_stats)
            
            # Update guild statistics
            guild_stats = await self.guild_stats_repo.get_or_create(guild_id)
            guild_stats.total_sessions += 1
            guild_stats.total_hosted_time += duration
            
            # Update longest session
            if duration > guild_stats.longest_session:
                guild_stats.longest_session = duration
            
            # Update average session length
            if guild_stats.total_sessions > 0:
                guild_stats.average_session_length = guild_stats.total_hosted_time // guild_stats.total_sessions
            
            await self.guild_stats_repo.update(guild_stats)
            
            logger.debug(f"Updated statistics for session end: duration={duration}")
        except Exception as e:
            logger.error(f"Error handling session_ended event: {e}")
    
    async def _on_vote_added(self, event: Event) -> None:
        """Handle vote added event."""
        try:
            guild_id = event.data.get("guild_id")
            host_id = event.data.get("user_id")  # This is the voter, not the host
            
            if not guild_id:
                return
            
            # Note: Vote tracking is session-specific, not host-specific
            # For now, we'll just track total votes per guild
            guild_stats = await self.guild_stats_repo.get_or_create(guild_id)
            guild_stats.total_votes += 1
            await self.guild_stats_repo.update(guild_stats)
            
            logger.debug(f"Updated guild vote count for {guild_id}")
        except Exception as e:
            logger.error(f"Error handling vote_added event: {e}")
    
    async def _on_boost_added(self, event: Event) -> None:
        """Handle boost added event."""
        try:
            guild_id = event.data.get("guild_id")
            
            if not guild_id:
                return
            
            # Update guild statistics
            guild_stats = await self.guild_stats_repo.get_or_create(guild_id)
            guild_stats.total_boosts += 1
            await self.guild_stats_repo.update(guild_stats)
            
            logger.debug(f"Updated guild boost count for {guild_id}")
        except Exception as e:
            logger.error(f"Error handling boost_added event: {e}")
    
    async def get_host_stats(self, guild_id: int, user_id: int) -> Optional[HostStatistics]:
        """Get statistics for a specific host."""
        try:
            return await self.host_stats_repo.get(guild_id, user_id)
        except Exception as e:
            logger.error(f"Error getting host stats: {e}")
            return None
    
    async def get_server_stats(self, guild_id: int) -> Optional[GuildStatistics]:
        """Get statistics for a guild."""
        try:
            return await self.guild_stats_repo.get(guild_id)
        except Exception as e:
            logger.error(f"Error getting server stats: {e}")
            return None
    
    async def get_top_hosts(self, guild_id: int, limit: int = 10) -> List[HostStatistics]:
        """Get top hosts by sessions hosted."""
        try:
            return await self.host_stats_repo.get_top_hosts(guild_id, limit)
        except Exception as e:
            logger.error(f"Error getting top hosts: {e}")
            return []
    
    async def get_session_stats(self, guild_id: int, session_id: int) -> Dict[str, Any]:
        """Get statistics for a specific session."""
        try:
            # This would need session-specific statistics tracking
            # For now, return basic session info
            return {
                "session_id": session_id,
                "guild_id": guild_id
            }
        except Exception as e:
            logger.error(f"Error getting session stats: {e}")
            return {}
    
    async def get_all_hosts(self, guild_id: int) -> List[HostStatistics]:
        """Get all hosts for a guild."""
        try:
            return await self.host_stats_repo.get_all_hosts(guild_id)
        except Exception as e:
            logger.error(f"Error getting all hosts: {e}")
            return []
