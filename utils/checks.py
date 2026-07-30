"""Discord.py command checks using the permission system."""

from typing import Callable, Optional
import discord
from discord.ext import commands

from database import GuildConfig
from .permissions import PermissionManager, PermissionLevel
from .logger import get_logger

logger = get_logger(__name__)


def has_permission(permission_level: str):
    """Check decorator for permission-based command access."""
    
    async def predicate(ctx: commands.Context) -> bool:
        # Get guild configuration
        from services.config_service import ConfigService
        config_service = ConfigService()
        guild_config = await config_service.get_guild_config(ctx.guild.id)
        
        # Create permission manager
        perm_manager = PermissionManager(guild_config)
        
        # Check permission
        if not perm_manager.has_permission(ctx.author, permission_level):
            logger.warning(
                f"Permission denied: {ctx.author} tried to use command "
                f"'{ctx.command.name}' requiring {permission_level}"
            )
            return False
        
        return True
    
    return commands.check(predicate)


def is_admin():
    """Check if user has admin permissions."""
    return has_permission(PermissionLevel.ADMIN)


def is_moderator():
    """Check if user has moderator permissions."""
    return has_permission(PermissionLevel.MODERATOR)


def is_host():
    """Check if user has host permissions."""
    return has_permission(PermissionLevel.HOST)


def is_member():
    """Check if user has member permissions."""
    return has_permission(PermissionLevel.MEMBER)


def guild_configured():
    """Check if guild has proper configuration."""
    
    async def predicate(ctx: commands.Context) -> bool:
        from services.config_service import ConfigService
        config_service = ConfigService()
        guild_config = await config_service.get_guild_config(ctx.guild.id)
        
        if not guild_config:
            logger.warning(f"Guild {ctx.guild.id} not configured")
            return False
        
        return True
    
    return commands.check(predicate)


def branding_configured():
    """Check if guild has branding configured."""
    
    async def predicate(ctx: commands.Context) -> bool:
        from services.branding import BrandingService
        branding_service = BrandingService()
        branding = await branding_service.get_branding(ctx.guild.id)
        
        if not branding:
            logger.warning(f"Guild {ctx.guild.id} branding not configured")
            return False
        
        return True
    
    return commands.check(predicate)


def bot_owner():
    """Check if user is the bot owner."""
    
    async def predicate(ctx: commands.Context) -> bool:
        from config import config
        if config.bot_owner_id and ctx.author.id == config.bot_owner_id:
            return True
        return False
    
    return commands.check(predicate)
