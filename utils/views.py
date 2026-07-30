"""Discord UI views and components for SessionCore."""

from typing import Optional, Callable, Awaitable, List
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


class SelectMenuView(View):
    """A view with a select menu for choosing options."""
    
    def __init__(
        self,
        author: discord.abc.User,
        options: List[discord.SelectOption],
        placeholder: str = "Select an option...",
        callback: Optional[Callable] = None,
        timeout: float = 180.0
    ) -> None:
        """Initialize select menu view."""
        super().__init__(timeout=timeout)
        self.author = author
        self.callback = callback
        
        self.select = Select(
            placeholder=placeholder,
            min_values=1,
            max_values=1,
            options=options
        )
        self.select.callback = self.on_select
        self.add_item(self.select)
    
    async def on_select(self, interaction: discord.Interaction) -> None:
        """Handle select menu interaction."""
        if self.callback:
            try:
                await self.callback(interaction, self.select.values[0])
            except Exception as e:
                logger.error(f"Error in select menu callback: {e}")
        
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
