"""Branding service for community customization."""

from typing import Optional
import discord

from database import Branding, BrandingRepository, database
from utils.logger import get_logger

logger = get_logger(__name__)


class BrandingService:
    """Service for managing community branding."""
    
    def __init__(self) -> None:
        """Initialize branding service."""
        self.repository = BrandingRepository(database)
    
    async def get_branding(self, guild_id: int) -> Optional[Branding]:
        """Get branding by guild ID."""
        try:
            return await self.repository.get_by_guild(guild_id)
        except Exception as e:
            logger.error(f"Error getting branding for {guild_id}: {e}")
            return None
    
    async def create_branding(
        self,
        guild_id: int,
        community_name: str,
        description: Optional[str] = None,
        logo_url: Optional[str] = None,
        embed_color: int = 0x5865F2,
        footer_text: Optional[str] = None,
        footer_icon_url: Optional[str] = None,
        custom_emoji: Optional[str] = None,
        website_url: Optional[str] = None,
        invite_link: Optional[str] = None
    ) -> Optional[Branding]:
        """Create new branding configuration."""
        try:
            branding = Branding(
                guild_id=guild_id,
                community_name=community_name,
                description=description,
                logo_url=logo_url,
                embed_color=embed_color,
                footer_text=footer_text,
                footer_icon_url=footer_icon_url,
                custom_emoji=custom_emoji,
                website_url=website_url,
                invite_link=invite_link
            )
            return await self.repository.create(branding)
        except Exception as e:
            logger.error(f"Error creating branding for {guild_id}: {e}")
            return None
    
    async def update_branding(
        self,
        guild_id: int,
        community_name: Optional[str] = None,
        description: Optional[str] = None,
        logo_url: Optional[str] = None,
        embed_color: Optional[int] = None,
        footer_text: Optional[str] = None,
        footer_icon_url: Optional[str] = None,
        custom_emoji: Optional[str] = None,
        website_url: Optional[str] = None,
        invite_link: Optional[str] = None
    ) -> Optional[Branding]:
        """Update branding configuration."""
        try:
            branding = await self.repository.get_by_guild(guild_id)
            if not branding:
                logger.warning(f"Branding not found for {guild_id}")
                return None
            
            # Update only provided fields
            if community_name is not None:
                branding.community_name = community_name
            if description is not None:
                branding.description = description
            if logo_url is not None:
                branding.logo_url = logo_url
            if embed_color is not None:
                branding.embed_color = embed_color
            if footer_text is not None:
                branding.footer_text = footer_text
            if footer_icon_url is not None:
                branding.footer_icon_url = footer_icon_url
            if custom_emoji is not None:
                branding.custom_emoji = custom_emoji
            if website_url is not None:
                branding.website_url = website_url
            if invite_link is not None:
                branding.invite_link = invite_link
            
            return await self.repository.update(branding)
        except Exception as e:
            logger.error(f"Error updating branding for {guild_id}: {e}")
            return None
    
    async def delete_branding(self, guild_id: int) -> bool:
        """Delete branding configuration."""
        try:
            return await self.repository.delete(guild_id)
        except Exception as e:
            logger.error(f"Error deleting branding for {guild_id}: {e}")
            return False
    
    async def ensure_branding(
        self,
        guild_id: int,
        community_name: str = "Community"
    ) -> Branding:
        """Ensure branding exists, create with defaults if not."""
        branding = await self.get_branding(guild_id)
        if not branding:
            logger.info(f"Creating default branding for guild {guild_id}")
            branding = await self.create_branding(guild_id, community_name)
        return branding
    
    async def set_community_name(self, guild_id: int, name: str) -> Optional[Branding]:
        """Set community name."""
        return await self.update_branding(guild_id, community_name=name)
    
    async def set_description(self, guild_id: int, description: str) -> Optional[Branding]:
        """Set community description."""
        return await self.update_branding(guild_id, description=description)
    
    async def set_logo_url(self, guild_id: int, url: str) -> Optional[Branding]:
        """Set logo URL."""
        return await self.update_branding(guild_id, logo_url=url)
    
    async def set_embed_color(self, guild_id: int, color: int) -> Optional[Branding]:
        """Set embed color."""
        return await self.update_branding(guild_id, embed_color=color)
    
    async def set_footer_text(self, guild_id: int, text: str) -> Optional[Branding]:
        """Set footer text."""
        return await self.update_branding(guild_id, footer_text=text)
    
    async def set_footer_icon(self, guild_id: int, url: str) -> Optional[Branding]:
        """Set footer icon URL."""
        return await self.update_branding(guild_id, footer_icon_url=url)
    
    async def set_custom_emoji(self, guild_id: int, emoji: str) -> Optional[Branding]:
        """Set custom emoji."""
        return await self.update_branding(guild_id, custom_emoji=emoji)
    
    async def set_website_url(self, guild_id: int, url: str) -> Optional[Branding]:
        """Set website URL."""
        return await self.update_branding(guild_id, website_url=url)
    
    async def set_invite_link(self, guild_id: int, url: str) -> Optional[Branding]:
        """Set invite link."""
        return await self.update_branding(guild_id, invite_link=url)
    
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
