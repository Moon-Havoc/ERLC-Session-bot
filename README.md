# SessionCore

A production-ready, modular Discord bot framework designed to power multiple ER:LC communities from a single reusable codebase. SessionCore provides a clean, scalable foundation for session management with configurable branding and multi-community support.

## Features

- **Modular Cog Architecture**: Clean separation of concerns with extensible command modules
- **Configurable Branding**: Community-specific customization without code changes
- **Database Abstraction Layer**: Type-safe database operations with migration support
- **Permission System**: Flexible role-based access control
- **Structured Logging**: Comprehensive logging with configurable levels
- **API Integration**: Optional external API support with auto-disable
- **Slash Commands**: Modern Discord slash command interface
- **Async Throughout**: Fully asynchronous for optimal performance

## Requirements

- Python 3.12+
- discord.py 2.x
- SQLite

## Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd SessionCore
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Configure environment variables:
```bash
cp .env.example .env
```

4. Edit `.env` with your configuration:
```env
DISCORD_TOKEN=your_discord_bot_token_here
COMMAND_PREFIX=!
BOT_OWNER_ID=123456789012345678
DATABASE_PATH=sessioncore.db
```

## Configuration

### Environment Variables

| Variable | Description | Required | Default |
|----------|-------------|----------|---------|
| `DISCORD_TOKEN` | Discord bot token | Yes | - |
| `COMMAND_PREFIX` | Bot command prefix | No | `!` |
| `BOT_OWNER_ID` | Bot owner Discord ID | No | - |
| `DATABASE_PATH` | SQLite database path | No | `sessioncore.db` |
| `API_BASE_URL` | External API base URL | No | - |
| `API_KEY` | External API key | No | - |
| `API_TIMEOUT` | API request timeout (seconds) | No | `30` |
| `LOG_LEVEL` | Logging level | No | `INFO` |
| `LOG_FILE` | Log file path | No | - |
| `BOT_DESCRIPTION` | Bot description | No | `A modular Discord bot framework...` |
| `BOT_VERSION` | Bot version | No | `1.0.0` |

### Initial Setup

1. Start the bot:
```bash
python bot.py
```

2. In your Discord server, run:
```
/config setup
```

This initializes the server configuration and default branding.

3. Configure roles:
```
/config roles @AdminRole @ModeratorRole @HostRole @MemberRole
```

4. Configure channels:
```
/config channels #log-channel #session-channel #welcome-channel
```

5. Customize branding:
```
/branding name "Your Community Name"
/branding description "Your community description"
/branding color #5865F2
/branding logo https://example.com/logo.png
```

## Usage

### Available Commands

#### Configuration Commands (`/config`)
- `setup` - Initialize server configuration
- `roles` - Configure permission roles
- `channels` - Configure bot channels
- `autorole` - Toggle auto role functionality

#### Branding Commands (`/branding`)
- `name` - Set community name
- `description` - Set community description
- `color` - Set embed color
- `logo` - Set logo URL
- `footer` - Set footer text and icon
- `website` - Set website URL
- `invite` - Set invite link
- `emoji` - Set custom emoji

#### Utility Commands
- `ping` - Check bot latency
- `info` - Show bot information
- `commands` - Display help information
- `invite` - Get community invite link
- `website` - Get community website
- `avatar` - Show user avatar
- `server` - Show server information
- `user` - Show user information

#### Session Commands (`/sessions`)
*Structure in place, commands to be implemented*

#### Stats Commands (`/stats`)
*Structure in place, commands to be implemented*

## Architecture

### Project Structure

```
SessionCore/
├── bot.py                 # Main bot entry point
├── config.py              # Configuration management
├── requirements.txt        # Python dependencies
├── .env.example          # Environment variables template
├── README.md             # This file
├── database/             # Database layer
│   ├── __init__.py
│   ├── database.py       # Database abstraction layer
│   ├── models.py         # Data models
│   └── migrations.py     # Migration system
├── services/             # Business logic layer
│   ├── __init__.py
│   ├── branding.py       # Branding service
│   ├── session_service.py # Session management
│   ├── stats_service.py  # Statistics service
│   ├── api_service.py    # External API integration
│   └── config_service.py # Configuration service
├── cogs/                 # Discord commands
│   ├── __init__.py
│   ├── admin.py          # Administrative commands
│   ├── session.py        # Session commands
│   ├── stats.py          # Statistics commands
│   └── utility.py        # Utility commands
├── utils/                # Utilities and helpers
│   ├── __init__.py
│   ├── embeds.py         # Embed helpers
│   ├── checks.py         # Command checks
│   ├── permissions.py    # Permission system
│   ├── views.py          # Discord UI views
│   └── logger.py         # Logging utilities
└── assets/               # Static assets
```

