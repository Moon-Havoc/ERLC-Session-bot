# Changelog

All notable changes to SessionCore will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
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

## [1.0.0] - 2026-07-30

### Added
- Initial release of SessionCore Discord bot framework
- Modular cog architecture with separation of concerns
- Database abstraction layer with repository pattern
- Migration system for schema changes
- ConfigService for guild configuration
- BrandingService for community customization
- SessionService for session management (foundation)
- StatsService for statistics tracking (foundation)
- APIService with optional external integration
- Permission system with configurable Discord roles
- Structured logging with configurable levels
- Admin cog with configuration commands
- Session cog structure (no commands)
- Stats cog structure (no commands)
- Utility cog with helper commands
- Embed helpers with branding support
- Discord UI components (ConfirmView, PaginationView, SessionModal, SelectMenuView)
- Command checks and permissions
- Main bot entry point with automatic setup
- Environment variable configuration
- SQLite database with proper schema
- Type hints throughout
- Async throughout for optimal performance

### Database Schema
- Guild configuration table
- Branding table
- Sessions table
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
