"""Embed helper with branding support for SessionCore."""

from __future__ import annotations

import discord
from typing import Optional

from database import Branding
from .logger import get_logger

logger = get_logger(__name__)


class EmbedHelper:
    """Helper for creating branded Discord embeds."""
    
    def __init__(self, branding: Optional[Branding] = None) -> None:
        """Initialize embed helper with branding configuration."""
        self.branding = branding
    
    def set_branding(self, branding: Branding) -> None:
        """Update branding configuration."""
        self.branding = branding
    
    def create_embed(
        self,
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
        """Create a branded Discord embed."""
        
        # Use branding color if provided, otherwise use default
        embed_color = color or (self.branding.embed_color if self.branding else 0x5865F2)
        
        embed = discord.Embed(
            title=title,
            description=description,
            color=embed_color
        )
        
        # Add fields if provided (list of tuples: (name, value, inline))
        if fields:
            for field in fields:
                if len(field) >= 3:
                    embed.add_field(name=field[0], value=field[1], inline=field[2])
                else:
                    embed.add_field(name=field[0], value=field[1], inline=False)
        
        # Set footer
        footer = footer_text or (self.branding.footer_text if self.branding else None)
        footer_icon_url = footer_icon or (self.branding.footer_icon_url if self.branding else None)
        
        if footer:
            embed.set_footer(text=footer, icon_url=footer_icon_url)
        
        # Set thumbnail
        thumbnail_url = thumbnail or (self.branding.logo_url if self.branding else None)
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
    
    def create_success_embed(
        self,
        title: str,
        description: Optional[str] = None
    ) -> discord.Embed:
        """Create a success embed (green)."""
        return self.create_embed(
            title=title,
            description=description,
            color=0x57F287  # Discord green
        )
    
    def create_error_embed(
        self,
        title: str,
        description: Optional[str] = None
    ) -> discord.Embed:
        """Create an error embed (red)."""
        return self.create_embed(
            title=title,
            description=description,
            color=0xED4245  # Discord red
        )
    
    def create_warning_embed(
        self,
        title: str,
        description: Optional[str] = None
    ) -> discord.Embed:
        """Create a warning embed (yellow)."""
        return self.create_embed(
            title=title,
            description=description,
            color=0xFEE75C  # Discord yellow
        )
    
    def create_info_embed(
        self,
        title: str,
        description: Optional[str] = None
    ) -> discord.Embed:
        """Create an info embed (blue)."""
        return self.create_embed(
            title=title,
            description=description,
            color=0x5865F2  # Discord blurple
        )
    
    def create_session_embed(
        self,
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
        
        return self.create_embed(
            title=session_title,
            description=description,
            fields=fields
        )
    
    def create_stats_embed(
        self,
        user_name: str,
        stats: dict
    ) -> discord.Embed:
        """Create a statistics embed."""
        
        fields = [
            (stat_name, str(stat_value), True)
            for stat_name, stat_value in stats.items()
        ]
        
        return self.create_embed(
            title=f"Statistics for {user_name}",
            fields=fields
        )


def get_embed_helper(branding: Optional[Branding] = None) -> EmbedHelper:
    """Get an embed helper instance."""
    return EmbedHelper(branding)
