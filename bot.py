"""Main bot entry point for SessionCore."""

import asyncio
from typing import Optional
import discord
from discord.ext import commands

from config import config
from database import database, get_migration_runner
from services import (
    ConfigService, BrandingService, SessionService,
    StatisticsService, AuditService,
    initialize_container, get_container
)
from utils.views import persistent_view_manager
from utils import get_logger

logger = get_logger(__name__)


class SessionCoreBot(commands.Bot):
    """Main bot class for SessionCore."""
    
    def __init__(self) -> None:
        """Initialize the bot."""
        intents = discord.Intents.default()
        intents.guilds = True
        intents.members = True
        intents.messages = True
        intents.message_content = True
        intents.reactions = True
        
        super().__init__(
            command_prefix=config.command_prefix,
            intents=intents,
            help_command=None,
            activity=discord.Activity(
                type=discord.ActivityType.watching,
                name="sessions"
            )
        )
    
    async def setup_hook(self) -> None:
        """Called when the bot is setting up."""
        logger.info("Setting up bot...")
        
        # Initialize service container
        initialize_container()
        container = get_container()
        
        # Initialize database
        await database.initialize()
        logger.info("Database initialized")
        
        # Run migrations
        migration_runner = get_migration_runner(database)
        await migration_runner.migrate()
        logger.info("Database migrations completed")
        
        # Initialize statistics and audit services
        statistics_service = container.get_singleton('statistics_service')
        if statistics_service:
            await statistics_service.initialize()
            logger.info("Statistics service initialized")
        
        audit_service = container.get_singleton('audit_service')
        if audit_service:
            await audit_service.initialize()
            logger.info("Audit service initialized")
        
        # Load cogs
        await self.load_cogs()
        logger.info("Cogs loaded")
        
        # Restore active sessions
        session_service = container.get_singleton('session_service')
        if session_service:
            await session_service.restore_sessions()
            logger.info("Active sessions restored")
        
        # Restore persistent views from active sessions
        await self._restore_persistent_views()
    
    async def _restore_persistent_views(self) -> None:
        """Restore persistent views for active sessions."""
        try:
            container = get_container()
            session_service = container.get_singleton('session_service')
            branding_service = container.get_singleton('branding_service')
            config_service = container.get_singleton('config_service')
            
            if not session_service:
                return
            
            # Get all active sessions
            active_sessions = await session_service.session_repository.get_all_active_sessions()
            
            for session in active_sessions:
                try:
                    if not session.session_channel_id or not session.session_message_id:
                        continue
                    
                    guild = self.get_guild(session.guild_id)
                    if not guild:
                        continue
                    
                    channel = guild.get_channel(session.session_channel_id)
                    if not channel or not isinstance(channel, discord.TextChannel):
                        continue
                    
                    try:
                        message = await channel.fetch_message(session.session_message_id)
                        
                        # Recreate the session controls view
                        from utils.views import SessionControlsView
                        view = SessionControlsView(
                            guild_id=session.guild_id,
                            session_id=session.id,
                            session_service=session_service,
                            branding_service=branding_service,
                            config_service=config_service,
                            embed_callback=self._create_session_embed if hasattr(self, '_create_session_embed') else None
                        )
                        
                        # Update message with view
                        embed = await view._create_basic_embed(message, session)
                        await message.edit(embed=embed, view=view)
                        
                        # Register persistent view
                        persistent_view_manager.register_view(
                            view.custom_id,
                            view,
                            metadata={
                                "guild_id": session.guild_id,
                                "session_id": session.id,
                                "message_id": session.session_message_id,
                                "channel_id": session.session_channel_id
                            }
                        )
                        
                        logger.info(f"Restored persistent view for session {session.id}")
                    except discord.NotFound:
                        logger.warning(f"Could not restore view for session {session.id}: message not found")
                    except Exception as e:
                        logger.error(f"Error restoring view for session {session.id}: {e}")
                except Exception as e:
                    logger.error(f"Error processing session {session.id} for view restoration: {e}")
            
            logger.info(f"Restored {len(persistent_view_manager.get_all_views())} persistent views")
        except Exception as e:
            logger.error(f"Error restoring persistent views: {e}")
    
    async def _create_session_embed(self, guild_id: int, session) -> discord.Embed:
        """Helper method to create session embed for view restoration."""
        from services import BrandingService
        branding_service = BrandingService()
        
        config = await branding_service.config_service.get_guild_config(guild_id)
        community_name = config.community_name if config else "Community"
        
        # Get host member
        try:
            guild = self.get_guild(guild_id)
            host = guild.get_member(session.host_id) if guild else None
            host_name = host.display_name if host else f"<@{session.host_id}>"
        except Exception:
            host_name = f"<@{session.host_id}>"
        
        # Status indicator
        status_emoji = "🟢" if session.is_active else "🔴"
        status_text = "Session Active" if session.is_active else "Session Ended"
        
        fields = [
            (f"{status_emoji} {status_text}", "", False),
            ("Community", community_name, True),
            ("Host", host_name, True),
            ("Server Code", session.server_code, True),
            ("Started", discord.utils.format_dt(session.started_at, style="R") if session.started_at else "N/A", True),
            ("Duration", session.duration_str, True),
            ("Votes", str(session.vote_count), True),
            ("Boosts", str(session.boost_count), True)
        ]
        
        if session.notes:
            fields.insert(4, ("Notes", session.notes, False))
        
        if session.is_active:
            fields.append(("Status", "Live • Updates every 60s", False))
        else:
            fields.append(("Status", "Ended", False))
        
        embed = await branding_service.create_embed(
            guild_id,
            title=f"Session #{session.id}" if session.id else "Session",
            fields=fields
        )
        
        embed.timestamp = discord.utils.utcnow()
        
        return embed
    
    async def load_cogs(self) -> None:
        """Load all bot cogs."""
        cogs = [
            "cogs.admin",
            "cogs.session",
            "cogs.stats",
            "cogs.utility"
        ]
        
        for cog in cogs:
            try:
                await self.load_extension(cog)
                logger.info(f"Loaded cog: {cog}")
            except Exception as e:
                logger.error(f"Failed to load cog {cog}: {e}")
    
    async def on_ready(self) -> None:
        """Called when the bot is ready."""
        logger.info(f"Bot logged in as {self.user.name} (ID: {self.user.id})")
        logger.info(f"Connected to {len(self.guilds)} guilds")
        logger.info(f"Bot is ready!")
    
    async def on_guild_join(self, guild: discord.Guild) -> None:
        """Called when the bot joins a guild."""
        logger.info(f"Joined guild: {guild.name} (ID: {guild.id})")
        
        # Create default configuration for new guild
        from services import ConfigService
        config_service = ConfigService()
        
        try:
            await config_service.ensure_guild_config(guild.id, guild.name)
            logger.info(f"Created default configuration for guild {guild.id}")
        except Exception as e:
            logger.error(f"Failed to create default configuration for guild {guild.id}: {e}")
    
    async def on_guild_remove(self, guild: discord.Guild) -> None:
        """Called when the bot leaves a guild."""
        logger.info(f"Left guild: {guild.name} (ID: {guild.id})")
    
    async def on_command_error(self, ctx: commands.Context, error: Exception) -> None:
        """Called when a command error occurs."""
        logger.error(f"Command error: {error}")
        
        if isinstance(error, commands.CommandNotFound):
            return
        
        if isinstance(error, commands.MissingRequiredArgument):
            from utils import get_embed_helper
            embed_helper = get_embed_helper()
            embed = embed_helper.create_error_embed(
                title="Missing Argument",
                description=f"Missing required argument: `{error.param.name}`"
            )
            await ctx.send(embed=embed)
            return
        
        if isinstance(error, commands.MissingPermissions):
            from utils import get_embed_helper
            embed_helper = get_embed_helper()
            embed = embed_helper.create_error_embed(
                title="Missing Permissions",
                description="You don't have permission to use this command."
            )
            await ctx.send(embed=embed)
            return
        
        if isinstance(error, commands.BotMissingPermissions):
            from utils import get_embed_helper
            embed_helper = get_embed_helper()
            embed = embed_helper.create_error_embed(
                title="Bot Missing Permissions",
                description="The bot is missing required permissions."
            )
            await ctx.send(embed=embed)
            return
        
        if isinstance(error, commands.CheckFailure):
            from utils import get_embed_helper
            embed_helper = get_embed_helper()
            embed = embed_helper.create_error_embed(
                title="Access Denied",
                description="You don't meet the requirements to use this command."
            )
            await ctx.send(embed=embed)
            return
        
        # Generic error
        from utils import get_embed_helper
        embed_helper = get_embed_helper()
        embed = embed_helper.create_error_embed(
            title="Command Error",
            description="An error occurred while executing this command."
        )
        await ctx.send(embed=embed)
    
    async def close(self) -> None:
        """Close the bot and cleanup resources."""
        logger.info("Shutting down bot...")
        
        # Shutdown session service
        from services import SessionService
        session_service = SessionService()
        await session_service.shutdown()
        
        await super().close()


async def main() -> None:
    """Main entry point."""
    bot = SessionCoreBot()
    
    try:
        logger.info("Starting bot...")
        await bot.start(config.discord_token)
    except KeyboardInterrupt:
        logger.info("Shutting down bot...")
    except Exception as e:
        logger.error(f"Fatal error: {e}")
    finally:
        if not bot.is_closed():
            await bot.close()


if __name__ == "__main__":
    asyncio.run(main())
