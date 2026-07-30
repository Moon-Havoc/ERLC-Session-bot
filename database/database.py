"""Database abstraction layer for SessionCore."""

import sqlite3
import asyncio
from contextlib import asynccontextmanager
from typing import Optional, List, Any, Dict
from datetime import datetime
from pathlib import Path

from config import config
from .models import (
    GuildConfig, Branding, Session, SessionParticipant, SessionStats,
    Vote, Boost, Host, SessionStatus
)


class Database:
    """Database connection and query manager."""
    
    def __init__(self, db_path: str = None) -> None:
        """Initialize database connection."""
        self.db_path = db_path or config.database_path
        self._local = asyncio.Queue()
        self._lock = asyncio.Lock()
    
    async def initialize(self) -> None:
        """Initialize database connection and ensure schema exists."""
        Path(self.db_path).parent.mkdir(parents=True, exist_ok=True)
        
    @asynccontextmanager
    async def get_connection(self):
        """Get a database connection from the pool."""
        async with self._lock:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            try:
                yield conn
            finally:
                conn.close()
    
    async def execute(self, query: str, params: tuple = ()) -> sqlite3.Cursor:
        """Execute a SQL query."""
        async with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, params)
            conn.commit()
            return cursor
    
    async def fetchone(self, query: str, params: tuple = ()) -> Optional[sqlite3.Row]:
        """Fetch a single row from the database."""
        async with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, params)
            return cursor.fetchone()
    
    async def fetchall(self, query: str, params: tuple = ()) -> List[sqlite3.Row]:
        """Fetch all rows from the database."""
        async with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, params)
            return cursor.fetchall()
    
    async def fetchval(self, query: str, params: tuple = ()) -> Any:
        """Fetch a single value from the database."""
        row = await self.fetchone(query, params)
        return row[0] if row else None


class GuildConfigRepository:
    """Repository for guild configuration operations."""
    
    def __init__(self, db: Database) -> None:
        self.db = db
    
    async def create(self, config: GuildConfig) -> GuildConfig:
        """Create a new guild configuration."""
        query = """
            INSERT INTO guild_config (
                guild_id, community_name, community_description, logo_url, embed_color,
                footer_text, footer_icon_url, community_emoji, website_url, discord_invite,
                session_channel_id, logs_channel_id, welcome_channel_id,
                admin_role_id, management_role_id, host_role_id, moderator_role_id, member_role_id,
                timezone, auto_role_enabled, api_enabled, api_url, api_key,
                created_at, updated_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """
        await self.db.execute(query, (
            config.guild_id, config.community_name, config.community_description,
            config.logo_url, config.embed_color, config.footer_text, config.footer_icon_url,
            config.community_emoji, config.website_url, config.discord_invite,
            config.session_channel_id, config.logs_channel_id, config.welcome_channel_id,
            config.admin_role_id, config.management_role_id, config.host_role_id,
            config.moderator_role_id, config.member_role_id, config.timezone,
            config.auto_role_enabled, config.api_enabled, config.api_url, config.api_key,
            config.created_at, config.updated_at
        ))
        return config
    
    async def get_by_guild(self, guild_id: int) -> Optional[GuildConfig]:
        """Get guild configuration by guild ID."""
        query = "SELECT * FROM guild_config WHERE guild_id = ?"
        row = await self.db.fetchone(query, (guild_id,))
        if row:
            return GuildConfig(**dict(row))
        return None
    
    async def update(self, config: GuildConfig) -> GuildConfig:
        """Update guild configuration."""
        query = """
            UPDATE guild_config SET
                community_name = ?, community_description = ?, logo_url = ?, embed_color = ?,
                footer_text = ?, footer_icon_url = ?, community_emoji = ?, website_url = ?, discord_invite = ?,
                session_channel_id = ?, logs_channel_id = ?, welcome_channel_id = ?,
                admin_role_id = ?, management_role_id = ?, host_role_id = ?, moderator_role_id = ?, member_role_id = ?,
                timezone = ?, auto_role_enabled = ?, api_enabled = ?, api_url = ?, api_key = ?, updated_at = ?
            WHERE guild_id = ?
        """
        config.updated_at = datetime.utcnow()
        await self.db.execute(query, (
            config.community_name, config.community_description, config.logo_url, config.embed_color,
            config.footer_text, config.footer_icon_url, config.community_emoji, config.website_url, config.discord_invite,
            config.session_channel_id, config.logs_channel_id, config.welcome_channel_id,
            config.admin_role_id, config.management_role_id, config.host_role_id,
            config.moderator_role_id, config.member_role_id, config.timezone,
            config.auto_role_enabled, config.api_enabled, config.api_url, config.api_key,
            config.updated_at, config.guild_id
        ))
        return config
    
    async def delete(self, guild_id: int) -> bool:
        """Delete guild configuration."""
        query = "DELETE FROM guild_config WHERE guild_id = ?"
        cursor = await self.db.execute(query, (guild_id,))
        return cursor.rowcount > 0


