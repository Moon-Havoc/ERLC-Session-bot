"""Configuration service for guild settings."""

from typing import Optional
import discord

from database import GuildConfig, GuildConfigRepository, database
from utils.logger import get_logger

logger = get_logger(__name__)


class ConfigService:
    """Service for managing guild configuration."""
    
    def __init__(self) -> None:
        """Initialize config service."""
        self.repository = GuildConfigRepository(database)
    
    async def get_guild_config(self, guild_id: int) -> Optional[GuildConfig]:
        """Get guild configuration by guild ID."""
        try:
            return await self.repository.get_by_guild(guild_id)
        except Exception as e:
            logger.error(f"Error getting guild config for {guild_id}: {e}")
            return None
    
    async def create_guild_config(
        self,
        guild_id: int,
        admin_role_id: Optional[int] = None,
        moderator_role_id: Optional[int] = None,
        host_role_id: Optional[int] = None,
        member_role_id: Optional[int] = None,
        log_channel_id: Optional[int] = None,
        session_channel_id: Optional[int] = None,
        welcome_channel_id: Optional[int] = None,
        auto_role_enabled: bool = False
    ) -> Optional[GuildConfig]:
        """Create a new guild configuration."""
        try:
            config = GuildConfig(
                guild_id=guild_id,
                admin_role_id=admin_role_id,
                moderator_role_id=moderator_role_id,
                host_role_id=host_role_id,
                member_role_id=member_role_id,
                log_channel_id=log_channel_id,
                session_channel_id=session_channel_id,
                welcome_channel_id=welcome_channel_id,
                auto_role_enabled=auto_role_enabled
            )
            return await self.repository.create(config)
        except Exception as e:
            logger.error(f"Error creating guild config for {guild_id}: {e}")
            return None
    
    async def update_guild_config(
        self,
        guild_id: int,
        admin_role_id: Optional[int] = None,
        moderator_role_id: Optional[int] = None,
        host_role_id: Optional[int] = None,
        member_role_id: Optional[int] = None,
        log_channel_id: Optional[int] = None,
        session_channel_id: Optional[int] = None,
        welcome_channel_id: Optional[int] = None,
        auto_role_enabled: Optional[bool] = None
    ) -> Optional[GuildConfig]:
        """Update guild configuration."""
        try:
            config = await self.repository.get_by_guild(guild_id)
            if not config:
                logger.warning(f"Guild config not found for {guild_id}")
                return None
            
            # Update only provided fields
            if admin_role_id is not None:
                config.admin_role_id = admin_role_id
            if moderator_role_id is not None:
                config.moderator_role_id = moderator_role_id
            if host_role_id is not None:
                config.host_role_id = host_role_id
            if member_role_id is not None:
                config.member_role_id = member_role_id
            if log_channel_id is not None:
                config.log_channel_id = log_channel_id
            if session_channel_id is not None:
                config.session_channel_id = session_channel_id
            if welcome_channel_id is not None:
                config.welcome_channel_id = welcome_channel_id
            if auto_role_enabled is not None:
                config.auto_role_enabled = auto_role_enabled
            
            return await self.repository.update(config)
        except Exception as e:
            logger.error(f"Error updating guild config for {guild_id}: {e}")
            return None
    
    async def delete_guild_config(self, guild_id: int) -> bool:
        """Delete guild configuration."""
        try:
            return await self.repository.delete(guild_id)
        except Exception as e:
            logger.error(f"Error deleting guild config for {guild_id}: {e}")
            return False
    
    async def ensure_guild_config(self, guild_id: int) -> GuildConfig:
        """Ensure guild configuration exists, create if not."""
        config = await self.get_guild_config(guild_id)
        if not config:
            logger.info(f"Creating default config for guild {guild_id}")
            config = await self.create_guild_config(guild_id)
        return config
    
    async def set_admin_role(self, guild_id: int, role_id: int) -> Optional[GuildConfig]:
        """Set admin role for guild."""
        return await self.update_guild_config(guild_id, admin_role_id=role_id)
    
    async def set_moderator_role(self, guild_id: int, role_id: int) -> Optional[GuildConfig]:
        """Set moderator role for guild."""
        return await self.update_guild_config(guild_id, moderator_role_id=role_id)
    
    async def set_host_role(self, guild_id: int, role_id: int) -> Optional[GuildConfig]:
        """Set host role for guild."""
        return await self.update_guild_config(guild_id, host_role_id=role_id)
    
    async def set_member_role(self, guild_id: int, role_id: int) -> Optional[GuildConfig]:
        """Set member role for guild."""
        return await self.update_guild_config(guild_id, member_role_id=role_id)
    
    async def set_log_channel(self, guild_id: int, channel_id: int) -> Optional[GuildConfig]:
        """Set log channel for guild."""
        return await self.update_guild_config(guild_id, log_channel_id=channel_id)
    
    async def set_session_channel(self, guild_id: int, channel_id: int) -> Optional[GuildConfig]:
        """Set session channel for guild."""
        return await self.update_guild_config(guild_id, session_channel_id=channel_id)
    
    async def set_welcome_channel(self, guild_id: int, channel_id: int) -> Optional[GuildConfig]:
        """Set welcome channel for guild."""
        return await self.update_guild_config(guild_id, welcome_channel_id=channel_id)
    
    async def toggle_auto_role(self, guild_id: int) -> Optional[bool]:
        """Toggle auto role for guild."""
        config = await self.get_guild_config(guild_id)
        if config:
            config.auto_role_enabled = not config.auto_role_enabled
            updated = await self.repository.update(config)
            return updated.auto_role_enabled if updated else None
        return None
