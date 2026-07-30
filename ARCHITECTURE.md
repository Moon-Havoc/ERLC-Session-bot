# Architecture Documentation

## System Overview

SessionCore is a modular Discord bot framework built with a layered architecture that separates concerns and provides clear boundaries between components. The system is designed to be maintainable, testable, and scalable.

## Architecture Principles

1. **Separation of Concerns**: Each layer has a specific responsibility
2. **Dependency Injection**: Services receive dependencies through constructors
3. **Repository Pattern**: Database access abstracted through repositories
4. **Service Layer**: Business logic isolated in services
5. **Caching**: Performance optimization through strategic caching
6. **Async-First**: All I/O operations are asynchronous
7. **Type Safety**: Strong type hints throughout
8. **No Global State**: State managed through services and repositories

## Layer Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     Discord Interface                         │
│                      (Cogs Layer)                            │
└────────────────────────┬────────────────────────────────────┘
                         │
┌────────────────────────▼────────────────────────────────────┐
│                     Business Logic                            │
│                    (Services Layer)                           │
└────────────────────────┬────────────────────────────────────┘
                         │
┌────────────────────────▼────────────────────────────────────┐
│                    Data Access                                │
│                   (Repositories Layer)                         │
└────────────────────────┬────────────────────────────────────┘
                         │