### Database Schema

#### Guild Configuration
- Guild-specific settings
- Role mappings (admin, moderator, host, member)
- Channel assignments
- Auto role settings

#### Branding
- Community name and description
- Visual customization (colors, logos, emojis)
- Footer configuration
- External links (website, invite)

#### Sessions
- Session metadata (type, title, description)
- Scheduling information
- Participant tracking
- Status management

#### Session Statistics
- Per-session metrics
- User performance data
- Attendance tracking

#### Votes
- Session voting system
- Target-based voting

#### Boosts
- Server boost tracking
- User boost history

#### Hosts
- Host performance metrics
- Session hosting statistics
- Rating system

### Permission System

The permission system supports configurable Discord roles:

- **Admin**: Full administrative access
- **Moderator**: Moderation capabilities
- **Host**: Session hosting permissions
- **Member**: Basic member access
- **Everyone**: Public access

Permissions are checked using decorators:
```python
@commands.command()
@is_admin()
async def admin_command(self, ctx):
    # Admin-only command
```

### Branding System

Branding is stored in the database and can be customized without code changes:

- Community name and description
- Embed colors
- Logo and footer images
- Custom emojis
- Website and invite links

All embeds automatically use the configured branding.

### API Integration

The API service is optional and automatically disables if no credentials are provided:

```python
# API calls gracefully fail if not configured
if api_service.is_available():
    await api_service.sync_session(session_data)
```

## Development

### Adding New Commands

1. Create a new cog in `cogs/`:
```python
from discord.ext import commands

class MyCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    @commands.command()
    async def mycommand(self, ctx):
        await ctx.send("Hello!")

async def setup(bot):
    await bot.add_cog(MyCog(bot))
```

2. Register the cog in `bot.py`:
```python
await self.load_extension("cogs.my_cog")
```

### Database Migrations

To add a new migration:

1. Define migration functions in `database/migrations.py`:
```python
def migration_002_add_new_table(cursor: sqlite3.Cursor) -> None:
    cursor.execute("CREATE TABLE new_table (...)")

def migration_002_rollback(cursor: sqlite3.Cursor) -> None:
    cursor.execute("DROP TABLE new_table")
```

2. Register the migration:
```python
runner.register(Migration(
    version=2,
    name="add_new_table",
    up=migration_002_add_new_table,
    down=migration_002_rollback
))
```

### Adding Services

Create a new service in `services/`:
```python
class MyService:
    def __init__(self):
        self.repository = MyRepository(database)
    
    async def do_something(self):
        return await self.repository.get_data()
```

## Deployment

### Production Considerations

1. **Environment Variables**: Ensure all sensitive data is in environment variables
2. **Database Backups**: Implement regular SQLite database backups
3. **Logging**: Configure file logging for production monitoring
4. **Error Handling**: Monitor logs for errors and exceptions
5. **Rate Limiting**: Respect Discord API rate limits
6. **Security**: Keep dependencies updated and monitor for vulnerabilities

### Running as a Service

Use a process manager like systemd or supervisor to keep the bot running:

**systemd example:**
```ini
[Unit]
Description=SessionCore Bot
After=network.target

[Service]
Type=simple
User=botuser
WorkingDirectory=/path/to/SessionCore
ExecStart=/usr/bin/python3 bot.py
Restart=always

[Install]
WantedBy=multi-user.target
```

## License

[Specify your license here]

## Support

For issues, questions, or contributions, please contact the development team.

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## Changelog

### Version 1.0.0
- Initial release
- Core framework implementation
- Database abstraction layer
- Configurable branding system
- Permission system
- Admin and utility commands
- Session and stats service foundations
