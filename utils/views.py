"""Discord UI views and components for SessionCore."""

from typing import Optional, Callable, Awaitable, List, Dict, Any
import discord
from discord.ui import View, Button, Modal, TextInput, Select

from .logger import get_logger

logger = get_logger(__name__)


class ConfirmView(View):
    """A confirmation view with yes/no buttons."""
    
    def __init__(self, author: discord.abc.User, timeout: float = 180.0) -> None:
        """Initialize confirmation view."""
        super().__init__(timeout=timeout)
        self.author = author
        self.value: Optional[bool] = None
        self.confirmed_callback: Optional[Callable] = None
        self.denied_callback: Optional[Callable] = None
    
    def set_callbacks(
        self,
        confirmed: Optional[Callable] = None,
        denied: Optional[Callable] = None
    ) -> None:
        """Set callbacks for confirmed/denied actions."""
        self.confirmed_callback = confirmed
        self.denied_callback = denied
    
    @discord.ui.button(label="Yes", style=discord.ButtonStyle.green)
    async def confirm(self, interaction: discord.Interaction, button: discord.ui.Button) -> None:
        """Handle confirm button click."""
        self.value = True
        self.stop()
        
        if self.confirmed_callback:
            try:
                await self.confirmed_callback(interaction)
            except Exception as e:
                logger.error(f"Error in confirmed callback: {e}")
        
        await interaction.response.edit_message(view=None)
    
    @discord.ui.button(label="No", style=discord.ButtonStyle.red)
    async def deny(self, interaction: discord.Interaction, button: discord.ui.Button) -> None:
        """Handle deny button click."""
        self.value = False
        self.stop()
        
        if self.denied_callback:
            try:
                await self.denied_callback(interaction)
            except Exception as e:
                logger.error(f"Error in denied callback: {e}")
        
        await interaction.response.edit_message(view=None)
    
    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        """Ensure only the author can interact."""
        if interaction.user.id != self.author.id:
            await interaction.response.send_message(
                "You cannot interact with this view.",
                ephemeral=True
            )
            return False
        return True


class PaginationView(View):
    """A pagination view for navigating through pages."""
    
    def __init__(
        self,
        author: discord.abc.User,
        pages: List[discord.Embed],
        timeout: float = 180.0
    ) -> None:
        """Initialize pagination view."""
        super().__init__(timeout=timeout)
        self.author = author
        self.pages = pages
        self.current_page = 0
    
    def get_current_page(self) -> discord.Embed:
        """Get the current page embed."""
        return self.pages[self.current_page]
    
    def update_buttons(self) -> None:
        """Update button states based on current page."""
        self.first_page.disabled = self.current_page == 0
        self.previous_page.disabled = self.current_page == 0
        self.next_page.disabled = self.current_page == len(self.pages) - 1
        self.last_page.disabled = self.current_page == len(self.pages) - 1
    
    @discord.ui.button(label="⏮", style=discord.ButtonStyle.secondary)
    async def first_page(self, interaction: discord.Interaction, button: discord.ui.Button) -> None:
        """Go to first page."""
        self.current_page = 0
        self.update_buttons()
        await interaction.response.edit_message(embed=self.get_current_page(), view=self)
    
    @discord.ui.button(label="◀", style=discord.ButtonStyle.secondary)
    async def previous_page(self, interaction: discord.Interaction, button: discord.ui.Button) -> None:
        """Go to previous page."""
        self.current_page = max(0, self.current_page - 1)
        self.update_buttons()
        await interaction.response.edit_message(embed=self.get_current_page(), view=self)
    
    @discord.ui.button(label="▶", style=discord.ButtonStyle.secondary)
    async def next_page(self, interaction: discord.Interaction, button: discord.ui.Button) -> None:
        """Go to next page."""
        self.current_page = min(len(self.pages) - 1, self.current_page + 1)
        self.update_buttons()
        await interaction.response.edit_message(embed=self.get_current_page(), view=self)
    
    @discord.ui.button(label="⏭", style=discord.ButtonStyle.secondary)
    async def last_page(self, interaction: discord.Interaction, button: discord.ui.Button) -> None:
        """Go to last page."""
        self.current_page = len(self.pages) - 1
        self.update_buttons()
        await interaction.response.edit_message(embed=self.get_current_page(), view=self)
    
    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        """Ensure only the author can interact."""
        if interaction.user.id != self.author.id:
            await interaction.response.send_message(
                "You cannot interact with this view.",
                ephemeral=True
            )
            return False
        return True


