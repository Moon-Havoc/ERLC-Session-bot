"""Database models for SessionCore."""

from dataclasses import dataclass
from datetime import datetime
from typing import Optional
from enum import Enum


class SessionStatus(Enum):
    """Status of a session."""
    ACTIVE = "active"
    ENDED = "ended"
    CANCELLED = "cancelled"


@dataclass
class GuildConfig:
    """Guild-specific configuration including branding."""
    guild_id: int
    # Branding fields
    community_name: str = "Community"
    community_description: Optional[str] = None
    logo_url: Optional[str] = None
    embed_color: int = 0x5865F2  # Default Discord blurple
    footer_text: Optional[str] = None
    footer_icon_url: Optional[str] = None
    community_emoji: Optional[str] = None
    website_url: Optional[str] = None
    discord_invite: Optional[str] = None
    # Channel configuration
    session_channel_id: Optional[int] = None
    logs_channel_id: Optional[int] = None
    welcome_channel_id: Optional[int] = None
    # Role configuration
    admin_role_id: Optional[int] = None
    management_role_id: Optional[int] = None
    host_role_id: Optional[int] = None
    moderator_role_id: Optional[int] = None
    member_role_id: Optional[int] = None
    # Other configuration
    timezone: str = "UTC"
    auto_role_enabled: bool = False
    api_enabled: bool = False
    api_url: Optional[str] = None
    api_key: Optional[str] = None
    created_at: datetime = None
    updated_at: datetime = None
    
    def __post_init__(self) -> None:
        if self.created_at is None:
            self.created_at = datetime.utcnow()
        if self.updated_at is None:
            self.updated_at = datetime.utcnow()


@dataclass
class Branding:
    """Community branding configuration (deprecated - use GuildConfig)."""
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
    
    @classmethod
    def from_guild_config(cls, config: GuildConfig) -> "Branding":
        """Create Branding from GuildConfig for backward compatibility."""
        return cls(
            guild_id=config.guild_id,
            community_name=config.community_name,
            description=config.community_description,
            logo_url=config.logo_url,
            embed_color=config.embed_color,
            footer_text=config.footer_text,
            footer_icon_url=config.footer_icon_url,
            custom_emoji=config.community_emoji,
            website_url=config.website_url,
            invite_link=config.discord_invite,
            created_at=config.created_at,
            updated_at=config.updated_at
        )


@dataclass
class Session:
    """Training or practice session."""
    id: Optional[int] = None
    guild_id: int = 0
    host_id: int = 0
    server_code: str = ""
    notes: Optional[str] = None
    started_at: Optional[datetime] = None
    ended_at: Optional[datetime] = None
    status: SessionStatus = SessionStatus.ACTIVE
    session_channel_id: Optional[int] = None
    session_message_id: Optional[int] = None
    vote_count: int = 0
    boost_count: int = 0
    duration: Optional[int] = None  # Duration in seconds
    created_at: datetime = None
    updated_at: datetime = None
    
    def __post_init__(self) -> None:
        if self.created_at is None:
            self.created_at = datetime.utcnow()
        if self.updated_at is None:
            self.updated_at = datetime.utcnow()
    
    @property
    def is_active(self) -> bool:
        """Check if session is currently active."""
        return self.status == SessionStatus.ACTIVE
    
    @property
    def duration_str(self) -> str:
        """Get formatted duration string."""
        if self.duration:
            hours, remainder = divmod(self.duration, 3600)
            minutes, seconds = divmod(remainder, 60)
            if hours > 0:
                return f"{hours}h {minutes}m {seconds}s"
            elif minutes > 0:
                return f"{minutes}m {seconds}s"
            else:
                return f"{seconds}s"
        return "0s"


@dataclass
class SessionVote:
    """Vote for a session."""
    id: Optional[int] = None
    guild_id: int = 0
    session_id: int = 0
    user_id: int = 0
    created_at: datetime = None
    
    def __post_init__(self) -> None:
        if self.created_at is None:
            self.created_at = datetime.utcnow()


@dataclass
class SessionBoost:
    """Boost for a session."""
    id: Optional[int] = None
    guild_id: int = 0
    session_id: int = 0
    user_id: int = 0
    note: Optional[str] = None
    created_at: datetime = None
    
    def __post_init__(self) -> None:
        if self.created_at is None:
            self.created_at = datetime.utcnow()


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
