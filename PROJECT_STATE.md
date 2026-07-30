# Project State

## Overview
SessionCore is a production-ready Discord bot framework designed to power multiple ER:LC communities from a single reusable codebase. The project is currently in active development with a focus on core infrastructure.

## Current Status: Foundation Complete
The core framework architecture is complete and operational. The project provides a solid foundation for community-specific customization and session management.

## Completed Components

### ✅ Database Layer
- **Models**: Complete data models with type hints
  - `GuildConfig` - Comprehensive guild configuration including branding
  - `Session`, `SessionParticipant`, `SessionStats` - Session management
  - `Vote`, `Boost`, `Host` - Community engagement tracking
- **Repository Pattern**: Database abstraction layer preventing raw SQL in business logic
- **Migration System**: Version-controlled schema changes with rollback support
- **Current Schema Version**: 2 (merged branding into guild_config)

### ✅ Configuration System
- **ConfigService**: Centralized configuration management with caching
  - 5-minute cache TTL for performance
  - Automatic cache invalidation on updates
  - Helper methods for all configuration aspects
- **Environment Variables**: Secure configuration via .env
- **Guild-Specific Configuration**: Each guild has exactly one configuration record
- **Auto-Configuration**: Default configuration created on guild join

### ✅ Branding System
- **BrandingService**: Community customization service
  - Automatic embed branding (colors, footers, logos)
  - Helper methods: `success_embed()`, `error_embed()`, `warning_embed()`, `info_embed()`
  - URL and color validation
- **Database-Stored Branding**: All branding configurable without code changes
- **Supported Branding Elements**:
  - Community name and description
  - Logo URL and embed colors
  - Footer text and icon
  - Custom emoji
  - Website and invite links

### ✅ Permission System
- **Role-Based Access Control**: Configurable Discord roles
- **Permission Levels**: Admin, Management, Host, Moderator, Member, Everyone
- **Automatic Checks**: Decorator-based permission validation
- **Server Admin Override**: Server administrators always have access

### ✅ Services Layer
- **ConfigService**: Configuration management with caching
- **BrandingService**: Branding and embed creation
- **SessionService**: Complete session lifecycle management
  - Single active session per guild enforcement
  - Session caching with automatic restoration
  - Background task for live duration updates
  - Graceful shutdown and cleanup
- **StatsService**: Statistics tracking foundation
- **APIService**: Optional external API integration with auto-disable

### ✅ Cogs Layer
- **Admin Cog**: Complete configuration and branding commands
  - `/config view` - View server configuration
  - `/branding setname/setdescription/setlogo/setcolor/setfooter/setfootericon/setwebsite/setinvite/setemoji`
  - `/channel session/logs` - Channel configuration
  - `/roles admin/management/host/moderator` - Role configuration
- **Session Cog**: Complete session management commands
  - `/session start <server_code> [notes]` - Start a new session
  - `/session end` - End the active session
  - `/session info` - Display active session information
- **Stats Cog**: Structure ready for statistics commands
- **Utility Cog**: General utility commands (ping, info, help, invite, website, avatar, server, user)

### ✅ Utilities Layer
- **Logger**: Structured logging with configurable levels
- **Embeds**: Branded embed helpers
- **Permissions**: Permission system and checks
- **Views**: Discord UI components (ConfirmView, PaginationView, SessionModal, SelectMenuView)

### ✅ Main Application
- **Bot Entry Point**: Clean initialization with proper error handling
- **Automatic Setup**: Database migrations and default configuration
- **Event Handlers**: Guild join/leave with auto-configuration

## In Progress

### 🚧 Session Management Core
- **Status**: Core implementation complete
- **Features**: Single active session per guild, session lifecycle management, background updates
- **Commands**: `/session start`, `/session end`, `/session info`
- **Validation**: Permission checks, channel verification, error handling
- **Persistence**: Sessions survive bot restarts with automatic restoration
- **Background Updates**: 60-second interval for duration and timestamp updates

## Not Started

### 📋 Statistics Functionality  
- Leaderboard systems
- User statistics tracking
- Host performance metrics
- Period-based statistics

### 📋 API Integration
- External API sync for sessions
- External API sync for statistics
- Webhook support
- API authentication enhancements

### 📋 Session Participant Management
- Player tracking
- Attendance recording
- Player statistics
- Join/leave functionality

## Architecture Decisions

### Unified Configuration
**Decision**: Merged branding into GuildConfig model
**Rationale**: 
- Single source of truth for guild settings
- Simpler data access patterns
- Reduced database queries
- Easier cache management

### Caching Strategy
**Decision**: 5-minute TTL cache for configuration
**Rationale**:
- Balances performance with data freshness
- Reduces database load
- Simple implementation
- Sufficient for configuration data

### Service-Based Architecture
**Decision**: All business logic in services, no direct database access in cogs
**Rationale**:
- Separation of concerns
- Testability
- Reusability
- Future scalability

### Optional API Integration
**Decision**: API service auto-disables if no credentials
**Rationale**:
- Core functionality doesn't depend on external services
- Graceful degradation
- Easy deployment for different use cases

## Technical Debt

### Minor
- Some utility commands still use old embed helper pattern (being updated)
- Branding model kept for backward compatibility (can be removed in v2.0)

### Future Considerations
- Consider Redis for distributed caching if scaling to multiple bot instances
- Add database connection pooling for high-traffic scenarios
- Implement rate limiting for configuration changes

## Dependencies
- Python 3.12+
- discord.py 2.3.0+
- python-dotenv 1.0.0+
- aiohttp 3.9.0+

## Development Guidelines

### Code Style
- Follow PEP8
- Use type hints throughout
- Async/await for all I/O operations
- No global state
- Structured logging

### Database Operations
- Always use repository methods
- Never execute raw SQL in cogs or services
- Use migrations for schema changes
- Test migrations in development first

### Configuration Changes
- Use ConfigService helper methods
- Validate all user input
- Cache is automatically invalidated on updates
- Log all configuration changes

### Branding
- Always use BrandingService for embeds
- Never manually build branding in cogs
- Validate URLs and colors
- Branding changes are immediately reflected

## Testing Status

### Manual Testing Completed
- ✅ Bot startup and initialization
- ✅ Database migrations
- ✅ Configuration creation and updates
- ✅ Branding changes reflected in embeds
- ✅ Permission checks
- ✅ Guild join auto-configuration

### Automated Testing
- ❌ No automated tests yet
- 📋 Planned: Unit tests for services
- 📋 Planned: Integration tests for cogs
- 📋 Planned: Database migration tests

## Deployment Readiness

### Production Considerations
- ✅ Environment variable configuration
- ✅ Structured logging for monitoring
- ✅ Error handling throughout
- ✅ Database persistence
- ✅ Automatic schema migrations
- ⚠️ No health check endpoint
- ⚠️ No metrics/monitoring integration
- ⚠️ No automated backups

### Required for Production
- Database backup strategy
- Process manager (systemd/supervisor)
- Log rotation
- Monitoring/alerting
- Health checks

## Next Priorities

1. **Complete Session Commands** - Implement session creation and management
2. **Complete Statistics Commands** - Implement leaderboards and user stats
3. **Testing Infrastructure** - Add automated tests
4. **Documentation** - API documentation and deployment guide
5. **Monitoring** - Add health checks and metrics

## Notes

- The project uses SQLite for simplicity but can be migrated to PostgreSQL if needed
- All branding is database-stored and can be changed without code deployment
- The permission system is flexible and can be extended with additional roles
- The API service is designed to be optional and gracefully degrades when unavailable
- Configuration changes are immediately effective due to cache invalidation