class SessionModal(Modal, title="Create Session"):
    """Modal for creating a new session."""
    
    title_input = TextInput(
        label="Session Title",
        placeholder="Enter session title...",
        style=discord.TextStyle.short,
        required=True,
        max_length=100
    )
    
    description_input = TextInput(
        label="Description",
        placeholder="Enter session description...",
        style=discord.TextStyle.paragraph,
        required=False,
        max_length=1000
    )
    
    type_input = TextInput(
        label="Session Type",
        placeholder="e.g., Training, Patrol, Meeting",
        style=discord.TextStyle.short,
        required=True,
        max_length=50
    )
    
    def __init__(self, callback: Callable) -> None:
        """Initialize session modal."""
        super().__init__()
        self.callback = callback
    
    async def on_submit(self, interaction: discord.Interaction) -> None:
        """Handle modal submission."""
        try:
            await self.callback(
                interaction,
                self.title_input.value,
                self.description_input.value,
                self.type_input.value
            )
        except Exception as e:
            logger.error(f"Error in session modal callback: {e}")
            await interaction.response.send_message(
                "An error occurred while creating the session.",
                ephemeral=True
            )


    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        """Ensure only the author can interact."""
        if interaction.user.id != self.author.id:
            await interaction.response.send_message(
                "You cannot interact with this view.",
                ephemeral=True
            )
            return False
        return True


class BoostModal(Modal, title="Add Boost Note"):
    """Modal for adding a boost note."""
    
    note_input = TextInput(
        label="Boost Note (Optional)",
        placeholder="Enter a note for this boost...",
        style=discord.TextStyle.paragraph,
        required=False,
        max_length=500
    )
    
    def __init__(self, callback: Callable) -> None:
        """Initialize boost modal."""
        super().__init__()
        self.callback = callback
    
    async def on_submit(self, interaction: discord.Interaction) -> None:
        """Handle modal submission."""
        try:
            await self.callback(interaction, self.note_input.value)
        except Exception as e:
            logger.error(f"Error in boost modal callback: {e}")
            await interaction.response.send_message(
                "An error occurred while adding your boost.",
                ephemeral=True
            )


