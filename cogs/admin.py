"""Admin cog for server configuration and management."""

from __future__ import annotations

from typing import Optional
import discord
from discord.ext import commands

from services import ConfigService, BrandingService
from utils import (
    is_admin, guild_configured, branding_configured,
    get_embed_helper, get_logger
)

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
    
    @commands.group(name="config", invoke_without_command=True)
    @commands.guild_only()
    @is_admin()
    async def config(self, ctx: commands.Context) -> None:
        """Base command for configuration."""
        await ctx.send_help(self.config)
    
    @config.command(name="setup")
    @commands.guild_only()
    @is_admin()
    async def setup_config(self, ctx: commands.Context) -> None:
        """Initialize server configuration."""
        embed_helper = get_embed_helper()
        
        try:
            # Create guild config
            await self.config_service.create_guild_config(ctx.guild.id)
            
            # Create default branding
            await self.branding_service.create_branding(
                ctx.guild.id,
                community_name=ctx.guild.name
            )
            
            embed = embed_helper.create_success_embed(
                title="Configuration Created",
                description="Server configuration has been initialized. Use `/config` commands to customize settings."
            )
            await ctx.send(embed=embed)
            
            logger.info(f"Configuration initialized for guild {ctx.guild.id}")
        except Exception as e:
            logger.error(f"Error setting up config: {e}")
            embed = embed_helper.create_error_embed(
                title="Configuration Error",
                description="Failed to initialize configuration. Check logs for details."
            )
            await ctx.send(embed=embed)
    
    @config.command(name="roles")
    @commands.guild_only()
    @is_admin()
    async def config_roles(
        self,
        ctx: commands.Context,
        admin_role: Optional[discord.Role] = None,
        moderator_role: Optional[discord.Role] = None,
        host_role: Optional[discord.Role] = None,
        member_role: Optional[discord.Role] = None
    ) -> None:
        """Configure permission roles."""
        embed_helper = get_embed_helper()
        
        try:
            await self.config_service.update_guild_config(
                ctx.guild.id,
                admin_role_id=admin_role.id if admin_role else None,
                moderator_role_id=moderator_role.id if moderator_role else None,
                host_role_id=host_role.id if host_role else None,
                member_role_id=member_role.id if member_role else None
            )
            
            embed = embed_helper.create_success_embed(
                title="Roles Configured",
                description="Permission roles have been updated."
            )
            await ctx.send(embed=embed)
            
            logger.info(f"Roles configured for guild {ctx.guild.id}")
        except Exception as e:
            logger.error(f"Error configuring roles: {e}")
            embed = embed_helper.create_error_embed(
                title="Configuration Error",
                description="Failed to configure roles."
            )
            await ctx.send(embed=embed)
    
    @config.command(name="channels")
    @commands.guild_only()
    @is_admin()
    async def config_channels(
        self,
        ctx: commands.Context,
        log_channel: Optional[discord.TextChannel] = None,
        session_channel: Optional[discord.TextChannel] = None,
        welcome_channel: Optional[discord.TextChannel] = None
    ) -> None:
        """Configure bot channels."""
        embed_helper = get_embed_helper()
        
        try:
            await self.config_service.update_guild_config(
                ctx.guild.id,
                log_channel_id=log_channel.id if log_channel else None,
                session_channel_id=session_channel.id if session_channel else None,
                welcome_channel_id=welcome_channel.id if welcome_channel else None
            )
            
            embed = embed_helper.create_success_embed(
                title="Channels Configured",
                description="Bot channels have been updated."
            )
            await ctx.send(embed=embed)
            
            logger.info(f"Channels configured for guild {ctx.guild.id}")
        except Exception as e:
            logger.error(f"Error configuring channels: {e}")
            embed = embed_helper.create_error_embed(
                title="Configuration Error",
                description="Failed to configure channels."
            )
            await ctx.send(embed=embed)
    
    @config.command(name="autorole")
    @commands.guild_only()
    @is_admin()
    async def config_autorole(self, ctx: commands.Context, enabled: bool) -> None:
        """Toggle auto role functionality."""
        embed_helper = get_embed_helper()
        
        try:
            await self.config_service.update_guild_config(
                ctx.guild.id,
                auto_role_enabled=enabled
            )
            
            status = "enabled" if enabled else "disabled"
            embed = embed_helper.create_success_embed(
                title="Auto Role Updated",
                description=f"Auto role has been {status}."
            )
            await ctx.send(embed=embed)
            
            logger.info(f"Auto role set to {enabled} for guild {ctx.guild.id}")
        except Exception as e:
            logger.error(f"Error configuring auto role: {e}")
            embed = embed_helper.create_error_embed(
                title="Configuration Error",
                description="Failed to update auto role setting."
            )
            await ctx.send(embed=embed)
    
    @commands.group(name="branding", invoke_without_command=True)
    @commands.guild_only()
    @is_admin()
    async def branding_group(self, ctx: commands.Context) -> None:
        """Base command for branding configuration."""
        await ctx.send_help(self.branding_group)
    
    @branding_group.command(name="name")
    @commands.guild_only()
    @is_admin()
    async def branding_name(self, ctx: commands.Context, name: str) -> None:
        """Set community name."""
        embed_helper = get_embed_helper()
        
        try:
            await self.branding_service.set_community_name(ctx.guild.id, name)
            
            embed = embed_helper.create_success_embed(
                title="Community Name Updated",
                description=f"Community name set to: {name}"
            )
            await ctx.send(embed=embed)
            
            logger.info(f"Community name set to '{name}' for guild {ctx.guild.id}")
        except Exception as e:
            logger.error(f"Error setting community name: {e}")
            embed = embed_helper.create_error_embed(
                title="Branding Error",
                description="Failed to update community name."
            )
            await ctx.send(embed=embed)
    
    @branding_group.command(name="description")
    @commands.guild_only()
    @is_admin()
    async def branding_description(self, ctx: commands.Context, *, description: str) -> None:
        """Set community description."""
        embed_helper = get_embed_helper()
        
        try:
            await self.branding_service.set_description(ctx.guild.id, description)
            
            embed = embed_helper.create_success_embed(
                title="Description Updated",
                description="Community description has been updated."
            )
            await ctx.send(embed=embed)
            
            logger.info(f"Description updated for guild {ctx.guild.id}")
        except Exception as e:
            logger.error(f"Error setting description: {e}")
            embed = embed_helper.create_error_embed(
                title="Branding Error",
                description="Failed to update description."
            )
            await ctx.send(embed=embed)
    
    @branding_group.command(name="color")
    @commands.guild_only()
    @is_admin()
    async def branding_color(self, ctx: commands.Context, color: str) -> None:
        """Set embed color (hex format: #RRGGBB or 0xRRGGBB)."""
        embed_helper = get_embed_helper()
        
        try:
            color_int = self.branding_service.parse_color(color)
            if color_int is None:
                embed = embed_helper.create_error_embed(
                    title="Invalid Color",
                    description="Please provide a valid hex color (e.g., #5865F2 or 0x5865F2)."
                )
                await ctx.send(embed=embed)
                return
            
            await self.branding_service.set_embed_color(ctx.guild.id, color_int)
            
            embed = embed_helper.create_success_embed(
                title="Color Updated",
                description=f"Embed color has been updated.",
                color=color_int
            )
            await ctx.send(embed=embed)
            
            logger.info(f"Embed color set to {color} for guild {ctx.guild.id}")
        except Exception as e:
            logger.error(f"Error setting color: {e}")
            embed = embed_helper.create_error_embed(
                title="Branding Error",
                description="Failed to update embed color."
            )
            await ctx.send(embed=embed)
    
    @branding_group.command(name="logo")
    @commands.guild_only()
    @is_admin()
    async def branding_logo(self, ctx: commands.Context, url: str) -> None:
        """Set logo URL."""
        embed_helper = get_embed_helper()
        
        try:
            await self.branding_service.set_logo_url(ctx.guild.id, url)
            
            embed = embed_helper.create_success_embed(
                title="Logo Updated",
                description="Logo URL has been updated.",
                thumbnail=url
            )
            await ctx.send(embed=embed)
            
            logger.info(f"Logo URL set for guild {ctx.guild.id}")
        except Exception as e:
            logger.error(f"Error setting logo: {e}")
            embed = embed_helper.create_error_embed(
                title="Branding Error",
                description="Failed to update logo URL."
            )
            await ctx.send(embed=embed)
    
    @branding_group.command(name="footer")
    @commands.guild_only()
    @is_admin()
    async def branding_footer(self, ctx: commands.Context, text: str, icon_url: Optional[str] = None) -> None:
        """Set footer text and optional icon URL."""
        embed_helper = get_embed_helper()
        
        try:
            await self.branding_service.set_footer_text(ctx.guild.id, text)
            if icon_url:
                await self.branding_service.set_footer_icon(ctx.guild.id, icon_url)
            
            embed = embed_helper.create_success_embed(
                title="Footer Updated",
                description="Footer has been updated."
            )
            await ctx.send(embed=embed)
            
            logger.info(f"Footer updated for guild {ctx.guild.id}")
        except Exception as e:
            logger.error(f"Error setting footer: {e}")
            embed = embed_helper.create_error_embed(
                title="Branding Error",
                description="Failed to update footer."
            )
            await ctx.send(embed=embed)
    
    @branding_group.command(name="website")
    @commands.guild_only()
    @is_admin()
    async def branding_website(self, ctx: commands.Context, url: str) -> None:
        """Set website URL."""
        embed_helper = get_embed_helper()
        
        try:
            await self.branding_service.set_website_url(ctx.guild.id, url)
            
            embed = embed_helper.create_success_embed(
                title="Website Updated",
                description="Website URL has been updated."
            )
            await ctx.send(embed=embed)
            
            logger.info(f"Website URL set for guild {ctx.guild.id}")
        except Exception as e:
            logger.error(f"Error setting website: {e}")
            embed = embed_helper.create_error_embed(
                title="Branding Error",
                description="Failed to update website URL."
            )
            await ctx.send(embed=embed)
    
    @branding_group.command(name="invite")
    @commands.guild_only()
    @is_admin()
    async def branding_invite(self, ctx: commands.Context, url: str) -> None:
        """Set invite link."""
        embed_helper = get_embed_helper()
        
        try:
            await self.branding_service.set_invite_link(ctx.guild.id, url)
            
            embed = embed_helper.create_success_embed(
                title="Invite Link Updated",
                description="Invite link has been updated."
            )
            await ctx.send(embed=embed)
            
            logger.info(f"Invite link set for guild {ctx.guild.id}")
        except Exception as e:
            logger.error(f"Error setting invite: {e}")
            embed = embed_helper.create_error_embed(
                title="Branding Error",
                description="Failed to update invite link."
            )
            await ctx.send(embed=embed)
    
    @branding_group.command(name="emoji")
    @commands.guild_only()
    @is_admin()
    async def branding_emoji(self, ctx: commands.Context, emoji: str) -> None:
        """Set custom emoji."""
        embed_helper = get_embed_helper()
        
        try:
            await self.branding_service.set_custom_emoji(ctx.guild.id, emoji)
            
            embed = embed_helper.create_success_embed(
                title="Emoji Updated",
                description=f"Custom emoji set to: {emoji}"
            )
            await ctx.send(embed=embed)
            
            logger.info(f"Custom emoji set for guild {ctx.guild.id}")
        except Exception as e:
            logger.error(f"Error setting emoji: {e}")
            embed = embed_helper.create_error_embed(
                title="Branding Error",
                description="Failed to update custom emoji."
            )
            await ctx.send(embed=embed)
    
    @commands.command(name="status")
    @commands.guild_only()
    @is_admin()
    async def status(self, ctx: commands.Context) -> None:
        """Show current server configuration status."""
        embed_helper = get_embed_helper()
        
        try:
            guild_config = await self.config_service.get_guild_config(ctx.guild.id)
            branding = await self.branding_service.get_branding(ctx.guild.id)
            
            config_status = "✅ Configured" if guild_config else "❌ Not Configured"
            branding_status = "✅ Configured" if branding else "❌ Not Configured"
            
            fields = [
                ("Configuration Status", config_status, True),
                ("Branding Status", branding_status, True)
            ]
            
            if guild_config:
                fields.extend([
                    ("Admin Role", f"<@{guild_config.admin_role_id}>" if guild_config.admin_role_id else "Not set", True),
                    ("Moderator Role", f"<@{guild_config.moderator_role_id}>" if guild_config.moderator_role_id else "Not set", True),
                    ("Host Role", f"<@{guild_config.host_role_id}>" if guild_config.host_role_id else "Not set", True),
                    ("Member Role", f"<@{guild_config.member_role_id}>" if guild_config.member_role_id else "Not set", True),
                    ("Auto Role", "Enabled" if guild_config.auto_role_enabled else "Disabled", True)
                ])
            
            if branding:
                fields.extend([
                    ("Community Name", branding.community_name, True),
                    ("Embed Color", f"#{branding.embed_color:06X}", True)
                ])
            
            embed = embed_helper.create_info_embed(
                title="Server Status",
                fields=fields
            )
            await ctx.send(embed=embed)
            
        except Exception as e:
            logger.error(f"Error getting status: {e}")
            embed = embed_helper.create_error_embed(
                title="Status Error",
                description="Failed to retrieve server status."
            )
            await ctx.send(embed=embed)


async def setup(bot: commands.Bot) -> None:
    """Setup function for the admin cog."""
    await bot.add_cog(Admin(bot))
