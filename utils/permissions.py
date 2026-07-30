"""Permission system with configurable Discord roles."""

from typing import Optional
import discord

from database import GuildConfig
from .logger import get_logger

logger = get_logger(__name__)


class PermissionLevel:
    """Permission levels for the bot."""
    
    ADMIN = "admin"
    MODERATOR = "moderator"
    HOST = "host"
    MEMBER = "member"
    EVERYONE = "everyone"


class PermissionManager:
    """Manages permissions based on configurable Discord roles."""
    
    def __init__(self, guild_config: Optional[GuildConfig] = None) -> None:
        """Initialize permission manager with guild configuration."""
        self.guild_config = guild_config
    
    def set_guild_config(self, guild_config: GuildConfig) -> None:
        """Update guild configuration."""
        self.guild_config = guild_config
    
    def has_permission(
        self,
        member: discord.Member,
        permission_level: str
    ) -> bool:
        """Check if a member has a specific permission level."""
        
        if not self.guild_config:
            logger.warning("No guild configuration available for permission check")
            return False
        
        # Bot owner always has all permissions
        from config import config
        if config.bot_owner_id and member.id == config.bot_owner_id:
            return True
        
        # Guild owner always has all permissions
        if member.guild.owner_id == member.id:
            return True
        
        # Check admin permission
        if permission_level == PermissionLevel.ADMIN:
            return self._has_role(member, self.guild_config.admin_role_id)
        
        # Check moderator permission (includes admins)
        if permission_level == PermissionLevel.MODERATOR:
            return (
                self._has_role(member, self.guild_config.admin_role_id) or
                self._has_role(member, self.guild_config.moderator_role_id)
            )
        
        # Check host permission (includes moderators and admins)
        if permission_level == PermissionLevel.HOST:
            return (
                self._has_role(member, self.guild_config.admin_role_id) or
                self._has_role(member, self.guild_config.moderator_role_id) or
                self._has_role(member, self.guild_config.host_role_id)
            )
        
        # Check member permission (includes all higher roles)
        if permission_level == PermissionLevel.MEMBER:
            return (
                self._has_role(member, self.guild_config.admin_role_id) or
                self._has_role(member, self.guild_config.moderator_role_id) or
                self._has_role(member, self.guild_config.host_role_id) or
                self._has_role(member, self.guild_config.member_role_id)
            )
        
        # Everyone permission is always granted
        if permission_level == PermissionLevel.EVERYONE:
            return True
        
        return False
    
    def _has_role(self, member: discord.Member, role_id: Optional[int]) -> bool:
        """Check if member has a specific role."""
        if role_id is None:
            return False
        return any(role.id == role_id for role in member.roles)
    
    def get_permission_level(self, member: discord.Member) -> str:
        """Get the highest permission level for a member."""
        
        if not self.guild_config:
            return PermissionLevel.EVERYONE
        
        # Bot owner
        from config import config
        if config.bot_owner_id and member.id == config.bot_owner_id:
            return PermissionLevel.ADMIN
        
        # Guild owner
        if member.guild.owner_id == member.id:
            return PermissionLevel.ADMIN
        
        # Check roles in hierarchy
        if self._has_role(member, self.guild_config.admin_role_id):
            return PermissionLevel.ADMIN
        
        if self._has_role(member, self.guild_config.moderator_role_id):
            return PermissionLevel.MODERATOR
        
        if self._has_role(member, self.guild_config.host_role_id):
            return PermissionLevel.HOST
        
        if self._has_role(member, self.guild_config.member_role_id):
            return PermissionLevel.MEMBER
        
        return PermissionLevel.EVERYONE
    
    def is_admin(self, member: discord.Member) -> bool:
        """Check if member is an admin."""
        return self.has_permission(member, PermissionLevel.ADMIN)
    
    def is_moderator(self, member: discord.Member) -> bool:
        """Check if member is a moderator."""
        return self.has_permission(member, PermissionLevel.MODERATOR)
    
    def is_host(self, member: discord.Member) -> bool:
        """Check if member is a host."""
        return self.has_permission(member, PermissionLevel.HOST)
    
    def is_member(self, member: discord.Member) -> bool:
        """Check if member is a member."""
        return self.has_permission(member, PermissionLevel.MEMBER)


def get_permission_manager(guild_config: Optional[GuildConfig] = None) -> PermissionManager:
    """Get a permission manager instance."""
    return PermissionManager(guild_config)