class SessionControlsView(View):
    """Persistent view for session controls with vote, boost, refresh, and info buttons."""
    
    def __init__(
        self,
        guild_id: int,
        session_id: int,
        session_service,
        branding_service,
        config_service,
        embed_callback: Optional[Callable] = None,
        custom_id: Optional[str] = None
    ) -> None:
        """Initialize session controls view."""
        super().__init__(timeout=None)  # Persistent view
        self.guild_id = guild_id
        self.session_id = session_id
        self.session_service = session_service
        self.branding_service = branding_service
        self.config_service = config_service
        self.embed_callback = embed_callback
        self.custom_id = custom_id or f"session_controls_{guild_id}_{session_id}"
    
    async def update_embed(self, message: discord.Message) -> None:
        """Update the session embed."""
        try:
            session = await self.session_service.get_active_session(self.guild_id)
            if not session:
                return
            
            if self.embed_callback:
                embed = await self.embed_callback(self.guild_id, session)
            else:
                # Fallback: create basic embed
                embed = await self._create_basic_embed(message, session)
            
            await message.edit(embed=embed, view=self)
        except Exception as e:
            logger.error(f"Error updating session embed: {e}")
    
    async def _create_basic_embed(self, message: discord.Message, session) -> discord.Embed:
        """Create a basic session embed as fallback."""
        config = await self.config_service.get_guild_config(self.guild_id)
        community_name = config.community_name if config else "Community"
        
        # Get host member
        try:
            guild = message.guild
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
            self.guild_id,
            title=f"Session #{session.id}" if session.id else "Session",
            fields=fields
        )
        
        # Add timestamp for last updated
        embed.timestamp = discord.utils.utcnow()
        
        return embed
    
    @discord.ui.button(label="👍 Vote", style=discord.ButtonStyle.primary, emoji="👍")
    async def vote_button(self, interaction: discord.Interaction, button: discord.ui.Button) -> None:
        """Handle vote button click."""
        try:
            # Check if user already voted
            if await self.session_service.has_user_voted(self.guild_id, interaction.user.id):
                await interaction.response.send_message(
                    "You have already voted for this session.",
                    ephemeral=True
                )
                return
            
            # Record vote
            session = await self.session_service.vote(self.guild_id, interaction.user.id)
            if not session:
                await interaction.response.send_message(
                    "Failed to record your vote.",
                    ephemeral=True
                )
                return
            
            # Update embed
            await self.update_embed(interaction.message)
            
            await interaction.response.send_message(
                "Your vote has been recorded!",
                ephemeral=True
            )
        except Exception as e:
            logger.error(f"Error in vote button: {e}")
            await interaction.response.send_message(
                "An error occurred while recording your vote.",
                ephemeral=True
            )
    
    @discord.ui.button(label="⚡ Boost", style=discord.ButtonStyle.success, emoji="⚡")
    async def boost_button(self, interaction: discord.Interaction, button: discord.ui.Button) -> None:
        """Handle boost button click."""
        try:
            # Open boost modal
            modal = BoostModal(self._on_boost_submit)
            await interaction.response.send_modal(modal)
        except Exception as e:
            logger.error(f"Error in boost button: {e}")
            await interaction.response.send_message(
                "An error occurred while opening the boost modal.",
                ephemeral=True
            )
    
    async def _on_boost_submit(self, interaction: discord.Interaction, note: Optional[str] = None) -> None:
        """Handle boost modal submission."""
        try:
            # Record boost
            session = await self.session_service.boost(self.guild_id, interaction.user.id, note)
            if not session:
                await interaction.response.send_message(
                    "Failed to record your boost.",
                    ephemeral=True
                )
                return
            
            # Update embed
            await self.update_embed(interaction.message)
            
            await interaction.response.send_message(
                "Your boost has been recorded!",
                ephemeral=True
            )
        except Exception as e:
            logger.error(f"Error in boost submit: {e}")
            await interaction.response.send_message(
                "An error occurred while recording your boost.",
                ephemeral=True
            )
    
    @discord.ui.button(label="🔄 Refresh", style=discord.ButtonStyle.secondary, emoji="🔄")
    async def refresh_button(self, interaction: discord.Interaction, button: discord.ui.Button) -> None:
        """Handle refresh button click."""
        try:
            # Update embed
            await self.update_embed(interaction.message)
            
            await interaction.response.send_message(
                "Session information refreshed!",
                ephemeral=True
            )
        except Exception as e:
            logger.error(f"Error in refresh button: {e}")
            await interaction.response.send_message(
                "An error occurred while refreshing.",
                ephemeral=True
            )
    
    @discord.ui.button(label="ℹ️ Info", style=discord.ButtonStyle.secondary, emoji="ℹ️")
    async def info_button(self, interaction: discord.Interaction, button: discord.ui.Button) -> None:
        """Handle info button click."""
        try:
            session = await self.session_service.get_active_session(self.guild_id)
            if not session:
                await interaction.response.send_message(
                    "No active session found.",
                    ephemeral=True
                )
                return
            
            # Get host member
            try:
                guild = interaction.guild
                host = guild.get_member(session.host_id) if guild else None
                host_name = host.display_name if host else f"<@{session.host_id}>"
            except Exception:
                host_name = f"<@{session.host_id}>"
            
            fields = [
                ("Host", host_name, True),
                ("Duration", session.duration_str, True),
                ("Started", discord.utils.format_dt(session.started_at, style="R") if session.started_at else "N/A", True),
                ("Votes", str(session.vote_count), True),
                ("Boosts", str(session.boost_count), True),
                ("Status", "Active" if session.is_active else "Ended", True)
            ]
            
            if session.notes:
                fields.insert(2, ("Notes", session.notes, False))
            
            embed = await self.branding_service.create_embed(
                self.guild_id,
                title="Session Information",
                fields=fields
            )
            
            await interaction.response.send_message(embed=embed, ephemeral=True)
        except Exception as e:
            logger.error(f"Error in info button: {e}")
            await interaction.response.send_message(
                "An error occurred while retrieving session information.",
                ephemeral=True
            )


