"""Database models for SessionCore."""

from dataclasses import dataclass
from datetime import datetime
from typing import Optional
from enum import Enum


class SessionStatus(Enum):
    """Status of a session."""
    ACTIVE = "active"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


@dataclass
class GuildConfig:
    """Guild-specific configuration."""
    guild_id: int
    admin_role_id: Optional[int] = None
    moderator_role_id: Optional[int] = None
    host_role_id: Optional[int] = None
    member_role_id: Optional[int] = None
    log_channel_id: Optional[int] = None
    session_channel_id: Optional[int] = None
    welcome_channel_id: Optional[int] = None
    auto_role_enabled: bool = False
    created_at: datetime = None
    updated_at: datetime = None
    
    def __post_init__(self) -> None:
        if self.created_at is None:
            self.created_at = datetime.utcnow()
        if self.updated_at is None:
            self.updated_at = datetime.utcnow()


@dataclass
class Branding:
    """Community branding configuration."""
    guild_id: int
    community_name: str
    description: Optional[str] = None
    logo_url: Optional[str] = None
    embed_color: int = 0x5865F2  # Default Discord blurple
    footer_text: Optional[str] = None
    footer_icon_url: Optional[str] = None
    custom_emoji: Optional[str] = None
    website_url: Optional[str] = None
    invite_link: Optional[str] = None
    created_at: datetime = None
    updated_at: datetime = None
    
    def __post_init__(self) -> None:
        if self.created_at is None:
            self.created_at = datetime.utcnow()
        if self.updated_at is None:
            self.updated_at = datetime.utcnow()


@dataclass
class Session:
    """Training or practice session."""
    id: Optional[int] = None
    guild_id: int = 0
    host_id: int = 0
    session_type: str = ""
    title: str = ""
    description: Optional[str] = None
    scheduled_time: Optional[datetime] = None
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    status: SessionStatus = SessionStatus.ACTIVE
    max_participants: Optional[int] = None
    current_participants: int = 0
    message_id: Optional[int] = None
    channel_id: Optional[int] = None
    created_at: datetime = None
    updated_at: datetime = None
    
    def __post_init__(self) -> None:
        if self.created_at is None:
            self.created_at = datetime.utcnow()
        if self.updated_at is None:
            self.updated_at = datetime.utcnow()


@dataclass
class SessionParticipant:
    """Participant in a session."""
    id: Optional[int] = None
    session_id: int = 0
    user_id: int = 0
    joined_at: datetime = None
    left_at: Optional[datetime] = None
    attendance_minutes: int = 0
    
    def __post_init__(self) -> None:
        if self.joined_at is None:
            self.joined_at = datetime.utcnow()


@dataclass
class SessionStats:
    """Statistics for a session."""
    id: Optional[int] = None
    session_id: int = 0
    user_id: int = 0
    metric_name: str = ""
    metric_value: float = 0.0
    recorded_at: datetime = None
    
    def __post_init__(self) -> None:
        if self.recorded_at is None:
            self.recorded_at = datetime.utcnow()


@dataclass
class Vote:
    """Vote for sessions or other decisions."""
    id: Optional[int] = None
    guild_id: int = 0
    user_id: int = 0
    target_id: int = 0  # Can be session_id or other target
    vote_type: str = ""
    value: int = 0  # 1 for upvote, -1 for downvote
    created_at: datetime = None
    
    def __post_init__(self) -> None:
        if self.created_at is None:
            self.created_at = datetime.utcnow()


@dataclass
class Boost:
    """Server boost tracking."""
    id: Optional[int] = None
    guild_id: int = 0
    user_id: int = 0
    boost_count: int = 0
    total_boosts: int = 0
    last_boost_at: Optional[datetime] = None
    created_at: datetime = None
    updated_at: datetime = None
    
    def __post_init__(self) -> None:
        if self.created_at is None:
            self.created_at = datetime.utcnow()
        if self.updated_at is None:
            self.updated_at = datetime.utcnow()


@dataclass
class Host:
    """Host information and stats."""
    id: Optional[int] = None
    guild_id: int = 0
    user_id: int = 0
    total_sessions_hosted: int = 0
    total_participants: int = 0
    average_rating: float = 0.0
    total_rating_count: int = 0
    is_active: bool = True
    created_at: datetime = None
    updated_at: datetime = None
    
    def __post_init__(self) -> None:
        if self.created_at is None:
            self.created_at = datetime.utcnow()
        if self.updated_at is None:
            self.updated_at = datetime.utcnow()