class BrandingRepository:
    """Repository for branding operations."""
    
    def __init__(self, db: Database) -> None:
        self.db = db
    
    async def create(self, branding: Branding) -> Branding:
        """Create new branding configuration."""
        query = """
            INSERT INTO branding (
                guild_id, community_name, description, logo_url, embed_color,
                footer_text, footer_icon_url, custom_emoji, website_url,
                invite_link, created_at, updated_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """
        await self.db.execute(query, (
            branding.guild_id, branding.community_name, branding.description,
            branding.logo_url, branding.embed_color, branding.footer_text,
            branding.footer_icon_url, branding.custom_emoji,
            branding.website_url, branding.invite_link,
            branding.created_at, branding.updated_at
        ))
        return branding
    
    async def get_by_guild(self, guild_id: int) -> Optional[Branding]:
        """Get branding by guild ID."""
        query = "SELECT * FROM branding WHERE guild_id = ?"
        row = await self.db.fetchone(query, (guild_id,))
        if row:
            return Branding(**dict(row))
        return None
    
    async def update(self, branding: Branding) -> Branding:
        """Update branding configuration."""
        query = """
            UPDATE branding SET
                community_name = ?, description = ?, logo_url = ?,
                embed_color = ?, footer_text = ?, footer_icon_url = ?,
                custom_emoji = ?, website_url = ?, invite_link = ?,
                updated_at = ?
            WHERE guild_id = ?
        """
        branding.updated_at = datetime.utcnow()
        await self.db.execute(query, (
            branding.community_name, branding.description, branding.logo_url,
            branding.embed_color, branding.footer_text, branding.footer_icon_url,
            branding.custom_emoji, branding.website_url, branding.invite_link,
            branding.updated_at, branding.guild_id
        ))
        return branding
    
    async def delete(self, guild_id: int) -> bool:
        """Delete branding configuration."""
        query = "DELETE FROM branding WHERE guild_id = ?"
        cursor = await self.db.execute(query, (guild_id,))
        return cursor.rowcount > 0


class SessionRepository:
    """Repository for session operations."""
    
    def __init__(self, db: Database) -> None:
        self.db = db
    
    async def create(self, session: Session) -> Session:
        """Create a new session."""
        query = """
            INSERT INTO sessions (
                guild_id, host_id, server_code, notes, started_at, ended_at,
                status, session_channel_id, session_message_id, vote_count,
                boost_count, duration, created_at, updated_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """
        cursor = await self.db.execute(query, (
            session.guild_id, session.host_id, session.server_code, session.notes,
            session.started_at, session.ended_at, session.status.value,
            session.session_channel_id, session.session_message_id,
            session.vote_count, session.boost_count, session.duration,
            session.created_at, session.updated_at
        ))
        session.id = cursor.lastrowid
        return session
    
    async def get_by_id(self, session_id: int) -> Optional[Session]:
        """Get session by ID."""
        query = "SELECT * FROM sessions WHERE id = ?"
        row = await self.db.fetchone(query, (session_id,))
        if row:
            data = dict(row)
            data['status'] = SessionStatus(data['status'])
            return Session(**data)
        return None
    
    async def get_by_guild(self, guild_id: int, limit: int = 50) -> List[Session]:
        """Get sessions for a guild."""
        query = "SELECT * FROM sessions WHERE guild_id = ? ORDER BY created_at DESC LIMIT ?"
        rows = await self.db.fetchall(query, (guild_id, limit))
        sessions = []
        for row in rows:
            data = dict(row)
            data['status'] = SessionStatus(data['status'])
            sessions.append(Session(**data))
        return sessions
    
    async def get_active_session(self, guild_id: int) -> Optional[Session]:
        """Get the active session for a guild (only one active session per guild)."""
        query = """
            SELECT * FROM sessions 
            WHERE guild_id = ? AND status = ? 
            ORDER BY created_at DESC LIMIT 1
        """
        row = await self.db.fetchone(query, (guild_id, SessionStatus.ACTIVE.value))
        if row:
            data = dict(row)
            data['status'] = SessionStatus(data['status'])
            return Session(**data)
        return None
    
    async def get_all_active_sessions(self) -> List[Session]:
        """Get all active sessions across all guilds."""
        query = """
            SELECT * FROM sessions 
            WHERE status = ? 
            ORDER BY created_at DESC
        """
        rows = await self.db.fetchall(query, (SessionStatus.ACTIVE.value,))
        sessions = []
        for row in rows:
            data = dict(row)
            data['status'] = SessionStatus(data['status'])
            sessions.append(Session(**data))
        return sessions
    
    async def update(self, session: Session) -> Session:
        """Update session."""
        query = """
            UPDATE sessions SET
                server_code = ?, notes = ?, started_at = ?, ended_at = ?,
                status = ?, session_channel_id = ?, session_message_id = ?,
                vote_count = ?, boost_count = ?, duration = ?, updated_at = ?
            WHERE id = ?
        """
        session.updated_at = datetime.utcnow()
        await self.db.execute(query, (
            session.server_code, session.notes, session.started_at, session.ended_at,
            session.status.value, session.session_channel_id, session.session_message_id,
            session.vote_count, session.boost_count, session.duration,
            session.updated_at, session.id
        ))
        return session
    
    async def delete(self, session_id: int) -> bool:
        """Delete session."""
        query = "DELETE FROM sessions WHERE id = ?"
        cursor = await self.db.execute(query, (session_id,))
        return cursor.rowcount > 0