class SessionEndConfirmView(View):
    """Confirmation view for ending a session."""
    
    def __init__(
        self,
        guild_id: int,
        session_id: int,
        session_service,
        branding_service,
        author: discord.Member,
        embed_callback: Optional[Callable] = None
    ) -> None:
        """Initialize session end confirmation view."""
        super().__init__(timeout=180.0)
        self.guild_id = guild_id
        self.session_id = session_id
        self.session_service = session_service
        self.branding_service = branding_service
        self.author = author
        self.embed_callback = embed_callback
    
    @discord.ui.button(label="✅ Confirm End", style=discord.ButtonStyle.danger, emoji="✅")
    async def confirm_button(self, interaction: discord.Interaction, button: discord.ui.Button) -> None:
        """Handle confirm button click."""
        try:
            # End session
            ended_session = await self.session_service.end_session(self.guild_id)
            if not ended_session:
                await interaction.response.send_message(
                    "Failed to end the session.",
                    ephemeral=True
                )
                return
            
            # Update original session embed
            if ended_session.session_channel_id and ended_session.session_message_id:
                try:
                    guild = interaction.guild
                    channel = guild.get_channel(ended_session.session_channel_id)
                    if channel and isinstance(channel, discord.TextChannel):
                        try:
                            message = await channel.fetch_message(ended_session.session_message_id)
                            if self.embed_callback:
                                embed = await self.embed_callback(self.guild_id, ended_session)
                            else:
                                # Fallback simple embed
                                embed = await self.branding_service.create_embed(
                                    self.guild_id,
                                    title=f"Session #{ended_session.id}",
                                    description="Session ended"
                                )
                            await message.edit(embed=embed, view=None)  # Remove controls
                        except discord.NotFound:
                            logger.warning(f"Session message {ended_session.session_message_id} not found")
                        except Exception as e:
                            logger.error(f"Error updating session message: {e}")
                except Exception as e:
                    logger.error(f"Error getting session channel: {e}")
            
            # Create and send session summary
            summary_embed = await self._create_session_summary_embed(self.guild_id, ended_session)
            
            # Try to send to session channel, fallback to current channel
            if ended_session.session_channel_id:
                try:
                    guild = interaction.guild
                    summary_channel = guild.get_channel(ended_session.session_channel_id)
                    if summary_channel and isinstance(summary_channel, discord.TextChannel):
                        await summary_channel.send(embed=summary_embed)
                except Exception as e:
                    logger.error(f"Error sending summary to session channel: {e}")
                    await interaction.followup.send(embed=summary_embed)
            else:
                await interaction.followup.send(embed=summary_embed)
            
            # Remove persistent view
            persistent_view_manager.remove_view(f"session_controls_{self.guild_id}_{self.session_id}")
            
            await interaction.response.send_message(
                f"Session ended. Duration: {ended_session.duration_str}",
                ephemeral=True
            )
            
            self.stop()
            logger.info(f"Session {ended_session.id} ended by {self.author.id}")
        except Exception as e:
            logger.error(f"Error in confirm button: {e}")
            await interaction.response.send_message(
                "An error occurred while ending the session.",
                ephemeral=True
            )
    
    async def _create_session_summary_embed(self, guild_id: int, session) -> discord.Embed:
        """Create a session summary embed for ended sessions."""
        config = await self.branding_service.config_service.get_guild_config(guild_id)
        community_name = config.community_name if config else "Community"
        
        # Get host member
        try:
            # We don't have guild access here, so just use mention
            host_name = f"<@{session.host_id}>"
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
    
    @discord.ui.button(label="❌ Cancel", style=discord.ButtonStyle.secondary, emoji="❌")
    async def cancel_button(self, interaction: discord.Interaction, button: discord.ui.Button) -> None:
        """Handle cancel button click."""
        await interaction.response.send_message(
            "Session end cancelled.",
            ephemeral=True
        )
        self.stop()
    
    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        """Ensure only the author can interact."""
        if interaction.user.id != self.author.id:
            await interaction.response.send_message(
                "Only the person who initiated the session end can confirm.",
                ephemeral=True
            )
            return False
        return True


class PersistentViewManager:
    """Manager for persistent Discord views across bot restarts."""
    
    def __init__(self) -> None:
        """Initialize persistent view manager."""
        self._active_views: Dict[str, View] = {}
        self._view_data: Dict[str, Dict[str, Any]] = {}
    
    def register_view(self, custom_id: str, view: View, metadata: Optional[Dict[str, Any]] = None) -> None:
        """Register a persistent view."""
        self._active_views[custom_id] = view
        if metadata:
            self._view_data[custom_id] = metadata
        logger.debug(f"Registered persistent view: {custom_id}")
    
    def get_view(self, custom_id: str) -> Optional[View]:
        """Get a registered view by custom ID."""
        return self._active_views.get(custom_id)
    
    def get_view_metadata(self, custom_id: str) -> Optional[Dict[str, Any]]:
        """Get metadata for a view."""
        return self._view_data.get(custom_id)
    
    def remove_view(self, custom_id: str) -> None:
        """Remove a persistent view."""
        if custom_id in self._active_views:
            del self._active_views[custom_id]
        if custom_id in self._view_data:
            del self._view_data[custom_id]
        logger.debug(f"Removed persistent view: {custom_id}")
    
    def get_all_views(self) -> Dict[str, View]:
        """Get all registered views."""
        return self._active_views.copy()
    
    def clear_all(self) -> None:
        """Clear all persistent views."""
        self._active_views.clear()
        self._view_data.clear()
        logger.info("Cleared all persistent views")


# Global persistent view manager
persistent_view_manager = PersistentViewManager()
