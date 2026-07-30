"""Main bot entry point for SessionCore."""

import asyncio
from typing import Optional
import discord
from discord.ext import commands

from config import config
from database import database, get_migration_runner
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
        
        # Initialize database
        await database.initialize()
        logger.info("Database initialized")
        
        # Run migrations
        migration_runner = get_migration_runner(database)
        await migration_runner.migrate()
        logger.info("Database migrations completed")
        
        # Load cogs
        await self.load_cogs()
        logger.info("Cogs loaded")
        
        # Restore active sessions
        from services import SessionService
        session_service = SessionService()
        await session_service.restore_sessions()
        logger.info("Active sessions restored")
    
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
