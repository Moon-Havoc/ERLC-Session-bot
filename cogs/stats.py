"""Stats cog for statistics and leaderboards."""

from __future__ import annotations

from typing import Optional
import discord
from discord.ext import commands

from services import StatisticsService, ConfigService, BrandingService
from utils import get_logger

logger = get_logger(__name__)


class Stats(commands.Cog):
    """Statistics and leaderboard commands."""
    
    def __init__(self, bot: commands.Bot) -> None:
        """Initialize stats cog."""
        self.bot = bot
        self.statistics_service = StatisticsService()
        self.config_service = ConfigService()
        self.branding_service = BrandingService()
    
    @commands.Cog.listener()
    async def on_ready(self) -> None:
        """Called when the cog is ready."""
        logger.info("Stats cog loaded")
    
    @commands.group(name="stats", invoke_without_command=True)
    @commands.guild_only()
    async def stats_group(self, ctx: commands.Context) -> None:
        """Base command for statistics."""
        await ctx.send_help(self.stats_group)
    
    @stats_group.command(name="session")
    @commands.guild_only()
    async def stats_session(self, ctx: commands.Context) -> None:
        """Display statistics for the current session."""
        try:
            from services import SessionService
            session_service = SessionService()
            
            session = await session_service.get_active_session(ctx.guild.id)
            if not session:
                embed = await self.branding_service.error_embed(
                    ctx.guild.id,
                    title="No Active Session",
                    description="There is no active session to show statistics for."
                )
                await ctx.send(embed=embed)
                return
            
            # Get session statistics
            stats = await self.statistics_service.get_session_stats(ctx.guild.id, session.id)
            
            fields = [
                ("Session ID", str(session.id), True),
                ("Server Code", session.server_code, True),
                ("Duration", session.duration_str, True),
                ("Votes", str(session.vote_count), True),
                ("Boosts", str(session.boost_count), True)
            ]
            
            embed = await self.branding_service.create_embed(
                ctx.guild.id,
                title="Session Statistics",
                fields=fields
            )
            
            await ctx.send(embed=embed)
            
        except Exception as e:
            logger.error(f"Error displaying session stats: {e}")
            embed = await self.branding_service.error_embed(
                ctx.guild.id,
                title="Statistics Error",
                description="An error occurred while retrieving session statistics."
            )
            await ctx.send(embed=embed)
    
    @stats_group.command(name="server")
    @commands.guild_only()
    async def stats_server(self, ctx: commands.Context) -> None:
        """Display server-wide statistics."""
        try:
            guild_stats = await self.statistics_service.get_server_stats(ctx.guild.id)
            
            if not guild_stats:
                embed = await self.branding_service.error_embed(
                    ctx.guild.id,
                    title="No Statistics Available",
                    description="No statistics have been recorded for this server yet."
                )
                await ctx.send(embed=embed)
                return
            
            fields = [
                ("Total Sessions", str(guild_stats.total_sessions), True),
                ("Total Hosted Time", guild_stats.total_hosted_time_str, True),
                ("Total Votes", str(guild_stats.total_votes), True),
                ("Total Boosts", str(guild_stats.total_boosts), True),
                ("Longest Session", guild_stats.longest_session_str, True),
                ("Average Session Length", guild_stats.average_session_length_str, True)
            ]
            
            embed = await self.branding_service.create_embed(
                ctx.guild.id,
                title="Server Statistics",
                fields=fields
            )
            
            await ctx.send(embed=embed)
            
        except Exception as e:
            logger.error(f"Error displaying server stats: {e}")
            embed = await self.branding_service.error_embed(
                ctx.guild.id,
                title="Statistics Error",
                description="An error occurred while retrieving server statistics."
            )
            await ctx.send(embed=embed)
    
    @stats_group.command(name="host")
    @commands.guild_only()
    async def stats_host(self, ctx: commands.Context, user: Optional[discord.Member] = None) -> None:
        """Display statistics for a host (or yourself if no user specified)."""
        try:
            target_user = user or ctx.author
            
            host_stats = await self.statistics_service.get_host_stats(ctx.guild.id, target_user.id)
            
            if not host_stats:
                embed = await self.branding_service.error_embed(
                    ctx.guild.id,
                    title="No Statistics Available",
                    description=f"No statistics have been recorded for {target_user.display_name} yet."
                )
                await ctx.send(embed=embed)
                return
            
            fields = [
                ("Host", target_user.display_name, True),
                ("Sessions Hosted", str(host_stats.sessions_hosted), True),
                ("Total Hosted Time", host_stats.total_hosted_time_str, True),
                ("Total Votes", str(host_stats.total_votes), True),
                ("Total Boosts", str(host_stats.total_boosts), True)
            ]
            
            if host_stats.last_hosted:
                fields.append(("Last Hosted", discord.utils.format_dt(host_stats.last_hosted, style="R"), True))
            
            embed = await self.branding_service.create_embed(
                ctx.guild.id,
                title="Host Statistics",
                fields=fields
            )
            
            await ctx.send(embed=embed)
            
        except Exception as e:
            logger.error(f"Error displaying host stats: {e}")
            embed = await self.branding_service.error_embed(
                ctx.guild.id,
                title="Statistics Error",
                description="An error occurred while retrieving host statistics."
            )
            await ctx.send(embed=embed)
    
    @commands.group(name="leaderboard", invoke_without_command=True)
    @commands.guild_only()
    async def leaderboard_group(self, ctx: commands.Context) -> None:
        """Base command for leaderboards."""
        await ctx.send_help(self.leaderboard_group)
    
    @leaderboard_group.command(name="hosts")
    @commands.guild_only()
    async def leaderboard_hosts(self, ctx: commands.Context) -> None:
        """Display the top hosts leaderboard."""
        try:
            top_hosts = await self.statistics_service.get_top_hosts(ctx.guild.id, limit=10)
            
            if not top_hosts:
                embed = await self.branding_service.error_embed(
                    ctx.guild.id,
                    title="No Leaderboard Data",
                    description="No hosts have been ranked yet."
                )
                await ctx.send(embed=embed)
                return
            
            # Build leaderboard text
            leaderboard_text = ""
            for i, host_stats in enumerate(top_hosts, 1):
                try:
                    guild = ctx.guild
                    member = guild.get_member(host_stats.user_id) if guild else None
                    name = member.display_name if member else f"<@{host_stats.user_id}>"
                except Exception:
                    name = f"<@{host_stats.user_id}>"
                
                medal = ""
                if i == 1:
                    medal = "🥇"
                elif i == 2:
                    medal = "🥈"
                elif i == 3:
                    medal = "🥉"
                
                leaderboard_text += f"{medal} **#{i}** {name}\n"
                leaderboard_text += f"   └ {host_stats.sessions_hosted} sessions • {host_stats.total_hosted_time_str}\n\n"
            
            embed = await self.branding_service.create_embed(
                ctx.guild.id,
                title="🏆 Top Hosts",
                description=leaderboard_text
            )
            
            await ctx.send(embed=embed)
            
        except Exception as e:
            logger.error(f"Error displaying host leaderboard: {e}")
            embed = await self.branding_service.error_embed(
                ctx.guild.id,
                title="Leaderboard Error",
                description="An error occurred while retrieving the leaderboard."
            )
            await ctx.send(embed=embed)


async def setup(bot: commands.Bot) -> None:
    """Setup function for the stats cog."""
    await bot.add_cog(Stats(bot))
