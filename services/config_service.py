"""Configuration service for guild settings with caching."""

from __future__ import annotations

from typing import Optional
import discord
from datetime import datetime

from database import GuildConfig, GuildConfigRepository, database
from utils.logger import get_logger

logger = get_logger(__name__)


class ConfigService:
    """Service for managing guild configuration with caching."""
    
    def __init__(self) -> None:
        """Initialize config service with cache."""
        self.repository = GuildConfigRepository(database)
        self._cache: dict[int, GuildConfig] = {}
        self._cache_ttl: int = 300  # 5 minutes
        self._cache_timestamps: dict[int, datetime] = {}
    
    def _is_cache_valid(self, guild_id: int) -> bool:
        """Check if cache entry is still valid."""
        if guild_id not in self._cache_timestamps:
            return False
        
        age = (datetime.utcnow() - self._cache_timestamps[guild_id]).total_seconds()
        return age < self._cache_ttl
    
    def _set_cache(self, config: GuildConfig) -> None:
        """Set configuration in cache."""
        self._cache[config.guild_id] = config
        self._cache_timestamps[config.guild_id] = datetime.utcnow()
    
    def _invalidate_cache(self, guild_id: int) -> None:
        """Invalidate cache for a guild."""
        if guild_id in self._cache:
            del self._cache[guild_id]
        if guild_id in self._cache_timestamps:
            del self._cache_timestamps[guild_id]
    
    def _clear_cache(self) -> None:
        """Clear all cache entries."""
        self._cache.clear()
        self._cache_timestamps.clear()
    
    async def get_guild_config(self, guild_id: int, use_cache: bool = True) -> Optional[GuildConfig]:
        """Get guild configuration by guild ID with caching."""
        if use_cache and self._is_cache_valid(guild_id):
            return self._cache[guild_id]
        
        try:
            config = await self.repository.get_by_guild(guild_id)
            if config:
                self._set_cache(config)
            return config
        except Exception as e:
            logger.error(f"Error getting guild config for {guild_id}: {e}")
            return None
    
    async def create_guild_config(
        self,
        guild_id: int,
        community_name: str = "Community",
        community_description: Optional[str] = None,
        logo_url: Optional[str] = None,
        embed_color: int = 0x5865F2,
        footer_text: Optional[str] = None,
        footer_icon_url: Optional[str] = None,
        community_emoji: Optional[str] = None,
        website_url: Optional[str] = None,
        discord_invite: Optional[str] = None,
        session_channel_id: Optional[int] = None,
        logs_channel_id: Optional[int] = None,
        welcome_channel_id: Optional[int] = None,
        admin_role_id: Optional[int] = None,
        management_role_id: Optional[int] = None,
        host_role_id: Optional[int] = None,
        moderator_role_id: Optional[int] = None,
        member_role_id: Optional[int] = None,
        timezone: str = "UTC",
        auto_role_enabled: bool = False,
        api_enabled: bool = False,
        api_url: Optional[str] = None,
        api_key: Optional[str] = None
    ) -> Optional[GuildConfig]:
        """Create a new guild configuration."""
        try:
            config = GuildConfig(
                guild_id=guild_id,
                community_name=community_name,
                community_description=community_description,
                logo_url=logo_url,
                embed_color=embed_color,
                footer_text=footer_text,
                footer_icon_url=footer_icon_url,
                community_emoji=community_emoji,
                website_url=website_url,
                discord_invite=discord_invite,
                session_channel_id=session_channel_id,
                logs_channel_id=logs_channel_id,
                welcome_channel_id=welcome_channel_id,
                admin_role_id=admin_role_id,
                management_role_id=management_role_id,
                host_role_id=host_role_id,
                moderator_role_id=moderator_role_id,
                member_role_id=member_role_id,
                timezone=timezone,
                auto_role_enabled=auto_role_enabled,
                api_enabled=api_enabled,
                api_url=api_url,
                api_key=api_key
            )
            created = await self.repository.create(config)
            self._set_cache(created)
            logger.info(f"Created guild config for {guild_id}")
            return created
        except Exception as e:
            logger.error(f"Error creating guild config for {guild_id}: {e}")
            return None
    
    async def ensure_guild_config(self, guild_id: int, guild_name: str = "Community") -> GuildConfig:
        """Ensure guild configuration exists, create with defaults if not."""
        config = await self.get_guild_config(guild_id)
        if not config:
            logger.info(f"Creating default config for guild {guild_id}")
            config = await self.create_guild_config(guild_id, community_name=guild_name)
        return config
    
    # Branding helper methods
    async def set_community_name(self, guild_id: int, name: str) -> Optional[GuildConfig]:
        """Set community name."""
        config = await self.get_guild_config(guild_id, use_cache=False)
        if config:
            config.community_name = name
            updated = await self.repository.update(config)
            self._invalidate_cache(guild_id)
            if updated:
                self._set_cache(updated)
            return updated
        return None
    
    async def set_community_description(self, guild_id: int, description: str) -> Optional[GuildConfig]:
        """Set community description."""
        config = await self.get_guild_config(guild_id, use_cache=False)
        if config:
            config.community_description = description
            updated = await self.repository.update(config)
            self._invalidate_cache(guild_id)
            if updated:
                self._set_cache(updated)
            return updated
        return None
    
    async def set_logo_url(self, guild_id: int, url: str) -> Optional[GuildConfig]:
        """Set logo URL."""
        config = await self.get_guild_config(guild_id, use_cache=False)
        if config:
            config.logo_url = url
            updated = await self.repository.update(config)
            self._invalidate_cache(guild_id)
            if updated:
                self._set_cache(updated)
            return updated
        return None
    
    async def set_embed_color(self, guild_id: int, color: int) -> Optional[GuildConfig]:
        """Set embed color."""
        config = await self.get_guild_config(guild_id, use_cache=False)
        if config:
            config.embed_color = color
            updated = await self.repository.update(config)
            self._invalidate_cache(guild_id)
            if updated:
                self._set_cache(updated)
            return updated
        return None
    
    async def set_footer_text(self, guild_id: int, text: str) -> Optional[GuildConfig]:
        """Set footer text."""
        config = await self.get_guild_config(guild_id, use_cache=False)
        if config:
            config.footer_text = text
            updated = await self.repository.update(config)
            self._invalidate_cache(guild_id)
            if updated:
                self._set_cache(updated)
            return updated
        return None
    
    async def set_footer_icon_url(self, guild_id: int, url: str) -> Optional[GuildConfig]:
        """Set footer icon URL."""
        config = await self.get_guild_config(guild_id, use_cache=False)
        if config:
            config.footer_icon_url = url
            updated = await self.repository.update(config)
            self._invalidate_cache(guild_id)
            if updated:
                self._set_cache(updated)
            return updated
        return None
    
    async def set_community_emoji(self, guild_id: int, emoji: str) -> Optional[GuildConfig]:
        """Set community emoji."""
        config = await self.get_guild_config(guild_id, use_cache=False)
        if config:
            config.community_emoji = emoji
            updated = await self.repository.update(config)
            self._invalidate_cache(guild_id)
            if updated:
                self._set_cache(updated)
            return updated
        return None
    
    async def set_website_url(self, guild_id: int, url: str) -> Optional[GuildConfig]:
        """Set website URL."""
        config = await self.get_guild_config(guild_id, use_cache=False)
        if config:
            config.website_url = url
            updated = await self.repository.update(config)
            self._invalidate_cache(guild_id)
            if updated:
                self._set_cache(updated)
            return updated
        return None
    
    async def set_discord_invite(self, guild_id: int, invite: str) -> Optional[GuildConfig]:
        """Set Discord invite link."""
        config = await self.get_guild_config(guild_id, use_cache=False)
        if config:
            config.discord_invite = invite
            updated = await self.repository.update(config)
            self._invalidate_cache(guild_id)
            if updated:
                self._set_cache(updated)
            return updated
        return None
    
    # Channel helper methods
    async def set_session_channel(self, guild_id: int, channel_id: int) -> Optional[GuildConfig]:
        """Set session channel."""
        config = await self.get_guild_config(guild_id, use_cache=False)
        if config:
            config.session_channel_id = channel_id
            updated = await self.repository.update(config)
            self._invalidate_cache(guild_id)
            if updated:
                self._set_cache(updated)
            return updated
        return None
    
    async def set_logs_channel(self, guild_id: int, channel_id: int) -> Optional[GuildConfig]:
        """Set logs channel."""
        config = await self.get_guild_config(guild_id, use_cache=False)
        if config:
            config.logs_channel_id = channel_id
            updated = await self.repository.update(config)
            self._invalidate_cache(guild_id)
            if updated:
                self._set_cache(updated)
            return updated
        return None
    
    async def set_welcome_channel(self, guild_id: int, channel_id: int) -> Optional[GuildConfig]:
        """Set welcome channel."""
        config = await self.get_guild_config(guild_id, use_cache=False)
        if config:
            config.welcome_channel_id = channel_id
            updated = await self.repository.update(config)
            self._invalidate_cache(guild_id)
            if updated:
                self._set_cache(updated)
            return updated
        return None
    
    # Role helper methods
    async def set_admin_role(self, guild_id: int, role_id: int) -> Optional[GuildConfig]:
        """Set admin role."""
        config = await self.get_guild_config(guild_id, use_cache=False)
        if config:
            config.admin_role_id = role_id
            updated = await self.repository.update(config)
            self._invalidate_cache(guild_id)
            if updated:
                self._set_cache(updated)
            return updated
        return None
    
    async def set_management_role(self, guild_id: int, role_id: int) -> Optional[GuildConfig]:
        """Set management role."""
        config = await self.get_guild_config(guild_id, use_cache=False)
        if config:
            config.management_role_id = role_id
            updated = await self.repository.update(config)
            self._invalidate_cache(guild_id)
            if updated:
                self._set_cache(updated)
            return updated
        return None
    
    async def set_host_role(self, guild_id: int, role_id: int) -> Optional[GuildConfig]:
        """Set host role."""
        config = await self.get_guild_config(guild_id, use_cache=False)
        if config:
            config.host_role_id = role_id
            updated = await self.repository.update(config)
            self._invalidate_cache(guild_id)
            if updated:
                self._set_cache(updated)
            return updated
        return None
    
    async def set_moderator_role(self, guild_id: int, role_id: int) -> Optional[GuildConfig]:
        """Set moderator role."""
        config = await self.get_guild_config(guild_id, use_cache=False)
        if config:
            config.moderator_role_id = role_id
            updated = await self.repository.update(config)
            self._invalidate_cache(guild_id)
            if updated:
                self._set_cache(updated)
            return updated
        return None
    
    async def set_member_role(self, guild_id: int, role_id: int) -> Optional[GuildConfig]:
        """Set member role."""
        config = await self.get_guild_config(guild_id, use_cache=False)
        if config:
            config.member_role_id = role_id
            updated = await self.repository.update(config)
            self._invalidate_cache(guild_id)
            if updated:
                self._set_cache(updated)
            return updated
        return None
    
    # Other configuration methods
    async def set_timezone(self, guild_id: int, timezone: str) -> Optional[GuildConfig]:
        """Set timezone."""
        config = await self.get_guild_config(guild_id, use_cache=False)
        if config:
            config.timezone = timezone
            updated = await self.repository.update(config)
            self._invalidate_cache(guild_id)
            if updated:
                self._set_cache(updated)
            return updated
        return None
    
    async def toggle_auto_role(self, guild_id: int) -> Optional[bool]:
        """Toggle auto role."""
        config = await self.get_guild_config(guild_id, use_cache=False)
        if config:
            config.auto_role_enabled = not config.auto_role_enabled
            updated = await self.repository.update(config)
            self._invalidate_cache(guild_id)
            if updated:
                self._set_cache(updated)
            return updated.auto_role_enabled if updated else None
        return None
    
    async def set_api_config(self, guild_id: int, enabled: bool, url: Optional[str] = None, key: Optional[str] = None) -> Optional[GuildConfig]:
        """Set API configuration."""
        config = await self.get_guild_config(guild_id, use_cache=False)
        if config:
            config.api_enabled = enabled
            config.api_url = url
            config.api_key = key
            updated = await self.repository.update(config)
            self._invalidate_cache(guild_id)
            if updated:
                self._set_cache(updated)
            return updated
        return None
    
    async def delete_guild_config(self, guild_id: int) -> bool:
        """Delete guild configuration."""
        try:
            result = await self.repository.delete(guild_id)
            self._invalidate_cache(guild_id)
            return result
        except Exception as e:
            logger.error(f"Error deleting guild config for {guild_id}: {e}")
            return False
