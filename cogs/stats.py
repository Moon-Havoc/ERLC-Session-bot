"""Stats cog for viewing statistics and leaderboards."""

from __future__ import annotations

import discord
from discord.ext import commands

from services import StatsService, BrandingService
from utils import (
    guild_configured, branding_configured,
    get_embed_helper, get_logger
)

logger = get_logger(__name__)


class Stats(commands.Cog):
    """Statistics and leaderboard commands."""
    
    def __init__(self, bot: commands.Bot) -> None:
        """Initialize stats cog."""
        self.bot = bot
        self.stats_service = StatsService()
        self.branding_service = BrandingService()
    
    @commands.Cog.listener()
    async def on_ready(self) -> None:
        """Called when the cog is ready."""
        logger.info("Stats cog loaded")
    
    @commands.group(name="stats", invoke_without_command=True)
    @commands.guild_only()
    @guild_configured()
    async def stats_group(self, ctx: commands.Context, user: Optional[discord.Member] = None) -> None:
        """View statistics for a user."""
        # Placeholder for future implementation
        target_user = user or ctx.author
        embed_helper = get_embed_helper()
        
        embed = embed_helper.create_info_embed(
            title="Statistics",
            description=f"Statistics for {target_user.mention} will be displayed here."
        )
        await ctx.send(embed=embed)
    
    @stats_group.command(name="leaderboard")
    @commands.guild_only()
    @guild_configured()
    async def stats_leaderboard(self, ctx: commands.Context, metric: str = "sessions") -> None:
        """View leaderboard for a specific metric."""
        # Placeholder for future implementation
        embed_helper = get_embed_helper()
        
        embed = embed_helper.create_info_embed(
            title="Leaderboard",
            description=f"Leaderboard for '{metric}' will be displayed here."
        )
        await ctx.send(embed=embed)
    
    @stats_group.command(name="hosts")
    @commands.guild_only()
    @guild_configured()
    async def stats_hosts(self, ctx: commands.Context) -> None:
        """View host statistics."""
        # Placeholder for future implementation
        embed_helper = get_embed_helper()
        
        embed = embed_helper.create_info_embed(
            title="Host Statistics",
            description="Host statistics will be displayed here."
        )
        await ctx.send(embed=embed)
    
    # Placeholder for future stats commands:
    # - global: View global server statistics
    # - period: View statistics for a time period
    # - rankings: View user rankings


async def setup(bot: commands.Bot) -> None:
    """Setup function for the stats cog."""
    await bot.add_cog(Stats(bot))
