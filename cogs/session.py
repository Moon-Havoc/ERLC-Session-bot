"""Session cog for managing training and practice sessions."""

from __future__ import annotations

from typing import Optional
import discord
from discord.ext import commands

from services import SessionService, ConfigService, BrandingService
from utils import get_logger

logger = get_logger(__name__)


class Session(commands.Cog):
    """Session management commands."""
    
    def __init__(self, bot: commands.Bot) -> None:
        """Initialize session cog."""
        self.bot = bot
        self.session_service = SessionService()
        self.config_service = ConfigService()
        self.branding_service = BrandingService()
    
    @commands.Cog.listener()
    async def on_ready(self) -> None:
        """Called when the cog is ready."""
        logger.info("Session cog loaded")
    
    def _check_permissions(self, ctx: commands.Context) -> bool:
        """Check if user has session management permissions."""
        # Server administrators always have access
        if ctx.author.guild_permissions.administrator:
            return True
        
        # Check configured roles
        config = self.config_service.get_guild_config(ctx.guild.id, use_cache=False)
        if not config:
            return False
        
        required_roles = [
            config.admin_role_id,
            config.management_role_id,
            config.host_role_id
        ]
        
        return any(role.id in required_roles for role in ctx.author.roles if role.id)
    
    @commands.group(name="session", invoke_without_command=True)
    @commands.guild_only()
    async def session_group(self, ctx: commands.Context) -> None:
        """Base command for session management."""
        await ctx.send_help(self.session_group)
    
    @session_group.command(name="start")
    @commands.guild_only()
    async def session_start(self, ctx: commands.Context, server_code: str, *, notes: Optional[str] = None) -> None:
        """Start a new session."""
        if not self._check_permissions(ctx):
            embed = await self.branding_service.error_embed(
                ctx.guild.id,
                title="Permission Denied",
                description="You don't have permission to start sessions."
            )
            await ctx.send(embed=embed)
            return
        
        # Check for existing active session
        if await self.session_service.has_active_session(ctx.guild.id):
            embed = await self.branding_service.error_embed(
                ctx.guild.id,
                title="Session Already Active",
                description="A session is already running. End it first."
            )
            await ctx.send(embed=embed)
            return
        
        # Get session channel from configuration
        config = await self.config_service.get_guild_config(ctx.guild.id)
        if not config or not config.session_channel_id:
            embed = await self.branding_service.error_embed(
                ctx.guild.id,
                title="Configuration Error",
                description="Session channel not configured. Use `/channel session` to set it."
            )
            await ctx.send(embed=embed)
            return
        
        # Verify session channel exists
        session_channel = ctx.guild.get_channel(config.session_channel_id)
        if not session_channel or not isinstance(session_channel, discord.TextChannel):
            embed = await self.branding_service.error_embed(
                ctx.guild.id,
                title="Channel Error",
                description="Configured session channel not found or invalid."
            )
            await ctx.send(embed=embed)
            return
        
        # Check bot permissions in session channel
        bot_permissions = session_channel.permissions_for(ctx.guild.me)
        if not bot_permissions.send_messages or not bot_permissions.embed_links:
            embed = await self.branding_service.error_embed(
                ctx.guild.id,
                title="Permission Error",
                description="Bot lacks required permissions in the session channel."
            )
            await ctx.send(embed=embed)
            return
        
        try:
            # Create session
            session = await self.session_service.create_session(
                guild_id=ctx.guild.id,
                host_id=ctx.author.id,
                server_code=server_code,
                notes=notes,
                session_channel_id=session_channel.id
            )
            
            if not session:
                embed = await self.branding_service.error_embed(
                    ctx.guild.id,
                    title="Session Creation Failed",
                    description="Failed to create session. Please try again."
                )
                await ctx.send(embed=embed)
                return
            
            # Create and send session embed
            embed = await self._create_session_embed(ctx.guild.id, session)
            message = await session_channel.send(embed=embed)
            
            # Update session with message ID
            await self.session_service.update_session_message(
                ctx.guild.id,
                message.id,
                session_channel.id
            )
            
            # Send confirmation
            embed = await self.branding_service.success_embed(
                ctx.guild.id,
                title="Session Started",
                description=f"Session started successfully in {session_channel.mention}"
            )
            await ctx.send(embed=embed)
            
            logger.info(f"Session {session.id} started by {ctx.author.id} in guild {ctx.guild.id}")
            
        except Exception as e:
            logger.error(f"Error starting session: {e}")
            embed = await self.branding_service.error_embed(
                ctx.guild.id,
                title="Session Error",
                description="An error occurred while starting the session."
            )
            await ctx.send(embed=embed)
    
    @session_group.command(name="end")
    @commands.guild_only()
    async def session_end(self, ctx: commands.Context) -> None:
        """End the active session."""
        if not self._check_permissions(ctx):
            embed = await self.branding_service.error_embed(
                ctx.guild.id,
                title="Permission Denied",
                description="You don't have permission to end sessions."
            )
            await ctx.send(embed=embed)
            return
        
        # Check for active session
        session = await self.session_service.get_active_session(ctx.guild.id)
        if not session:
            embed = await self.branding_service.error_embed(
                ctx.guild.id,
                title="No Active Session",
                description="There is no active session to end."
            )
            await ctx.send(embed=embed)
            return
        
        try:
            # End session
            ended_session = await self.session_service.end_session(ctx.guild.id)
            if not ended_session:
                embed = await self.branding_service.error_embed(
                    ctx.guild.id,
                    title="Session End Failed",
                    description="Failed to end session. Please try again."
                )
                await ctx.send(embed=embed)
                return
            
            # Update original session embed
            if ended_session.session_channel_id and ended_session.session_message_id:
                try:
                    channel = ctx.guild.get_channel(ended_session.session_channel_id)
                    if channel and isinstance(channel, discord.TextChannel):
                        try:
                            message = await channel.fetch_message(ended_session.session_message_id)
                            embed = await self._create_session_embed(ctx.guild.id, ended_session)
                            await message.edit(embed=embed)
                        except discord.NotFound:
                            logger.warning(f"Session message {ended_session.session_message_id} not found")
                        except Exception as e:
                            logger.error(f"Error updating session message: {e}")
                except Exception as e:
                    logger.error(f"Error getting session channel: {e}")
            
            # Create and send session summary
            summary_embed = await self._create_session_summary_embed(ctx.guild.id, ended_session)
            
            # Try to send to session channel, fallback to current channel
            if ended_session.session_channel_id:
                try:
                    summary_channel = ctx.guild.get_channel(ended_session.session_channel_id)
                    if summary_channel and isinstance(summary_channel, discord.TextChannel):
                        await summary_channel.send(embed=summary_embed)
                except Exception as e:
                    logger.error(f"Error sending summary to session channel: {e}")
                    await ctx.send(embed=summary_embed)
            else:
                await ctx.send(embed=summary_embed)
            
            # Send confirmation
            embed = await self.branding_service.success_embed(
                ctx.guild.id,
                title="Session Ended",
                description=f"Session ended. Duration: {ended_session.duration_str}"
            )
            await ctx.send(embed=embed)
            
            logger.info(f"Session {ended_session.id} ended by {ctx.author.id} in guild {ctx.guild.id}")
            
        except Exception as e:
            logger.error(f"Error ending session: {e}")
            embed = await self.branding_service.error_embed(
                ctx.guild.id,
                title="Session Error",
                description="An error occurred while ending the session."
            )
            await ctx.send(embed=embed)
    
    @session_group.command(name="info")
    @commands.guild_only()
    async def session_info(self, ctx: commands.Context) -> None:
        """Display information about the active session."""
        session = await self.session_service.get_active_session(ctx.guild.id)
        if not session:
            embed = await self.branding_service.error_embed(
                ctx.guild.id,
                title="No Active Session",
                description="There is no active session running."
            )
            await ctx.send(embed=embed)
            return
        
        try:
            embed = await self._create_session_embed(ctx.guild.id, session)
            await ctx.send(embed=embed)
        except Exception as e:
            logger.error(f"Error displaying session info: {e}")
            embed = await self.branding_service.error_embed(
                ctx.guild.id,
                title="Session Error",
                description="An error occurred while retrieving session information."
            )
            await ctx.send(embed=embed)
    
    async def _create_session_embed(self, guild_id: int, session: Session) -> discord.Embed:
        """Create a session embed with current information."""
        config = await self.config_service.get_guild_config(guild_id)
        community_name = config.community_name if config else "Community"
        
        # Get host member
        try:
            guild = self.bot.get_guild(guild_id)
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
        
        embed = await self.branding_service.create_embed(
            guild_id,
            title=f"Session #{session.id}" if session.id else "Session",
            fields=fields
        )
        
        # Add timestamp for last updated
        embed.timestamp = discord.utils.utcnow()
        
        return embed
    
    @session_group.command(name="vote")
    @commands.guild_only()
    async def session_vote(self, ctx: commands.Context) -> None:
        """Vote for the active session."""
        # Check for active session
        session = await self.session_service.get_active_session(ctx.guild.id)
        if not session:
            embed = await self.branding_service.error_embed(
                ctx.guild.id,
                title="No Active Session",
                description="There is no active session to vote for."
            )
            await ctx.send(embed=embed, ephemeral=True)
            return
        
        # Check if user already voted
        if await self.session_service.has_user_voted(ctx.guild.id, ctx.author.id):
            embed = await self.branding_service.error_embed(
                ctx.guild.id,
                title="Already Voted",
                description="You have already voted for this session."
            )
            await ctx.send(embed=embed, ephemeral=True)
            return
        
        try:
            # Record vote
            updated_session = await self.session_service.vote(ctx.guild.id, ctx.author.id)
            if not updated_session:
                embed = await self.branding_service.error_embed(
                    ctx.guild.id,
                    title="Vote Failed",
                    description="Failed to record your vote. Please try again."
                )
                await ctx.send(embed=embed, ephemeral=True)
                return
            
            # Update session embed
            await self._update_session_embed(ctx.guild.id)
            
            # Send confirmation
            embed = await self.branding_service.success_embed(
                ctx.guild.id,
                title="Vote Recorded",
                description="Your vote has been recorded successfully."
            )
            await ctx.send(embed=embed, ephemeral=True)
            
            logger.info(f"User {ctx.author.id} voted for session {session.id}")
            
        except Exception as e:
            logger.error(f"Error recording vote: {e}")
            embed = await self.branding_service.error_embed(
                ctx.guild.id,
                title="Vote Error",
                description="An error occurred while recording your vote."
            )
            await ctx.send(embed=embed, ephemeral=True)
    
    @session_group.command(name="boost")
    @commands.guild_only()
    async def session_boost(self, ctx: commands.Context, *, note: Optional[str] = None) -> None:
        """Boost the active session."""
        # Check for active session
        session = await self.session_service.get_active_session(ctx.guild.id)
        if not session:
            embed = await self.branding_service.error_embed(
                ctx.guild.id,
                title="No Active Session",
                description="There is no active session to boost."
            )
            await ctx.send(embed=embed, ephemeral=True)
            return
        
        try:
            # Record boost
            updated_session = await self.session_service.boost(ctx.guild.id, ctx.author.id, note)
            if not updated_session:
                embed = await self.branding_service.error_embed(
                    ctx.guild.id,
                    title="Boost Failed",
                    description="Failed to record your boost. Please try again."
                )
                await ctx.send(embed=embed, ephemeral=True)
                return
            
            # Update session embed
            await self._update_session_embed(ctx.guild.id)
            
            # Send confirmation
            embed = await self.branding_service.success_embed(
                ctx.guild.id,
                title="Boost Recorded",
                description="Your boost has been recorded successfully."
            )
            await ctx.send(embed=embed, ephemeral=True)
            
            logger.info(f"User {ctx.author.id} boosted session {session.id}")
            
        except Exception as e:
            logger.error(f"Error recording boost: {e}")
            embed = await self.branding_service.error_embed(
                ctx.guild.id,
                title="Boost Error",
                description="An error occurred while recording your boost."
            )
            await ctx.send(embed=embed, ephemeral=True)
    
    async def _create_session_summary_embed(self, guild_id: int, session: Session) -> discord.Embed:
        config = await self.config_service.get_guild_config(guild_id)
        community_name = config.community_name if config else "Community"
        
        # Get host member
        try:
            guild = self.bot.get_guild(guild_id)
            host = guild.get_member(session.host_id) if guild else None
            host_name = host.display_name if host else f"<@{session.host_id}>"
        except Exception:
            host_name = f"<@{session.host_id}>"
        
        fields = [
            ("🔴 Session Ended", "", False),
            ("Community", community_name, True),
            ("Host", host_name, True),
            ("Server Code", session.server_code, True),
            ("Duration", session.duration_str, True),
            ("Votes", str(session.vote_count), True),
            ("Boosts", str(session.boost_count), True)
        ]
        
        if session.notes:
            fields.insert(4, ("Notes", session.notes, False))
        
        embed = await self.branding_service.create_embed(
            guild_id,
            title=f"Session #{session.id} Summary" if session.id else "Session Summary",
            fields=fields
        )
        
        embed.timestamp = discord.utils.utcnow()
        
        return embed
    
    async def update_session_display(self, guild_id: int) -> None:
        """Update the session embed for a guild (called by background task)."""
        session = await self.session_service.get_active_session(guild_id)
        if not session or not session.is_active:
            return
        
        if not session.session_channel_id or not session.session_message_id:
            return
        
        try:
            guild = self.bot.get_guild(guild_id)
            if not guild:
                return
            
            channel = guild.get_channel(session.session_channel_id)
            if not channel or not isinstance(channel, discord.TextChannel):
                return
            
            try:
                message = await channel.fetch_message(session.session_message_id)
                embed = await self._create_session_embed(guild_id, session)
                await message.edit(embed=embed)
            except discord.NotFound:
                logger.warning(f"Session message {session.session_message_id} not found, removing reference")
                await self.session_service.update_session_message(guild_id, None, None)
            except Exception as e:
                logger.error(f"Error updating session embed: {e}")
        except Exception as e:
            logger.error(f"Error updating session display: {e}")
    
    async def _update_session_embed(self, guild_id: int) -> None:
        """Update the session embed immediately (called after vote/boost)."""
        session = await self.session_service.get_active_session(guild_id)
        if not session or not session.is_active:
            return
        
        if not session.session_channel_id or not session.session_message_id:
            return
        
        try:
            guild = self.bot.get_guild(guild_id)
            if not guild:
                return
            
            channel = guild.get_channel(session.session_channel_id)
            if not channel or not isinstance(channel, discord.TextChannel):
                return
            
            try:
                message = await channel.fetch_message(session.session_message_id)
                embed = await self._create_session_embed(guild_id, session)
                await message.edit(embed=embed)
            except discord.NotFound:
                logger.warning(f"Session message {session.session_message_id} not found")
            except Exception as e:
                logger.error(f"Error updating session embed: {e}")
        except Exception as e:
            logger.error(f"Error updating session display: {e}")


async def setup(bot: commands.Bot) -> None:
    """Setup function for the session cog."""
    await bot.add_cog(Session(bot))