class SessionParticipantRepository:
    """Repository for session participant operations."""
    
    def __init__(self, db: Database) -> None:
        self.db = db
    
    async def add_participant(self, participant: SessionParticipant) -> SessionParticipant:
        """Add participant to session."""
        query = """
            INSERT INTO session_participants (
                session_id, user_id, joined_at, left_at, attendance_minutes
            ) VALUES (?, ?, ?, ?, ?)
        """
        cursor = await self.db.execute(query, (
            participant.session_id, participant.user_id, participant.joined_at,
            participant.left_at, participant.attendance_minutes
        ))
        participant.id = cursor.lastrowid
        return participant
    
    async def get_participants(self, session_id: int) -> List[SessionParticipant]:
        """Get all participants for a session."""
        query = "SELECT * FROM session_participants WHERE session_id = ?"
        rows = await self.db.fetchall(query, (session_id,))
        return [SessionParticipant(**dict(row)) for row in rows]
    
    async def remove_participant(self, session_id: int, user_id: int) -> bool:
        """Remove participant from session."""
        query = "DELETE FROM session_participants WHERE session_id = ? AND user_id = ?"
        cursor = await self.db.execute(query, (session_id, user_id))
        return cursor.rowcount > 0


class SessionStatsRepository:
    """Repository for session statistics operations."""
    
    def __init__(self, db: Database) -> None:
        self.db = db
    
    async def create(self, stats: SessionStats) -> SessionStats:
        """Create new session statistics."""
        query = """
            INSERT INTO session_stats (
                session_id, user_id, metric_name, metric_value, recorded_at
            ) VALUES (?, ?, ?, ?, ?)
        """
        cursor = await self.db.execute(query, (
            stats.session_id, stats.user_id, stats.metric_name,
            stats.metric_value, stats.recorded_at
        ))
        stats.id = cursor.lastrowid
        return stats
    
    async def get_by_session(self, session_id: int) -> List[SessionStats]:
        """Get statistics for a session."""
        query = "SELECT * FROM session_stats WHERE session_id = ?"
        rows = await self.db.fetchall(query, (session_id,))
        return [SessionStats(**dict(row)) for row in rows]
    
    async def get_by_user(self, user_id: int, limit: int = 100) -> List[SessionStats]:
        """Get statistics for a user."""
        query = "SELECT * FROM session_stats WHERE user_id = ? ORDER BY recorded_at DESC LIMIT ?"
        rows = await self.db.fetchall(query, (user_id, limit))
        return [SessionStats(**dict(row)) for row in rows]


