"""Admin cog for server configuration and management with slash commands."""

from __future__ import annotations

from typing import Optional
import discord
from discord.ext import commands

from services import ConfigService, BrandingService
from utils import get_logger

logger = get_logger(__name__)


class Admin(commands.Cog):
    """Administrative commands for server configuration."""
    
    def __init__(self, bot: commands.Bot) -> None:
        """Initialize admin cog."""
        self.bot = bot
        self.config_service = ConfigService()
        self.branding_service = BrandingService()
    
    @commands.Cog.listener()
    async def on_ready(self) -> None:
        """Called when the cog is ready."""
        logger.info("Admin cog loaded")
    
    async def _check_permissions(self, ctx: commands.Context) -> bool:
        """Check if user has admin permissions."""
        # Server administrators always have access
        if ctx.author.guild_permissions.administrator:
            return True
        
        # Check configured admin role
        config = await self.config_service.get_guild_config(ctx.guild.id)
        if config and config.admin_role_id:
            return any(role.id == config.admin_role_id for role in ctx.author.roles)
        
        return False
    
    # Configuration commands
    @commands.command(name="config")
    @commands.guild_only()
    async def config_view(self, ctx: commands.Context) -> None:
        """View current server configuration."""
        if not self._check_permissions(ctx):
            await ctx.send("You don't have permission to use this command.")
            return
        
        config = await self.config_service.get_guild_config(ctx.guild.id)
        if not config:
            await ctx.send("Server configuration not found.")
            return
        
        embed = await self.branding_service.info_embed(
            ctx.guild.id,
            title="Server Configuration",
            description=f"Configuration for {config.community_name}"
        )
        
        fields = [
            ("Community Name", config.community_name, True),
            ("Timezone", config.timezone, True),
            ("Auto Role", "Enabled" if config.auto_role_enabled else "Disabled", True),
            ("Session Channel", f"<#{config.session_channel_id}>" if config.session_channel_id else "Not set", True),
            ("Logs Channel", f"<#{config.logs_channel_id}>" if config.logs_channel_id else "Not set", True),
            ("Admin Role", f"<@&{config.admin_role_id}>" if config.admin_role_id else "Not set", True),
            ("Management Role", f"<@&{config.management_role_id}>" if config.management_role_id else "Not set", True),
            ("Host Role", f"<@&{config.host_role_id}>" if config.host_role_id else "Not set", True),
            ("Moderator Role", f"<@&{config.moderator_role_id}>" if config.moderator_role_id else "Not set", True),
        ]
        
        if config.community_description:
            fields.insert(1, ("Description", config.community_description, False))
        
        for field in fields:
            embed.add_field(name=field[0], value=field[1], inline=field[2])
        
        await ctx.send(embed=embed)
    
    # Branding commands
    @commands.command(name="branding")
    @commands.guild_only()
    async def branding_group(self, ctx: commands.Context) -> None:
        """Base command for branding configuration."""
        await ctx.send_help(self.branding_group)
    
    @branding_group.command(name="setname")
    @commands.guild_only()
    async def branding_setname(self, ctx: commands.Context, *, name: str) -> None:
        """Set community name."""
        if not self._check_permissions(ctx):
            await ctx.send("You don't have permission to use this command.")
            return
        
        if len(name) > 100:
            await ctx.send("Community name must be 100 characters or less.")
            return
        
        await self.config_service.set_community_name(ctx.guild.id, name)
        embed = await self.branding_service.success_embed(
            ctx.guild.id,
            title="Community Name Updated",
            description=f"Community name set to: {name}"
        )
        await ctx.send(embed=embed)
        logger.info(f"Community name set to '{name}' for guild {ctx.guild.id}")
    
    @branding_group.command(name="setdescription")
    @commands.guild_only()
    async def branding_setdescription(self, ctx: commands.Context, *, description: str) -> None:
        """Set community description."""
        if not self._check_permissions(ctx):
            await ctx.send("You don't have permission to use this command.")
            return
        
        if len(description) > 500:
            await ctx.send("Description must be 500 characters or less.")
            return
        
        await self.config_service.set_community_description(ctx.guild.id, description)
        embed = await self.branding_service.success_embed(
            ctx.guild.id,
            title="Description Updated",
            description="Community description has been updated."
        )
        await ctx.send(embed=embed)
        logger.info(f"Description updated for guild {ctx.guild.id}")
    
    @branding_group.command(name="setlogo")
    @commands.guild_only()
    async def branding_setlogo(self, ctx: commands.Context, url: str) -> None:
        """Set logo URL."""
        if not self._check_permissions(ctx):
            await ctx.send("You don't have permission to use this command.")
            return
        
        if not self.branding_service.validate_url(url):
            await ctx.send("Please provide a valid URL.")
            return
        
        await self.config_service.set_logo_url(ctx.guild.id, url)
        embed = await self.branding_service.success_embed(
            ctx.guild.id,
            title="Logo Updated",
            description="Logo URL has been updated.",
            thumbnail=url
        )
        await ctx.send(embed=embed)
        logger.info(f"Logo URL set for guild {ctx.guild.id}")
    
    @branding_group.command(name="setcolor")
    @commands.guild_only()
    async def branding_setcolor(self, ctx: commands.Context, color: str) -> None:
        """Set embed color (hex format: #RRGGBB or 0xRRGGBB)."""
        if not self._check_permissions(ctx):
            await ctx.send("You don't have permission to use this command.")
            return
        
        color_int = self.branding_service.parse_color(color)
        if color_int is None:
            embed = await self.branding_service.error_embed(
                ctx.guild.id,
                title="Invalid Color",
                description="Please provide a valid hex color (e.g., #5865F2 or 0x5865F2)."
            )
            await ctx.send(embed=embed)
            return
        
        await self.config_service.set_embed_color(ctx.guild.id, color_int)
        embed = await self.branding_service.success_embed(
            ctx.guild.id,
            title="Color Updated",
            description=f"Embed color has been updated.",
            color=color_int
        )
        await ctx.send(embed=embed)
        logger.info(f"Embed color set to {color} for guild {ctx.guild.id}")
    
    @branding_group.command(name="setfooter")
    @commands.guild_only()
    async def branding_setfooter(self, ctx: commands.Context, text: str) -> None:
        """Set footer text."""
        if not self._check_permissions(ctx):
            await ctx.send("You don't have permission to use this command.")
            return
        
        if len(text) > 200:
            await ctx.send("Footer text must be 200 characters or less.")
            return
        
        await self.config_service.set_footer_text(ctx.guild.id, text)
        embed = await self.branding_service.success_embed(
            ctx.guild.id,
            title="Footer Updated",
            description="Footer text has been updated."
        )
        await ctx.send(embed=embed)
        logger.info(f"Footer text updated for guild {ctx.guild.id}")
    
    @branding_group.command(name="setfootericon")
    @commands.guild_only()
    async def branding_setfootericon(self, ctx: commands.Context, url: str) -> None:
        """Set footer icon URL."""
        if not self._check_permissions(ctx):
            await ctx.send("You don't have permission to use this command.")
            return
        
        if not self.branding_service.validate_url(url):
            await ctx.send("Please provide a valid URL.")
            return
        
        await self.config_service.set_footer_icon_url(ctx.guild.id, url)
        embed = await self.branding_service.success_embed(
            ctx.guild.id,
            title="Footer Icon Updated",
            description="Footer icon URL has been updated."
        )
        await ctx.send(embed=embed)
        logger.info(f"Footer icon URL set for guild {ctx.guild.id}")
    
    @branding_group.command(name="setwebsite")
    @commands.guild_only()
    async def branding_setwebsite(self, ctx: commands.Context, url: str) -> None:
        """Set website URL."""
        if not self._check_permissions(ctx):
            await ctx.send("You don't have permission to use this command.")
            return
        
        if not self.branding_service.validate_url(url):
            await ctx.send("Please provide a valid URL.")
            return
        
        await self.config_service.set_website_url(ctx.guild.id, url)
        embed = await self.branding_service.success_embed(
            ctx.guild.id,
            title="Website Updated",
            description="Website URL has been updated."
        )
        await ctx.send(embed=embed)
        logger.info(f"Website URL set for guild {ctx.guild.id}")
    
    @branding_group.command(name="setinvite")
    @commands.guild_only()
    async def branding_setinvite(self, ctx: commands.Context, url: str) -> None:
        """Set Discord invite link."""
        if not self._check_permissions(ctx):
            await ctx.send("You don't have permission to use this command.")
            return
        
        if not self.branding_service.validate_url(url):
            await ctx.send("Please provide a valid URL.")
            return
        
        await self.config_service.set_discord_invite(ctx.guild.id, url)
        embed = await self.branding_service.success_embed(
            ctx.guild.id,
            title="Invite Link Updated",
            description="Invite link has been updated."
        )
        await ctx.send(embed=embed)
        logger.info(f"Invite link set for guild {ctx.guild.id}")
    
    @branding_group.command(name="setemoji")
    @commands.guild_only()
    async def branding_setemoji(self, ctx: commands.Context, emoji: str) -> None:
        """Set custom emoji."""
        if not self._check_permissions(ctx):
            await ctx.send("You don't have permission to use this command.")
            return
        
        if len(emoji) > 50:
            await ctx.send("Emoji must be 50 characters or less.")
            return
        
        await self.config_service.set_community_emoji(ctx.guild.id, emoji)
        embed = await self.branding_service.success_embed(
            ctx.guild.id,
            title="Emoji Updated",
            description=f"Custom emoji set to: {emoji}"
        )
        await ctx.send(embed=embed)
        logger.info(f"Custom emoji set for guild {ctx.guild.id}")
    
    # Channel commands
    @commands.command(name="channel")
    @commands.guild_only()
    async def channel_group(self, ctx: commands.Context) -> None:
        """Base command for channel configuration."""
        await ctx.send_help(self.channel_group)
    
    @channel_group.command(name="session")
    @commands.guild_only()
    async def channel_session(self, ctx: commands.Context, channel: discord.TextChannel) -> None:
        """Set session channel."""
        if not self._check_permissions(ctx):
            await ctx.send("You don't have permission to use this command.")
            return
        
        await self.config_service.set_session_channel(ctx.guild.id, channel.id)
        embed = await self.branding_service.success_embed(
            ctx.guild.id,
            title="Session Channel Updated",
            description=f"Session channel set to {channel.mention}"
        )
        await ctx.send(embed=embed)
        logger.info(f"Session channel set to {channel.id} for guild {ctx.guild.id}")
    
    @channel_group.command(name="logs")
    @commands.guild_only()
    async def channel_logs(self, ctx: commands.Context, channel: discord.TextChannel) -> None:
        """Set logs channel."""
        if not self._check_permissions(ctx):
            await ctx.send("You don't have permission to use this command.")
            return
        
        await self.config_service.set_logs_channel(ctx.guild.id, channel.id)
        embed = await self.branding_service.success_embed(
            ctx.guild.id,
            title="Logs Channel Updated",
            description=f"Logs channel set to {channel.mention}"
        )
        await ctx.send(embed=embed)
        logger.info(f"Logs channel set to {channel.id} for guild {ctx.guild.id}")
    
    # Role commands
    @commands.command(name="roles")
    @commands.guild_only()
    async def roles_group(self, ctx: commands.Context) -> None:
        """Base command for role configuration."""
        await ctx.send_help(self.roles_group)
    
    @roles_group.command(name="admin")
    @commands.guild_only()
    async def roles_admin(self, ctx: commands.Context, role: discord.Role) -> None:
        """Set admin role."""
        if not self._check_permissions(ctx):
            await ctx.send("You don't have permission to use this command.")
            return
        
        await self.config_service.set_admin_role(ctx.guild.id, role.id)
        embed = await self.branding_service.success_embed(
            ctx.guild.id,
            title="Admin Role Updated",
            description=f"Admin role set to {role.mention}"
        )
        await ctx.send(embed=embed)
        logger.info(f"Admin role set to {role.id} for guild {ctx.guild.id}")
    
    @roles_group.command(name="management")
    @commands.guild_only()
    async def roles_management(self, ctx: commands.Context, role: discord.Role) -> None:
        """Set management role."""
        if not self._check_permissions(ctx):
            await ctx.send("You don't have permission to use this command.")
            return
        
        await self.config_service.set_management_role(ctx.guild.id, role.id)
        embed = await self.branding_service.success_embed(
            ctx.guild.id,
            title="Management Role Updated",
            description=f"Management role set to {role.mention}"
        )
        await ctx.send(embed=embed)
        logger.info(f"Management role set to {role.id} for guild {ctx.guild.id}")
    
    @roles_group.command(name="host")
    @commands.guild_only()
    async def roles_host(self, ctx: commands.Context, role: discord.Role) -> None:
        """Set host role."""
        if not self._check_permissions(ctx):
            await ctx.send("You don't have permission to use this command.")
            return
        
        await self.config_service.set_host_role(ctx.guild.id, role.id)
        embed = await self.branding_service.success_embed(
            ctx.guild.id,
            title="Host Role Updated",
            description=f"Host role set to {role.mention}"
        )
        await ctx.send(embed=embed)
        logger.info(f"Host role set to {role.id} for guild {ctx.guild.id}")
    
    @roles_group.command(name="moderator")
    @commands.guild_only()
    async def roles_moderator(self, ctx: commands.Context, role: discord.Role) -> None:
        """Set moderator role."""
        if not self._check_permissions(ctx):
            await ctx.send("You don't have permission to use this command.")
            return
        
        await self.config_service.set_moderator_role(ctx.guild.id, role.id)
        embed = await self.branding_service.success_embed(
            ctx.guild.id,
            title="Moderator Role Updated",
            description=f"Moderator role set to {role.mention}"
        )
        await ctx.send(embed=embed)
        logger.info(f"Moderator role set to {role.id} for guild {ctx.guild.id}")


async def setup(bot: commands.Bot) -> None:
    """Setup function for the admin cog."""
    await bot.add_cog(Admin(bot))