┌────────────────────────▼────────────────────────────────────┐
│                      Database                                 │
│                     (SQLite)                                  │
└─────────────────────────────────────────────────────────────┘
```

## Component Details

### 1. Cogs Layer (`cogs/`)

**Purpose**: Discord command interface and event handling

**Responsibilities**:
- Handle Discord events (on_ready, on_guild_join, etc.)
- Define and register Discord commands
- Validate user input
- Permission checking
- Response formatting

**Key Components**:
- `Admin` - Configuration and branding commands
- `Session` - Session management commands (structure ready)
- `Stats` - Statistics commands (structure ready)
- `Utility` - General utility commands

**Design Patterns**:
- Command groups for logical organization
- Decorator-based permission checks
- Service injection through constructors
- Consistent error handling

**Example**:
```python
class Admin(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot
        self.config_service = ConfigService()
        self.branding_service = BrandingService()
    
    @commands.command(name="config")
    @commands.guild_only()
    async def config_view(self, ctx: commands.Context) -> None:
        config = await self.config_service.get_guild_config(ctx.guild.id)
        # Process and respond
```

### 2. Services Layer (`services/`)

**Purpose**: Business logic and coordination

**Responsibilities**:
- Implement business rules
- Coordinate between repositories
- Provide caching for performance
- Handle validation
- External API integration

**Key Components**:
- `ConfigService` - Configuration management with caching
- `BrandingService` - Branding and embed creation
- `SessionService` - Session business logic
- `StatsService` - Statistics calculation
- `APIService` - External API integration

**Design Patterns**:
- Repository pattern for data access
- Cache-aside pattern for performance
- Strategy pattern for different embed types
- Optional dependency pattern for API service

**Example**:
```python
class ConfigService:
    def __init__(self) -> None:
        self.repository = GuildConfigRepository(database)
        self._cache: dict[int, GuildConfig] = {}
        self._cache_ttl: int = 300
    
    async def get_guild_config(self, guild_id: int) -> Optional[GuildConfig]:
        if self._is_cache_valid(guild_id):
            return self._cache[guild_id]
        config = await self.repository.get_by_guild(guild_id)
        if config:
            self._set_cache(config)
        return config
```

### 3. Repository Layer (`database/database.py`)

**Purpose**: Data access abstraction

**Responsibilities**:
- Execute database queries
- Map database rows to domain models
- Provide CRUD operations
- Handle database connections

**Key Components**:
- `Database` - Connection management
- `GuildConfigRepository` - Guild configuration operations
- `SessionRepository` - Session data operations
- `BrandingRepository` - Branding data operations (legacy)
- Other repositories for each domain model

**Design Patterns**:
- Repository pattern
- Connection pooling (via context managers)
- Row mapping to dataclasses
- Async database operations

**Example**:
```python
class GuildConfigRepository:
    def __init__(self, db: Database) -> None:
        self.db = db
    
    async def get_by_guild(self, guild_id: int) -> Optional[GuildConfig]:
        query = "SELECT * FROM guild_config WHERE guild_id = ?"
        row = await self.db.fetchone(query, (guild_id,))
        if row:
            return GuildConfig(**dict(row))
        return None
```

### 4. Database Layer (`database/`)

**Purpose**: Data persistence and schema management

**Responsibilities**:
- Database connection management
- Schema migrations
- Data integrity
- Query execution

**Key Components**:
- `Database` - Connection and query execution
- `models.py` - Domain models
- `migrations.py` - Schema versioning

**Design Patterns**:
- Migration pattern for schema changes
- Dataclass pattern for models
- Async context managers for connections

### 5. Utilities Layer (`utils/`)

**Purpose**: Cross-cutting concerns and helpers

**Responsibilities**:
- Logging configuration
- Permission checking
- Embed creation helpers
- Discord UI components

**Key Components**:
- `logger.py` - Structured logging
- `permissions.py` - Permission system
- `checks.py` - Discord command checks
- `embeds.py` - Embed helpers (legacy, being phased out)
- `views.py` - Discord UI components

## Data Flow

### Configuration Request Flow

```
User Command (Cog)
    ↓
ConfigService.get_guild_config()
    ↓
Cache Check
    ↓ (cache miss)
GuildConfigRepository.get_by_guild()
    ↓
Database Query
    ↓
GuildConfig Model
    ↓
Cache Update
    ↓
Return to Cog
```

### Embed Creation Flow

```
Cog needs embed
    ↓
BrandingService.create_embed()
    ↓
ConfigService.get_guild_config()
    ↓
Apply branding (color, footer, logo)
    ↓
Return discord.Embed
    ↓
Cog sends embed
```

### Configuration Update Flow

```
User changes configuration
    ↓
Cog validates input
    ↓
ConfigService.update_guild_config()
    ↓
Cache invalidation
    ↓
GuildConfigRepository.update()
    ↓
Database update
    ↓
Cache refresh
    ↓
Return success
```

### Session Management Flow

```
User Command (Session Cog)
    ↓
Permission Check
    ↓
SessionService.create_session()
    ↓
Check for existing active session
    ↓ (no active session)
Validate session channel
    ↓
SessionRepository.create()
    ↓
Cache active session
    ↓
Start background updater task
    ↓
Create and send session embed
    ↓
Update session with message/channel IDs
    ↓
Return success
```

### Session Update Flow

```
Background Task (60-second interval)
    ↓
SessionService._start_session_updater()
    ↓
Get active session from cache
    ↓
Calculate current duration
    ↓
Update duration in database
    ↓
Update cache
    ↓
Log update (embed update handled by cog)
    ↓
Sleep 60 seconds
```

### Event Flow

```
Action (SessionService)
    ↓
EventService.publish(event_name, data)
    ↓
Create Event object
    ↓
Get all listeners for event
    ↓
Execute each listener callback
    ↓
Continue regardless of listener errors
```

### Vote Flow

```
User Command (/session vote)
    ↓
Check active session exists
    ↓
Check user hasn't already voted
    ↓
SessionService.vote()
    ↓
Create SessionVote record
    ↓
Update session vote count
    ↓
Publish vote_added event
    ↓
Update session embed immediately
    ↓
Send ephemeral confirmation
```

### Dependency Injection Flow

```
Bot Startup
    ↓
ServiceContainer.initialize()
    ↓
Register all services
    ↓
Initialize singletons
    ↓
Services available via container
    ↓
Cogs receive services via injection
```

### Statistics Update Flow

```
Session Event (EventService)
    ↓
StatisticsService Event Listener
    ↓
Update database statistics
    ↓
Calculate aggregates (totals, averages)
    ↓
Persist changes
    ↓
Statistics available for queries
```

### Audit Logging Flow

```
Session Event (EventService)
    ↓
AuditService Event Listener
    ↓
Create audit log entry
    ↓
Store event metadata (JSON)
    ↓
Persist to database
    ↓
Audit trail complete
```

### Boost Flow

```
User Command (/session boost [note])
    ↓
Check active session exists
    ↓
SessionService.boost()
    ↓
Create SessionBoost record
    ↓
Update session boost count
    ↓
Publish boost_added event
    ↓
Update session embed immediately
    ↓
Send ephemeral confirmation
```

## Key Design Decisions

### 1. Unified Configuration Model

**Decision**: Merged branding into GuildConfig model
**Rationale**:
- Single source of truth reduces complexity
- Fewer database queries needed
- Simpler cache management
- Atomic updates to related settings

**Trade-offs**:
- Larger model size
- Mixed concerns in single model

### 2. Cache-Aside Pattern

**Decision**: 5-minute TTL cache for configuration
**Rationale**:
- Reduces database load significantly
- Configuration changes are infrequent
- Simple implementation
- Acceptable staleness for configuration data

**Trade-offs**:
- Slight delay in seeing changes
- Cache invalidation complexity
- Memory usage increases with guild count

### 3. Service-Based Business Logic

**Decision**: All business logic in services, not in cogs
**Rationale**:
- Testability (services can be tested without Discord)
- Reusability (services can be used in different contexts)
- Separation of concerns
- Easier to maintain

**Trade-offs**:
- More layers to navigate
- Slightly more boilerplate

### 4. Optional API Integration

**Decision**: API service auto-disables if no credentials
**Rationale**:
- Core functionality doesn't depend on external services
- Graceful degradation
- Easy deployment for different use cases
- No breaking changes if API is unavailable

**Trade-offs**:
- Some features silently disabled
- Configuration complexity

### 5. Repository Pattern

**Decision**: Abstract database access behind repositories
**Rationale**:
- No raw SQL in business logic
- Easier to change database implementation
- Testable with mock repositories
- Consistent data access patterns

**Trade-offs**:
- More boilerplate code
- Potential performance overhead

## Caching Strategy

### Configuration Cache

**Scope**: Guild-specific configuration
**TTL**: 5 minutes
**Invalidation**: On update operations
**Storage**: In-memory dictionary

```python
class ConfigService:
    def __init__(self) -> None:
        self._cache: dict[int, GuildConfig] = {}
        self._cache_timestamps: dict[int, datetime] = {}
        self._cache_ttl: int = 300  # 5 minutes
```

**Cache Operations**:
- **Read**: Check cache → if valid, return; else fetch from DB and cache
- **Write**: Invalidate cache → update DB → refresh cache
- **Invalidate**: Remove from cache and timestamps

## Permission System

### Hierarchy

```
Server Administrator (Discord permission)
    ↓
Configured Admin Role
    ↓
Configured Management Role
    ↓
Configured Host Role
    ↓
Configured Moderator Role
    ↓
Configured Member Role
    ↓
Everyone
```

### Implementation

```python
def _check_permissions(self, ctx: commands.Context) -> bool:
    # Server administrators always have access
    if ctx.author.guild_permissions.administrator:
        return True
    
    # Check configured admin role
    config = await self.config_service.get_guild_config(ctx.guild.id)
    if config and config.admin_role_id:
        return any(role.id == config.admin_role_id for role in ctx.author.roles)
    
    return False
```

## Error Handling Strategy

### Levels

1. **User Input Errors**: Clear messages with validation feedback
2. **Service Errors**: Logged with context, user-friendly error messages
3. **Database Errors**: Logged with details, generic error messages
4. **Critical Errors**: Logged extensively, alert sent if configured

### Example

```python
try:
    config = await self.config_service.set_community_name(guild_id, name)
    if not config:
        await ctx.send("Failed to update configuration.")
        return
    embed = await self.branding_service.success_embed(...)
    await ctx.send(embed=embed)
except Exception as e:
    logger.error(f"Error setting community name: {e}")
    embed = await self.branding_service.error_embed(...)
    await ctx.send(embed=embed)
```

## Migration System

### Strategy

- **Version-controlled**: Each migration has a version number
- **Forward and Backward**: Migrations support up and down operations
- **Tracking**: Schema migrations table tracks applied versions
- **Safe Operations**: Migrations designed to be safe to run multiple times

### Example

```python
def migration_002_merge_branding_to_guild_config(cursor: sqlite3.Cursor) -> None:
    # Add new columns
    cursor.execute("ALTER TABLE guild_config ADD COLUMN community_name TEXT")
    # Migrate data
    cursor.execute("UPDATE guild_config SET community_name = ...")
```

## Scalability Considerations

### Current Limitations

- **Single Process**: Designed for single bot instance
- **In-Memory Cache**: Not shared across instances
- **SQLite**: File-based database

### Scaling Paths

1. **Multiple Bot Instances**:
   - Use Redis for distributed caching
   - Use PostgreSQL for database
   - Implement proper locking

2. **High Traffic**:
   - Database connection pooling
   - Request rate limiting
   - Queue system for operations

3. **Large Guild Count**:
   - Cache size limits
   - Database connection limits
   - Memory optimization

## Security Considerations

### Data Protection

- **API Keys**: Stored in environment variables, never in code
- **Database**: File permissions restricted
- **Logging**: Sensitive data not logged

### Input Validation

- **URLs**: Validated before storage
- **Colors**: Hex format validation
- **IDs**: Type checking and existence verification
- **Length Limits**: String field length validation

### Permission Checks

- **Server Admins**: Always have access
- **Role-Based**: Configurable role requirements
- **Channel-Specific**: Checks for channel permissions

## Performance Optimization

### Database

- **Indexes**: On frequently queried columns
- **Connection Management**: Context managers for cleanup
- **Query Optimization**: Selective column retrieval

### Application

- **Caching**: Configuration caching reduces DB load
- **Async Operations**: Non-blocking I/O
- **Lazy Loading**: Services loaded on demand

### Monitoring Points

- **Cache Hit Rate**: Monitor cache effectiveness
- **Database Query Time**: Track slow queries
- **API Response Time**: External API performance
- **Command Execution Time**: Track slow commands

## Event System Architecture

### Overview

SessionCore includes a lightweight internal event system (EventService) that implements a publish/subscribe pattern for inter-service communication. This allows services to communicate without direct dependencies, enabling future features like statistics, logging, dashboards, and webhooks to subscribe to events without modifying core services.

### Design Principles

- **No Third-Party Dependencies**: Built with standard asyncio and typing only
- **Async-First**: All event operations are asynchronous
- **Error Isolation**: Listener errors don't crash the system
- **Priority Support**: Listeners can be prioritized for execution order
- **Zero-Dependency Listeners**: Bot continues functioning if no listeners exist

### Event Components

#### Event Object
```python
class Event:
    name: str  # Event name
    data: Dict[str, Any]  # Event payload
    timestamp: float  # Event creation time
```

#### EventListener Object
```python
class EventListener:
    event_name: str  # Event to listen for
    callback: Callable[[Event], None]  # Async callback
    priority: int  # Execution priority (higher first)
    id: int  # Unique listener ID
```

#### EventService
```python
class EventService:
    async def subscribe(event_name, callback, priority=0) -> EventListener
    async def unsubscribe(listener) -> bool
    async def publish(event_name, data) -> None
    async def publish_and_wait(event_name, data, timeout=5.0) -> None
    get_listener_count(event_name) -> int
    get_all_event_names() -> List[str]
```

### Available Events

#### session_started
Published when a new session is created and started.

**Payload:**
```python
{
    "session_id": int,
    "guild_id": int,
    "host_id": int,
    "server_code": str
}
```

**Use Cases:**
- Initialize session statistics
- Send notifications to external systems
- Start session-specific timers
- Log session start to audit log

#### session_ended
Published when a session is ended.

**Payload:**
```python
{
    "session_id": int,
    "guild_id": int,
    "host_id": int,
    "duration": int  # Duration in seconds
}
```

**Use Cases:**
- Calculate final statistics
- Archive session data
- Send completion notifications
- Update leaderboards
- Trigger achievement checks

#### vote_added
Published when a user votes for a session.

**Payload:**
```python
{
    "session_id": int,
    "guild_id": int,
    "user_id": int,
    "vote_count": int
}
```

**Use Cases:**
- Update live statistics
- Send vote notifications
- Track engagement metrics
- Trigger vote-based achievements

#### boost_added
Published when a user boosts a session.

**Payload:**
```python
{
    "session_id": int,
    "guild_id": int,
    "user_id": int,
    "note": Optional[str],
    "boost_count": int
}
```

**Use Cases:**
- Update live statistics
- Send boost notifications
- Track engagement metrics
- Trigger boost-based achievements

### Event Subscription Example

```python
from services import event_service, EVENT_VOTE_ADDED

async def on_vote_added(event: Event) -> None:
    """Handle vote added event."""
    session_id = event.data["session_id"]
    user_id = event.data["user_id"]
    # Process vote...
    pass

# Subscribe to event
listener = await event_service.subscribe(
    EVENT_VOTE_ADDED,
    on_vote_added,
    priority=10
)

# Unsubscribe when done
await event_service.unsubscribe(listener)
```

### Event Publishing Example

```python
from services import event_service, EVENT_VOTE_ADDED

await event_service.publish(EVENT_VOTE_ADDED, {
    "session_id": 123,
    "guild_id": 456,
    "user_id": 789,
    "vote_count": 5
})
```

### Best Practices

1. **Don't Block**: Keep listener callbacks fast and non-blocking
2. **Error Handling**: Always wrap listener code in try/except
3. **Priority Use**: Use priority for execution order (e.g., validation before processing)
4. **Clean Up**: Always unsubscribe listeners when they're no longer needed
5. **Data Validation**: Validate event data in listeners before processing
6. **Logging**: Log event processing for debugging

### Future Event Extensions

The event system is designed for easy extension. Future events might include:

- `participant_joined` - When a user joins a session
- `participant_left` - When a user leaves a session
- `session_cancelled` - When a session is cancelled
- `achievement_unlocked` - When a user earns an achievement
- `statistics_updated` - When session statistics change
- `api_sync_complete` - When API sync operations complete

### Error Handling

- Listener errors are logged but don't stop event propagation
- If a listener fails, other listeners still execute
- Listeners should handle their own errors gracefully
- EventService logs errors for debugging

### Performance Considerations

- Events are lightweight and fast
- Listeners execute in sequence (not parallel)
- Consider using `publish_and_wait` for critical events
- Use priority for time-sensitive listeners
- Avoid heavy processing in listeners

### Unit Tests

- **Services**: Test business logic with mock repositories
- **Repositories**: Test data access with test database
- **Utilities**: Test helper functions

### Integration Tests

- **Cogs**: Test command execution with test bot
- **Services**: Test with real database
- **Migrations**: Test schema changes

### Manual Testing

- **Guild Join**: Test auto-configuration
- **Configuration**: Test configuration changes
- **Branding**: Test embed appearance
- **Permissions**: Test access control

## Future Architecture Evolution

### Planned Improvements

1. **Event System**: More sophisticated event handling
2. **Task Queue**: Background task processing
3. **Webhooks**: External notification system
4. **Analytics**: Usage tracking and metrics
5. **Plugin System**: Extensible architecture for plugins

### Technical Debt

1. **Remove Legacy Code**: Phase out old branding model
2. **Standardize Error Handling**: Consistent error patterns
3. **Improve Type Coverage**: 100% type hint coverage
4. **Add Documentation**: API documentation for services

## Development Guidelines

### Adding New Features

1. **Define Model**: Add/update data model in `models.py`
2. **Create Migration**: Add migration in `migrations.py`
3. **Create Repository**: Add repository in `database.py`
4. **Create Service**: Add service in `services/`
5. **Create Commands**: Add commands in appropriate cog
6. **Update Cogs**: Register new commands
7. **Test**: Manual and automated testing
8. **Document**: Update documentation

### Code Review Checklist

- [ ] Type hints present
- [ ] Async/await used correctly
- [ ] Error handling implemented
- [ ] Logging added
- [ ] No global state
- [ ] Follows existing patterns
- [ ] No hardcoded values
- [ ] Permissions checked
- [ ] Input validated
- [ ] Documentation updated

## Conclusion

The SessionCore architecture provides a solid foundation for a scalable, maintainable Discord bot framework. The layered approach ensures clear separation of concerns, while the service-based design makes the system testable and extensible. The caching strategy and repository pattern balance performance with code quality, and the permission system provides flexible access control.

Future evolution should focus on scalability improvements, testing infrastructure, and enhanced monitoring while maintaining the core architectural principles.
