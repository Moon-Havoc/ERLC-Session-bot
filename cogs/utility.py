"""Utility cog for helpful commands and information."""

from __future__ import annotations

import discord
from discord.ext import commands

from services import BrandingService
from utils import get_embed_helper, get_logger

logger = get_logger(__name__)


class Utility(commands.Cog):
    """Utility commands for general information and help."""
    
    def __init__(self, bot: commands.Bot) -> None:
        """Initialize utility cog."""
        self.bot = bot
        self.branding_service = BrandingService()
    
    @commands.Cog.listener()
    async def on_ready(self) -> None:
        """Called when the cog is ready."""
        logger.info("Utility cog loaded")
    
    @commands.command(name="ping")
    async def ping(self, ctx: commands.Context) -> None:
        """Check bot latency."""
        embed_helper = get_embed_helper()
        
        latency = round(self.bot.latency * 1000)
        
        embed = embed_helper.create_info_embed(
            title="Pong!",
            description=f"Latency: {latency}ms"
        )
        await ctx.send(embed=embed)
    
    @commands.command(name="info")
    async def info(self, ctx: commands.Context) -> None:
        """Show bot information."""
        embed_helper = get_embed_helper()
        
        from config import config
        
        # Get branding if available
        branding = None
        if ctx.guild:
            branding = await self.branding_service.get_branding(ctx.guild.id)
            if branding:
                embed_helper.set_branding(branding)
        
        fields = [
            ("Version", config.bot_version, True),
            ("Python", "3.12+", True),
            ("Library", "discord.py 2.x", True),
            ("Servers", str(len(self.bot.guilds)), True),
            ("Users", str(len(self.bot.users)), True)
        ]
        
        if branding:
            fields.insert(0, ("Community", branding.community_name, True))
        
        embed = embed_helper.create_info_embed(
            title=config.bot_description,
            fields=fields
        )
        await ctx.send(embed=embed)
    
    @commands.command(name="commands")
    async def help_command(self, ctx: commands.Context, *, command_name: Optional[str] = None) -> None:
        """Show help information."""
        embed_helper = get_embed_helper()
        
        # Get branding if available
        if ctx.guild:
            branding = await self.branding_service.get_branding(ctx.guild.id)
            if branding:
                embed_helper.set_branding(branding)
        
        if command_name:
            # Show help for specific command
            command = self.bot.get_command(command_name)
            if command:
                signature = f"{ctx.prefix}{command.qualified_name} {command.signature}"
                
                fields = [
                    ("Usage", f"```{signature}```", False),
                    ("Description", command.help or "No description available.", False)
                ]
                
                if command.aliases:
                    fields.append(("Aliases", ", ".join(command.aliases), True))
                
                embed = embed_helper.create_info_embed(
                    title=f"Command: {command.name}",
                    fields=fields
                )
            else:
                embed = embed_helper.create_error_embed(
                    title="Command Not Found",
                    description=f"Command `{command_name}` not found."
                )
        else:
            # Show general help
            fields = []
            
            # Group commands by cog
            cogs = {}
            for cmd in self.bot.commands:
                if cmd.cog and cmd.cog.qualified_name != "Utility":
                    cog_name = cmd.cog.qualified_name
                    if cog_name not in cogs:
                        cogs[cog_name] = []
                    cogs[cog_name].append(cmd.name)
            
            # Add cog sections
            for cog_name, commands_list in cogs.items():
                fields.append((cog_name, ", ".join(f"`{cmd}`" for cmd in commands_list), False))
            
            # Add utility commands
            utility_commands = [cmd.name for cmd in self.bot.commands if cmd.cog and cmd.cog.qualified_name == "Utility"]
            if utility_commands:
                fields.append(("Utility", ", ".join(f"`{cmd}`" for cmd in utility_commands), False))
            
            embed = embed_helper.create_info_embed(
                title="Available Commands",
                description="Use `/help <command>` for more information on a specific command.",
                fields=fields
            )
        
        await ctx.send(embed=embed)
    
    @commands.command(name="invite")
    async def invite(self, ctx: commands.Context) -> None:
        """Get bot invite link."""
        embed_helper = get_embed_helper()
        
        # Get branding if available
        branding = None
        if ctx.guild:
            branding = await self.branding_service.get_branding(ctx.guild.id)
            if branding:
                embed_helper.set_branding(branding)
        
        invite_url = branding.invite_link if branding else None
        
        if invite_url:
            embed = embed_helper.create_info_embed(
                title="Invite Link",
                description=f"Join the community: [Click Here]({invite_url})"
            )
        else:
            # Generate OAuth2 invite link for the bot
            from config import config
            invite_url = f"https://discord.com/oauth2/authorize?client_id={self.bot.user.id}&permissions=8&scope=bot%20applications.commands"
            
            embed = embed_helper.create_info_embed(
                title="Bot Invite",
                description=f"Add this bot to your server: [Click Here]({invite_url})"
            )
        
        await ctx.send(embed=embed)
    
    @commands.command(name="website")
    async def website(self, ctx: commands.Context) -> None:
        """Get community website link."""
        embed_helper = get_embed_helper()
        
        # Get branding if available
        if ctx.guild:
            branding = await self.branding_service.get_branding(ctx.guild.id)
            if branding:
                embed_helper.set_branding(branding)
                
                if branding.website_url:
                    embed = embed_helper.create_info_embed(
                        title="Website",
                        description=f"Visit our website: [Click Here]({branding.website_url})"
                    )
                    await ctx.send(embed=embed)
                    return
        
        embed = embed_helper.create_error_embed(
            title="Website Not Configured",
            description="No website URL has been configured for this server."
        )
        await ctx.send(embed=embed)
    
    @commands.command(name="avatar")
    async def avatar(self, ctx: commands.Context, user: Optional[discord.Member] = None) -> None:
        """Show user avatar."""
        target_user = user or ctx.author
        embed_helper = get_embed_helper()
        
        embed = embed_helper.create_info_embed(
            title=f"{target_user.name}'s Avatar",
            image=target_user.avatar.url if target_user.avatar else target_user.default_avatar.url
        )
        await ctx.send(embed=embed)
    
    @commands.command(name="server")
    @commands.guild_only()
    async def server_info(self, ctx: commands.Context) -> None:
        """Show server information."""
        embed_helper = get_embed_helper()
        
        # Get branding if available
        branding = await self.branding_service.get_branding(ctx.guild.id)
        if branding:
            embed_helper.set_branding(branding)
        
        guild = ctx.guild
        
        fields = [
            ("Owner", guild.owner.mention, True),
            ("Members", str(guild.member_count), True),
            ("Channels", str(len(guild.channels)), True),
            ("Roles", str(len(guild.roles)), True),
            ("Created", guild.created_at.strftime("%Y-%m-%d"), True),
            ("ID", str(guild.id), True)
        ]
        
        embed = embed_helper.create_info_embed(
            title=guild.name,
            description=guild.description or "No description set.",
            fields=fields,
            thumbnail=guild.icon.url if guild.icon else None
        )
        await ctx.send(embed=embed)
    
    @commands.command(name="user")
    async def user_info(self, ctx: commands.Context, user: Optional[discord.Member] = None) -> None:
        """Show user information."""
        target_user = user or ctx.author
        embed_helper = get_embed_helper()
        
        # Get branding if available
        if ctx.guild:
            branding = await self.branding_service.get_branding(ctx.guild.id)
            if branding:
                embed_helper.set_branding(branding)
        
        fields = [
            ("ID", str(target_user.id), True),
            ("Created", target_user.created_at.strftime("%Y-%m-%d"), True),
            ("Bot", "Yes" if target_user.bot else "No", True)
        ]
        
        if isinstance(target_user, discord.Member):
            fields.extend([
                ("Joined", target_user.joined_at.strftime("%Y-%m-%d") if target_user.joined_at else "N/A", True),
                ("Roles", ", ".join(role.name for role in target_user.roles[1:]), True)
            ])
        
        embed = embed_helper.create_info_embed(
            title=str(target_user),
            fields=fields,
            thumbnail=target_user.avatar.url if target_user.avatar else target_user.default_avatar.url
        )
        await ctx.send(embed=embed)


async def setup(bot: commands.Bot) -> None:
    """Setup function for the utility cog."""
    await bot.add_cog(Utility(bot))
