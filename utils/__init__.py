"""Utility package for SessionCore."""

from .logger import get_logger, StructuredLogger
from .embeds import EmbedHelper, get_embed_helper
from .permissions import PermissionManager, PermissionLevel, get_permission_manager
from .checks import (
    has_permission,
    is_admin,
    is_moderator,
    is_host,
    is_member,
    guild_configured,
    branding_configured,
    bot_owner
)
from .views import (
    ConfirmView,
    PaginationView,
    SessionModal,
    SelectMenuView
)

__all__ = [
    "get_logger",
    "StructuredLogger",
    "EmbedHelper",
    "get_embed_helper",
    "PermissionManager",
    "PermissionLevel",
    "get_permission_manager",
    "has_permission",
    "is_admin",
    "is_moderator",
    "is_host",
    "is_member",
    "guild_configured",
    "branding_configured",
    "bot_owner",
    "ConfirmView",
    "PaginationView",
    "SessionModal",
    "SelectMenuView",
]
