# Changelog

All notable changes to SessionCore will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Complete session management core with lifecycle control
- SessionService with single active session per guild enforcement
- Session caching with automatic restoration on bot startup
- Background task system for live session updates (60-second intervals)
- Session commands: `/session start`, `/session end`, `/session info`
- Session model with comprehensive fields (server_code, notes, vote_count, boost_count, duration)
- Session embeds with live duration and relative timestamps
- Database migration 003 for updated session schema
- Graceful session message and channel deletion handling
- Permission checks for session management (Host, Management, Admin, Server Admin)
- Session summary generation for ended sessions
- Automatic session restoration on bot startup
- Background task cleanup on bot shutdown

### Changed
- Updated SessionStatus enum (COMPLETED → ENDED)
- Refactored SessionService to be single source of truth for session operations
- Updated SessionRepository methods for new schema
- Added session caching and background update tasks
- Enhanced Session model with properties (is_active, duration_str)
- Updated bot initialization to restore active sessions
- Updated bot shutdown to cleanup session background tasks

### Fixed
- Session persistence across bot restarts
- Only one active session per guild enforcement
- Graceful handling of deleted session messages/channels
- Background task cleanup on session end
- Proper session duration calculation

### Security
- Permission checks for session start/end operations
- Channel permission validation before session creation
- Input validation for server codes and notes

### Database
- Migration 003: Updated session schema for session management core
- Added fields: server_code, notes, started_at, ended_at, session_channel_id, session_message_id, vote_count, boost_count, duration
- Removed legacy fields: session_type, title, scheduled_time, max_participants, current_participants
- Changed status: 'completed' → 'ended'

### Architecture
- Session caching layer for performance
- Background task system for live updates
- Session lifecycle management with proper cleanup
- Database-driven session state persistence
- Future-proof design for additional session features

## [1.1.0] - 2026-07-30

### Added
- Complete session management core with lifecycle control
- SessionService with single active session per guild enforcement
- Session caching with automatic restoration on bot startup
- Background task system for live session updates (60-second intervals)
- Session commands: `/session start`, `/session end`, `/session info`
- Session model with comprehensive fields (server_code, notes, vote_count, boost_count, duration)
- Session embeds with live duration and relative timestamps
- Database migration 003 for updated session schema
- Graceful session message and channel deletion handling
- Permission checks for session management (Host, Management, Admin, Server Admin)
- Session summary generation for ended sessions
- Automatic session restoration on bot startup
- Background task cleanup on bot shutdown

### Changed
- Updated SessionStatus enum (COMPLETED → ENDED)
- Refactored SessionService to be single source of truth for session operations
- Updated SessionRepository methods for new schema
- Added session caching and background update tasks
- Enhanced Session model with properties (is_active, duration_str)
- Updated bot initialization to restore active sessions
- Updated bot shutdown to cleanup session background tasks

### Fixed
- Session persistence across bot restarts
- Only one active session per guild enforcement
- Graceful handling of deleted session messages/channels
- Background task cleanup on session end
- Proper session duration calculation

### Security
- Permission checks for session start/end operations
- Channel permission validation before session creation
- Input validation for server codes and notes

### Database
- Migration 003: Updated session schema for session management core
- Added fields: server_code, notes, started_at, ended_at, session_channel_id, session_message_id, vote_count, boost_count, duration
- Removed legacy fields: session_type, title, scheduled_time, max_participants, current_participants
- Changed status: 'completed' → 'ended'

### Architecture
- Session caching layer for performance
- Background task system for live updates
- Session lifecycle management with proper cleanup
- Database-driven session state persistence
- Future-proof design for additional session features

## [1.0.0] - 2026-07-30

### Added
- Initial release of SessionCore Discord bot framework
- Complete configuration and branding system with database storage
- ConfigService with 5-minute caching for performance
- BrandingService with automatic embed branding
- Comprehensive slash commands for configuration management
- URL and hex color validation
- Permission checks requiring server admin or configured admin role
- Configuration cache invalidation on updates
- Helper methods for all configuration aspects
- Automatic guild configuration on bot join
- Database migration system (version 2)
- PROJECT_STATE.md documentation
- ARCHITECTURE.md documentation
- Modular cog architecture with separation of concerns
- Database abstraction layer with repository pattern
- Migration system for schema changes
- Permission system with configurable Discord roles
- Structured logging with configurable levels
- Admin cog with configuration commands
- Session cog structure (foundation)
- Stats cog structure (foundation)
- Utility cog with helper commands
- Embed helpers with branding support
- Discord UI components (ConfirmView, PaginationView, SessionModal, SelectMenuView)
- Command checks and permissions
- Main bot entry point with automatic setup
- Environment variable configuration
- SQLite database with proper schema
- Type hints throughout
- Async throughout for optimal performance

### Changed
- Merged branding fields into GuildConfig model for unified configuration
- Updated all database queries to support new schema
- Refactored ConfigService to include caching layer
- Refactored BrandingService to use ConfigService and provide embed helpers
- Updated all cogs to use new service methods
- Simplified bot initialization to use ConfigService.ensure_guild_config()
- Updated utility commands to use BrandingService embed methods

### Deprecated
- Separate Branding model (kept for backward compatibility)
- Old embed helper utilities (being phased out in favor of BrandingService)

### Fixed
- Configuration changes now immediately reflected due to cache invalidation
- Permission checks now properly check both server admin and configured roles
- URL validation for branding fields
- Color parsing for hex format validation

### Security
- API credentials moved to unified configuration
- Added input validation for all configuration fields
- Enhanced permission checking for configuration commands

### Database Schema
- Guild configuration table with merged branding fields
- Sessions table (foundation)
- Session participants table
- Session statistics table
- Votes table
- Boosts table
- Hosts table

### Architecture
- Service-based business logic layer
- Repository pattern for data access
- Cache-aside pattern for performance
- Optional dependency pattern for API service
- Clean separation between cogs, services, and data access

### Documentation
- Comprehensive README with installation and usage instructions
- Project structure documentation
- Architecture overview
- Configuration examples
- Development guidelines

## [Future Versions]

### Database Schema
- Guild configuration table with merged branding fields
- Sessions table (foundation)
- Session participants table
- Session statistics table
- Votes table
- Boosts table
- Hosts table

## [Future Versions]

### Planned
- Session management commands implementation
- Statistics and leaderboard commands
- Automated testing infrastructure
- API documentation
- Health check endpoints
- Monitoring and metrics integration
- Database backup strategies
- Redis caching for distributed deployments
- PostgreSQL migration option
- Webhook support system
- Plugin architecture for extensibility
