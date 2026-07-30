"""Statistics service for tracking and reporting session metrics."""

from __future__ import annotations

from typing import Optional, List, Dict, Any
from datetime import datetime, timedelta

from database import (
    SessionStats, Session, Host, Boost, Vote,
    SessionStatsRepository, SessionRepository, HostRepository, BoostRepository, VoteRepository, database
)
from services.api_service import api_service
from utils.logger import get_logger

logger = get_logger(__name__)


class StatsService:
    """Service for managing statistics and metrics."""
    
    def __init__(self) -> None:
        """Initialize stats service."""
        self.stats_repository = SessionStatsRepository(database)
        self.session_repository = SessionRepository(database)
        self.host_repository = HostRepository(database)
        self.boost_repository = BoostRepository(database)
        self.vote_repository = VoteRepository(database)
    
    async def record_stat(
        self,
        session_id: int,
        user_id: int,
        metric_name: str,
        metric_value: float
    ) -> Optional[SessionStats]:
        """Record a session statistic."""
        try:
            stat = SessionStats(
                session_id=session_id,
                user_id=user_id,
                metric_name=metric_name,
                metric_value=metric_value
            )
            
            created_stat = await self.stats_repository.create(stat)
            
            # Sync to API if available
            if api_service.is_available():
                await api_service.sync_stats({
                    "session_id": session_id,
                    "user_id": user_id,
                    "metric_name": metric_name,
                    "metric_value": metric_value
                })
            
            logger.info(f"Recorded stat {metric_name}={metric_value} for user {user_id}")
            return created_stat
        except Exception as e:
            logger.error(f"Error recording stat: {e}")
            return None
    
    async def get_session_stats(self, session_id: int) -> List[SessionStats]:
        """Get statistics for a session."""
        try:
            return await self.stats_repository.get_by_session(session_id)
        except Exception as e:
            logger.error(f"Error getting stats for session {session_id}: {e}")
            return []
    
    async def get_user_stats(self, user_id: int, limit: int = 100) -> List[SessionStats]:
        """Get statistics for a user."""
        try:
            return await self.stats_repository.get_by_user(user_id, limit)
        except Exception as e:
            logger.error(f"Error getting stats for user {user_id}: {e}")
            return []
    
    async def get_user_aggregate_stats(self, user_id: int, guild_id: int) -> Dict[str, float]:
        """Get aggregate statistics for a user."""
        try:
            user_stats = await self.get_user_stats(user_id)
            
            # Filter by guild (need to join with sessions - simplified for now)
            # This would need additional query logic in the repository
            
            aggregates: Dict[str, float] = {}
            for stat in user_stats:
                if stat.metric_name not in aggregates:
                    aggregates[stat.metric_name] = 0.0
                aggregates[stat.metric_name] += stat.metric_value
            
            return aggregates
        except Exception as e:
            logger.error(f"Error getting aggregate stats for user {user_id}: {e}")
            return {}
    
    async def get_guild_leaderboard(self, guild_id: int, metric_name: str, limit: int = 10) -> List[Dict]:
        """Get leaderboard for a specific metric."""
        try:
            # This would need a more complex query
            # Placeholder for future implementation
            logger.debug(f"Leaderboard placeholder for {metric_name} in guild {guild_id}")
            return []
        except Exception as e:
            logger.error(f"Error getting leaderboard: {e}")
            return []
    
    async def record_host_session(
        self,
        guild_id: int,
        user_id: int,
        participant_count: int
    ) -> Optional[Host]:
        """Record a hosted session for a host."""
        try:
            host = await self.host_repository.get_by_user(guild_id, user_id)
            
            if not host:
                host = Host(
                    guild_id=guild_id,
                    user_id=user_id,
                    total_sessions_hosted=1,
                    total_participants=participant_count
                )
                await self.host_repository.create(host)
            else:
                host.total_sessions_hosted += 1
                host.total_participants += participant_count
                await self.host_repository.update(host)
            
            logger.info(f"Recorded hosted session for user {user_id}")
            return host
        except Exception as e:
            logger.error(f"Error recording host session: {e}")
            return None
    
    async def rate_host(
        self,
        guild_id: int,
        user_id: int,
        rating: int
    ) -> Optional[Host]:
        """Rate a host (1-5 scale)."""
        try:
            if not 1 <= rating <= 5:
                logger.warning(f"Invalid rating: {rating}")
                return None
            
            host = await self.host_repository.get_by_user(guild_id, user_id)
            if not host:
                logger.warning(f"Host not found for user {user_id}")
                return None
            
            # Update average rating
            total_rating_value = host.average_rating * host.total_rating_count
            host.total_rating_count += 1
            host.average_rating = (total_rating_value + rating) / host.total_rating_count
            
            updated_host = await self.host_repository.update(host)
            logger.info(f"Rated host {user_id} with {rating} stars")
            return updated_host
        except Exception as e:
            logger.error(f"Error rating host: {e}")
            return None
    
    async def get_host_stats(self, guild_id: int, user_id: int) -> Optional[Host]:
        """Get host statistics."""
        try:
            return await self.host_repository.get_by_user(guild_id, user_id)
        except Exception as e:
            logger.error(f"Error getting host stats: {e}")
            return None
    
    async def get_active_hosts(self, guild_id: int) -> List[Host]:
        """Get all active hosts for a guild."""
        try:
            return await self.host_repository.get_active_hosts(guild_id)
        except Exception as e:
            logger.error(f"Error getting active hosts: {e}")
            return []
    
    async def record_boost(
        self,
        guild_id: int,
        user_id: int,
        boost_count: int = 1
    ) -> Optional[Boost]:
        """Record server boost for a user."""
        try:
            boost = await self.boost_repository.get_by_user(guild_id, user_id)
            
            if not boost:
                boost = Boost(
                    guild_id=guild_id,
                    user_id=user_id,
                    boost_count=boost_count,
                    total_boosts=boost_count,
                    last_boost_at=datetime.utcnow()
                )
                await self.boost_repository.create(boost)
            else:
                boost.boost_count = boost_count
                boost.total_boosts += boost_count
                boost.last_boost_at = datetime.utcnow()
                await self.boost_repository.update(boost)
            
            # Sync to API if available
            if api_service.is_available():
                await api_service.sync_boost({
                    "guild_id": guild_id,
                    "user_id": user_id,
                    "boost_count": boost_count,
                    "total_boosts": boost.total_boosts
                })
            
            logger.info(f"Recorded boost for user {user_id}")
            return boost
        except Exception as e:
            logger.error(f"Error recording boost: {e}")
            return None
    
    async def get_boost_stats(self, guild_id: int, user_id: int) -> Optional[Boost]:
        """Get boost statistics for a user."""
        try:
            return await self.boost_repository.get_by_user(guild_id, user_id)
        except Exception as e:
            logger.error(f"Error getting boost stats: {e}")
            return None
    
    async def record_vote(
        self,
        guild_id: int,
        user_id: int,
        target_id: int,
        vote_type: str,
        value: int
    ) -> Optional[Vote]:
        """Record a vote."""
        try:
            # Check if user already voted
            existing = await self.vote_repository.get_user_vote(user_id, target_id, vote_type)
            if existing:
                # Update existing vote
                # This would need an update method in the repository
                logger.info(f"Updated vote for user {user_id} on {target_id}")
                return existing
            
            vote = Vote(
                guild_id=guild_id,
                user_id=user_id,
                target_id=target_id,
                vote_type=vote_type,
                value=value
            )
            
            created_vote = await self.vote_repository.create(vote)
            
            # Sync to API if available
            if api_service.is_available():
                await api_service.sync_vote({
                    "guild_id": guild_id,
                    "user_id": user_id,
                    "target_id": target_id,
                    "vote_type": vote_type,
                    "value": value
                })
            
            logger.info(f"Recorded vote for user {user_id} on {target_id}")
            return created_vote
        except Exception as e:
            logger.error(f"Error recording vote: {e}")
            return None
    
    async def get_votes(self, target_id: int, vote_type: str) -> List[Vote]:
        """Get votes for a target."""
        try:
            return await self.vote_repository.get_votes(target_id, vote_type)
        except Exception as e:
            logger.error(f"Error getting votes: {e}")
            return []
    
    async def get_vote_summary(self, target_id: int, vote_type: str) -> Dict[str, int]:
        """Get vote summary (upvotes/downvotes)."""
        try:
            votes = await self.get_votes(target_id, vote_type)
            
            upvotes = sum(1 for v in votes if v.value > 0)
            downvotes = sum(1 for v in votes if v.value < 0)
            total = len(votes)
            
            return {
                "upvotes": upvotes,
                "downvotes": downvotes,
                "total": total,
                "net": upvotes - downvotes
            }
        except Exception as e:
            logger.error(f"Error getting vote summary: {e}")
            return {"upvotes": 0, "downvotes": 0, "total": 0, "net": 0}
    
    async def get_period_stats(
        self,
        guild_id: int,
        start_date: datetime,
        end_date: datetime
    ) -> Dict[str, Any]:
        """Get statistics for a time period."""
        try:
            # This would need complex queries joining sessions, stats, etc.
            # Placeholder for future implementation
            logger.debug(f"Period stats placeholder for guild {guild_id}")
            return {
                "total_sessions": 0,
                "total_participants": 0,
                "total_hosts": 0,
                "active_hosts": 0
            }
        except Exception as e:
            logger.error(f"Error getting period stats: {e}")
            return {}
    
    async def get_user_summary(self, user_id: int, guild_id: int) -> Dict[str, Any]:
        """Get comprehensive summary for a user."""
        try:
            # Get user stats
            user_stats = await self.get_user_aggregate_stats(user_id, guild_id)
            
            # Get host stats
            host_stats = await self.get_host_stats(guild_id, user_id)
            
            # Get boost stats
            boost_stats = await self.get_boost_stats(guild_id, user_id)
            
            return {
                "user_id": user_id,
                "guild_id": guild_id,
                "stats": user_stats,
                "host_info": {
                    "total_sessions_hosted": host_stats.total_sessions_hosted if host_stats else 0,
                    "total_participants": host_stats.total_participants if host_stats else 0,
                    "average_rating": host_stats.average_rating if host_stats else 0.0,
                    "total_rating_count": host_stats.total_rating_count if host_stats else 0
                } if host_stats else None,
                "boost_info": {
                    "total_boosts": boost_stats.total_boosts if boost_stats else 0,
                    "current_boosts": boost_stats.boost_count if boost_stats else 0
                } if boost_stats else None
            }
        except Exception as e:
            logger.error(f"Error getting user summary: {e}")
            return {}
