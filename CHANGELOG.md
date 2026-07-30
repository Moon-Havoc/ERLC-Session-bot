# Changelog

All notable changes to SessionCore will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.3.0] - 2026-07-30

### Added
- ServiceContainer: Lightweight dependency injection container for all services
  - Singleton pattern for long-lived services
  - Automatic initialization and shutdown
  - Easy service registration for future services
- StatisticsService: Event-driven statistics tracking
  - Host statistics: sessions hosted, total time, votes, boosts
  - Guild statistics: total sessions, total time, longest session, average length
  - Automatic updates from event listeners
  - Leaderboard calculation methods
- AuditService: Complete audit logging
  - Records all session events with metadata
  - Query by guild, session, user, or event type
  - JSON metadata storage for flexibility
- Database migration 005 for statistics and audit tables
- HostStatistics model with formatted time properties
- GuildStatistics model with aggregate calculations
- AuditLog model with JSON metadata storage
- Statistics commands: `/stats session`, `/stats server`, `/stats host [user]`
- Leaderboard commands: `/leaderboard hosts`
- Event listeners for automatic statistics updates
- Event listeners for complete audit logging
- HostStatisticsRepository and GuildStatisticsRepository
- AuditLogRepository with multiple query methods
- Medal formatting for leaderboards (🥇🥈🥉)
- Service injection into bot initialization

### Changed
- Bot initialization now uses ServiceContainer
- Statistics and audit services automatically initialize on startup
- StatisticsService replaces StatsService (foundation)
- All services now managed by ServiceContainer
- Event listeners automatically registered on service initialization

### Fixed
- Statistics automatically update from events
- SessionService no longer directly modifies statistics
- Leaderboards calculate correctly from database
- Audit logs record every published event
- Multiple guilds remain isolated

### Security
- Statistics viewing available to all members
- No special permissions required for statistics
- Audit logs designed for future permission controls

### Database
- Migration 005: Added host_statistics, guild_statistics, audit_logs tables
- HostStatistics: guild_id, user_id, sessions_hosted, total_hosted_time, total_votes, total_boosts, last_hosted
- GuildStatistics: guild_id, total_sessions, total_hosted_time, total_votes, total_boosts, longest_session, average_session_length
- AuditLog: guild_id, session_id, event_type, user_id, timestamp, metadata (JSON)
- Indexes on audit_logs for performance
- PRIMARY KEY on (guild_id, user_id) for host_statistics

### Architecture
- Dependency injection pattern for service management
- Event-driven statistics and audit logging
- Single source of truth for all statistics
- Future-proof design for API integration

## [1.2.0] - 2026-07-30

### Added
- Internal event system (EventService) for pub/sub pattern
  - Lightweight, no third-party dependencies
  - Event listeners with priority support
  - Async event publishing
  - Events: session_started, session_ended, vote_added, boost_added
- SessionVote and SessionBoost database models
- SessionVoteRepository and SessionBoostRepository
- Vote and boost commands: `/session vote`, `/session boost [note]`
- SessionService extensions for voting and boosting
  - vote(), boost(), has_user_voted(), get_vote_count(), get_boost_count()
  - get_session_statistics(), record_vote(), record_boost()
- Database migration 004 for vote and boost tables
- Event publishing on session lifecycle and engagement actions
- Immediate session embed updates on vote/boost
- UNIQUE constraint on votes (one vote per user per session)
- Multiple boosts allowed per user with optional notes
- Ephemeral responses for vote/boost commands
- Last updated timestamp on session embeds

### Changed
- SessionService now publishes events on session start/end
- SessionService now integrates with EventService
- Session embeds display vote and boost counts
- Session embeds show last updated timestamp
- Vote and boost counts persist across bot restarts

### Fixed
- Duplicate votes prevented at database level
- Multiple boosts work correctly
- Embed updates immediately on vote/boost
- Events published correctly on all actions

### Security
- No special permissions required for voting/boosting
- Available to all members who can view session channel
- Database constraints enforce vote uniqueness

### Database
- Migration 004: Added session_votes and session_boosts tables
- SessionVote: id, guild_id, session_id, user_id, created_at
- SessionBoost: id, guild_id, session_id, user_id, note, created_at
- UNIQUE constraint on (guild_id, session_id, user_id) for votes
- Indexes on session_id and user_id for performance
- ON DELETE CASCADE for referential integrity

### Architecture
- Event-driven architecture for extensibility
- Future features can subscribe to events without modifying core services
- Single source of truth pattern for all session operations
- Event system documented in ARCHITECTURE.md

## [Unreleased]

### Added
- Internal event system (EventService) for pub/sub pattern
  - Lightweight, no third-party dependencies
  - Event listeners with priority support
  - Async event publishing
  - Events: session_started, session_ended, vote_added, boost_added
- SessionVote and SessionBoost database models
- SessionVoteRepository and SessionBoostRepository
- Vote and boost commands: `/session vote`, `/session boost [note]`
- SessionService extensions for voting and boosting
  - vote(), boost(), has_user_voted(), get_vote_count(), get_boost_count()
  - get_session_statistics(), record_vote(), record_boost()
- Database migration 004 for vote and boost tables
- Event publishing on session lifecycle and engagement actions
- Immediate session embed updates on vote/boost
- UNIQUE constraint on votes (one vote per user per session)
- Multiple boosts allowed per user with optional notes
- Ephemeral responses for vote/boost commands
- Last updated timestamp on session embeds

### Changed
- SessionService now publishes events on session start/end
- SessionService now integrates with EventService
- Session embeds display vote and boost counts
- Session embeds show last updated timestamp
- Vote and boost counts persist across bot restarts

### Fixed
- Duplicate votes prevented at database level
- Multiple boosts work correctly
- Embed updates immediately on vote/boost
- Events published correctly on all actions

### Security
- No special permissions required for voting/boosting
- Available to all members who can view session channel
- Database constraints enforce vote uniqueness

### Database
- Migration 004: Added session_votes and session_boosts tables
- SessionVote: id, guild_id, session_id, user_id, created_at
- SessionBoost: id, guild_id, session_id, user_id, note, created_at
- UNIQUE constraint on (guild_id, session_id, user_id) for votes
- Indexes on session_id and user_id for performance
- ON DELETE CASCADE for referential integrity

### Architecture
- Event-driven architecture for extensibility
- Future features can subscribe to events without modifying core services
- Single source of truth pattern for all session operations
- Event system documented in ARCHITECTURE.md

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