class VoteRepository:
    """Repository for vote operations."""
    
    def __init__(self, db: Database) -> None:
        self.db = db
    
    async def create(self, vote: Vote) -> Vote:
        """Create a new vote."""
        query = """
            INSERT INTO votes (guild_id, user_id, target_id, vote_type, value, created_at)
            VALUES (?, ?, ?, ?, ?, ?)
        """
        cursor = await self.db.execute(query, (
            vote.guild_id, vote.user_id, vote.target_id,
            vote.vote_type, vote.value, vote.created_at
        ))
        vote.id = cursor.lastrowid
        return vote
    
    async def get_user_vote(self, user_id: int, target_id: int, vote_type: str) -> Optional[Vote]:
        """Get a user's vote on a target."""
        query = """
            SELECT * FROM votes 
            WHERE user_id = ? AND target_id = ? AND vote_type = ?
        """
        row = await self.db.fetchone(query, (user_id, target_id, vote_type))
        if row:
            return Vote(**dict(row))
        return None
    
    async def get_votes(self, target_id: int, vote_type: str) -> List[Vote]:
        """Get all votes for a target."""
        query = """
            SELECT * FROM votes 
            WHERE target_id = ? AND vote_type = ?
        """
        rows = await self.db.fetchall(query, (target_id, vote_type))
        return [Vote(**dict(row)) for row in rows]
    
    async def delete(self, vote_id: int) -> bool:
        """Delete a vote."""
        query = "DELETE FROM votes WHERE id = ?"
        cursor = await self.db.execute(query, (vote_id,))
        return cursor.rowcount > 0


class BoostRepository:
    """Repository for boost operations."""
    
    def __init__(self, db: Database) -> None:
        self.db = db
    
    async def create(self, boost: Boost) -> Boost:
        """Create new boost record."""
        query = """
            INSERT INTO boosts (
                guild_id, user_id, boost_count, total_boosts,
                last_boost_at, created_at, updated_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?)
        """
        await self.db.execute(query, (
            boost.guild_id, boost.user_id, boost.boost_count,
            boost.total_boosts, boost.last_boost_at,
            boost.created_at, boost.updated_at
        ))
        return boost
    
    async def get_by_user(self, guild_id: int, user_id: int) -> Optional[Boost]:
        """Get boost record for a user."""
        query = "SELECT * FROM boosts WHERE guild_id = ? AND user_id = ?"
        row = await self.db.fetchone(query, (guild_id, user_id))
        if row:
            return Boost(**dict(row))
        return None
    
    async def update(self, boost: Boost) -> Boost:
        """Update boost record."""
        query = """
            UPDATE boosts SET
                boost_count = ?, total_boosts = ?, last_boost_at = ?, updated_at = ?
            WHERE guild_id = ? AND user_id = ?
        """
        boost.updated_at = datetime.utcnow()
        await self.db.execute(query, (
            boost.boost_count, boost.total_boosts, boost.last_boost_at,
            boost.updated_at, boost.guild_id, boost.user_id
        ))
        return boost


class HostRepository:
    """Repository for host operations."""
    
    def __init__(self, db: Database) -> None:
        self.db = db
    
    async def create(self, host: Host) -> Host:
        """Create new host record."""
        query = """
            INSERT INTO hosts (
                guild_id, user_id, total_sessions_hosted, total_participants,
                average_rating, total_rating_count, is_active, created_at, updated_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """
        await self.db.execute(query, (
            host.guild_id, host.user_id, host.total_sessions_hosted,
            host.total_participants, host.average_rating,
            host.total_rating_count, host.is_active,
            host.created_at, host.updated_at
        ))
        return host
    
    async def get_by_user(self, guild_id: int, user_id: int) -> Optional[Host]:
        """Get host record for a user."""
        query = "SELECT * FROM hosts WHERE guild_id = ? AND user_id = ?"
        row = await self.db.fetchone(query, (guild_id, user_id))
        if row:
            return Host(**dict(row))
        return None
    
    async def get_active_hosts(self, guild_id: int) -> List[Host]:
        """Get all active hosts for a guild."""
        query = "SELECT * FROM hosts WHERE guild_id = ? AND is_active = ?"
        rows = await self.db.fetchall(query, (guild_id, True))
        return [Host(**dict(row)) for row in rows]
    
    async def update(self, host: Host) -> Host:
        """Update host record."""
        query = """
            UPDATE hosts SET
                total_sessions_hosted = ?, total_participants = ?,
                average_rating = ?, total_rating_count = ?,
                is_active = ?, updated_at = ?
            WHERE guild_id = ? AND user_id = ?
        """
        host.updated_at = datetime.utcnow()
        await self.db.execute(query, (
            host.total_sessions_hosted, host.total_participants,
            host.average_rating, host.total_rating_count,
            host.is_active, host.updated_at, host.guild_id, host.user_id
        ))
        return host


# Global database instance
database = Database()
