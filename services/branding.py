"""Branding service for community customization with embed helpers."""

from __future__ import annotations

from typing import Optional
import discord

from database import GuildConfig
from services.config_service import ConfigService
from utils.logger import get_logger

logger = get_logger(__name__)


class BrandingService:
    """Service for managing community branding and creating branded embeds."""
    
    def __init__(self) -> None:
        """Initialize branding service."""
        self.config_service = ConfigService()
    
    async def get_branding_config(self, guild_id: int) -> Optional[GuildConfig]:
        """Get guild configuration which contains branding settings."""
        return await self.config_service.get_guild_config(guild_id)
    
    async def create_embed(
        self,
        guild_id: int,
        title: str,
        description: Optional[str] = None,
        color: Optional[int] = None,
        fields: Optional[list] = None,
        footer_text: Optional[str] = None,
        footer_icon: Optional[str] = None,
        thumbnail: Optional[str] = None,
        image: Optional[str] = None,
        author: Optional[dict] = None,
        timestamp: bool = True
    ) -> discord.Embed:
        """Create a branded Discord embed using guild configuration."""
        config = await self.get_branding_config(guild_id)
        
        # Use branding color if provided, otherwise use default
        embed_color = color or (config.embed_color if config else 0x5865F2)
        
        embed = discord.Embed(
            title=title,
            description=description,
            color=embed_color
        )
        
        # Add fields if provided
        if fields:
            for field in fields:
                if len(field) >= 3:
                    embed.add_field(name=field[0], value=field[1], inline=field[2])
                else:
                    embed.add_field(name=field[0], value=field[1], inline=False)
        
        # Set footer
        footer = footer_text or (config.footer_text if config else None)
        footer_icon_url = footer_icon or (config.footer_icon_url if config else None)
        
        if footer:
            embed.set_footer(text=footer, icon_url=footer_icon_url)
        
        # Set thumbnail
        thumbnail_url = thumbnail or (config.logo_url if config else None)
        if thumbnail_url:
            embed.set_thumbnail(url=thumbnail_url)
        
        # Set image
        if image:
            embed.set_image(url=image)
        
        # Set author
        if author:
            embed.set_author(
                name=author.get('name'),
                url=author.get('url'),
                icon_url=author.get('icon_url')
            )
        
        # Set timestamp
        if timestamp:
            embed.timestamp = discord.utils.utcnow()
        
        return embed
    
    async def success_embed(
        self,
        guild_id: int,
        title: str,
        description: Optional[str] = None
    ) -> discord.Embed:
        """Create a success embed (green)."""
        return await self.create_embed(
            guild_id,
            title=title,
            description=description,
            color=0x57F287  # Discord green
        )
    
    async def error_embed(
        self,
        guild_id: int,
        title: str,
        description: Optional[str] = None
    ) -> discord.Embed:
        """Create an error embed (red)."""
        return await self.create_embed(
            guild_id,
            title=title,
            description=description,
            color=0xED4245  # Discord red
        )
    
    async def warning_embed(
        self,
        guild_id: int,
        title: str,
        description: Optional[str] = None
    ) -> discord.Embed:
        """Create a warning embed (yellow)."""
        return await self.create_embed(
            guild_id,
            title=title,
            description=description,
            color=0xFEE75C  # Discord yellow
        )
    
    async def info_embed(
        self,
        guild_id: int,
        title: str,
        description: Optional[str] = None
    ) -> discord.Embed:
        """Create an info embed (blue)."""
        return await self.create_embed(
            guild_id,
            title=title,
            description=description,
            color=0x5865F2  # Discord blurple
        )
    
    async def session_embed(
        self,
        guild_id: int,
        session_title: str,
        session_type: str,
        host_name: str,
        description: Optional[str] = None,
        scheduled_time: Optional[str] = None,
        participant_count: int = 0,
        max_participants: Optional[int] = None
    ) -> discord.Embed:
        """Create a session-specific embed."""
        fields = [
            ("Host", host_name, True),
            ("Type", session_type, True),
            ("Participants", f"{participant_count}{f'/{max_participants}' if max_participants else ''}", True)
        ]
        
        if scheduled_time:
            fields.append(("Scheduled Time", scheduled_time, False))
        
        return await self.create_embed(
            guild_id,
            title=session_title,
            description=description,
            fields=fields
        )
    
    async def stats_embed(
        self,
        guild_id: int,
        user_name: str,
        stats: dict
    ) -> discord.Embed:
        """Create a statistics embed."""
        fields = [
            (stat_name, str(stat_value), True)
            for stat_name, stat_value in stats.items()
        ]
        
        return await self.create_embed(
            guild_id,
            title=f"Statistics for {user_name}",
            fields=fields
        )
    
    def parse_color(self, color_string: str) -> Optional[int]:
        """Parse color string to integer."""
        try:
            # Handle hex format (0x..., #..., or plain hex)
            if color_string.startswith('0x'):
                return int(color_string, 16)
            elif color_string.startswith('#'):
                return int(color_string[1:], 16)
            else:
                return int(color_string, 16)
        except (ValueError, AttributeError):
            logger.warning(f"Invalid color string: {color_string}")
            return None
    
    def validate_url(self, url: str) -> bool:
        """Validate URL format."""
        if not url:
            return True  # Empty URLs are allowed (optional fields)
        
        try:
            from urllib.parse import urlparse
            result = urlparse(url)
            return all([result.scheme, result.netloc])
        except Exception:
            return False
