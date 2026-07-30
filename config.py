"""Configuration management for SessionCore."""

import os
from dataclasses import dataclass
from typing import Optional
from dotenv import load_dotenv

load_dotenv()


@dataclass(frozen=True)
class Config:
    """Application configuration loaded from environment variables."""
    
    # Discord Bot Configuration
    discord_token: str
    command_prefix: str = "!"
    bot_owner_id: Optional[int] = None
    
    # Database Configuration
    database_path: str = "sessioncore.db"
    
    # API Configuration (Optional)
    api_base_url: Optional[str] = None
    api_key: Optional[str] = None
    api_timeout: int = 30
    
    # Logging Configuration
    log_level: str = "INFO"
    log_file: Optional[str] = None
    
    # Bot Configuration
    bot_description: str = "A modular Discord bot framework for session management"
    bot_version: str = "1.0.0"
    
    def __post_init__(self) -> None:
        """Validate configuration after initialization."""
        if not self.discord_token:
            raise ValueError("DISCORD_TOKEN is required")
        
        if self.log_level not in ("DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"):
            raise ValueError(f"Invalid log level: {self.log_level}")
    
    @property
    def api_enabled(self) -> bool:
        """Check if API integration is enabled."""
        return bool(self.api_base_url and self.api_key)


def load_config() -> Config:
    """Load configuration from environment variables."""
    return Config(
        discord_token=os.getenv("DISCORD_TOKEN", ""),
        command_prefix=os.getenv("COMMAND_PREFIX", "!"),
        bot_owner_id=int(os.getenv("BOT_OWNER_ID", 0)) or None,
        database_path=os.getenv("DATABASE_PATH", "sessioncore.db"),
        api_base_url=os.getenv("API_BASE_URL"),
        api_key=os.getenv("API_KEY"),
        api_timeout=int(os.getenv("API_TIMEOUT", "30")),
        log_level=os.getenv("LOG_LEVEL", "INFO"),
        log_file=os.getenv("LOG_FILE"),
        bot_description=os.getenv("BOT_DESCRIPTION", "A modular Discord bot framework for session management"),
        bot_version=os.getenv("BOT_VERSION", "1.0.0"),
    )


# Global configuration instance
config = load_config()
