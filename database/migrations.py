"""Database migration system for SessionCore."""

import sqlite3
import asyncio
from typing import Optional, List, Callable
from datetime import datetime
from pathlib import Path

from config import config
from .database import Database


class Migration:
    """Represents a database migration."""
    
    def __init__(self, version: int, name: str, up: Callable, down: Optional[Callable] = None) -> None:
        self.version = version
        self.name = name
        self.up = up
        self.down = down


class MigrationRunner:
    """Manages database migrations."""
    
    def __init__(self, db: Database) -> None:
        self.db = db
        self.migrations: List[Migration] = []
    
    def register(self, migration: Migration) -> None:
        """Register a migration."""
        self.migrations.append(migration)
    
    async def initialize_schema(self) -> None:
        """Initialize the migration tracking table."""
        query = """
            CREATE TABLE IF NOT EXISTS schema_migrations (
                version INTEGER PRIMARY KEY,
                name TEXT NOT NULL,
                applied_at TEXT NOT NULL
            )
        """
        await self.db.execute(query)
    
    async def get_applied_migrations(self) -> List[int]:
        """Get list of applied migration versions."""
        query = "SELECT version FROM schema_migrations ORDER BY version"
        rows = await self.db.fetchall(query)
        return [row[0] for row in rows]
    
    async def apply_migration(self, migration: Migration) -> None:
        """Apply a single migration."""
        async with self.db.get_connection() as conn:
            cursor = conn.cursor()
            
            # Execute migration
            await migration.up(cursor)
            
            # Record migration
            query = """
                INSERT INTO schema_migrations (version, name, applied_at)
                VALUES (?, ?, ?)
            """
            cursor.execute(query, (migration.version, migration.name, datetime.utcnow().isoformat()))
            conn.commit()
    
    async def rollback_migration(self, migration: Migration) -> None:
        """Rollback a single migration."""
        if migration.down is None:
            raise ValueError(f"Migration {migration.version} cannot be rolled back")
        
        async with self.db.get_connection() as conn:
            cursor = conn.cursor()
            
            # Execute rollback
            await migration.down(cursor)
            
            # Remove migration record
            query = "DELETE FROM schema_migrations WHERE version = ?"
            cursor.execute(query, (migration.version,))
            conn.commit()
    
    async def migrate(self, target_version: Optional[int] = None) -> None:
        """Run migrations to bring database to target version."""
        await self.initialize_schema()
        applied = await self.get_applied_migrations()
        
        if target_version is None:
            # Migrate to latest
            for migration in self.migrations:
                if migration.version not in applied:
                    await self.apply_migration(migration)
        else:
            # Migrate to specific version
            for migration in self.migrations:
                if migration.version <= target_version and migration.version not in applied:
                    await self.apply_migration(migration)
                elif migration.version > target_version and migration.version in applied:
                    await self.rollback_migration(migration)
    
    async def rollback(self, steps: int = 1) -> None:
        """Rollback specified number of migrations."""
        await self.initialize_schema()
        applied = await self.get_applied_migrations()
        
        if not applied:
            return
        
        # Get the last N applied migrations
        to_rollback = sorted(applied, reverse=True)[:steps]
        
        for version in to_rollback:
            migration = next((m for m in self.migrations if m.version == version), None)
            if migration and migration.down:
                await self.rollback_migration(migration)


# Migration functions
def migration_001_create_tables(cursor: sqlite3.Cursor) -> None:
    """Create initial database schema."""
    
    # Guild configuration table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS guild_config (
            guild_id INTEGER PRIMARY KEY,
            admin_role_id INTEGER,
            moderator_role_id INTEGER,
            host_role_id INTEGER,
            member_role_id INTEGER,
            log_channel_id INTEGER,
            session_channel_id INTEGER,
            welcome_channel_id INTEGER,
            auto_role_enabled BOOLEAN DEFAULT 0,
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL
        )
    """)
    
    # Branding table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS branding (
            guild_id INTEGER PRIMARY KEY,
            community_name TEXT NOT NULL,
            description TEXT,
            logo_url TEXT,
            embed_color INTEGER DEFAULT 5865F2,
            footer_text TEXT,
            footer_icon_url TEXT,
            custom_emoji TEXT,
            website_url TEXT,
            invite_link TEXT,
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL
        )
    """)
    
    # Sessions table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS sessions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            guild_id INTEGER NOT NULL,
            host_id INTEGER NOT NULL,
            session_type TEXT NOT NULL,
            title TEXT NOT NULL,
            description TEXT,
            scheduled_time TEXT,
            start_time TEXT,
            end_time TEXT,
            status TEXT NOT NULL DEFAULT 'active',
            max_participants INTEGER,
            current_participants INTEGER DEFAULT 0,
            message_id INTEGER,
            channel_id INTEGER,
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL,
            FOREIGN KEY (guild_id) REFERENCES guild_config(guild_id)
        )
    """)
    
    # Session participants table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS session_participants (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            session_id INTEGER NOT NULL,
            user_id INTEGER NOT NULL,
            joined_at TEXT NOT NULL,
            left_at TEXT,
            attendance_minutes INTEGER DEFAULT 0,
            FOREIGN KEY (session_id) REFERENCES sessions(id) ON DELETE CASCADE
        )
    """)
    
    # Session statistics table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS session_stats (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            session_id INTEGER NOT NULL,
            user_id INTEGER NOT NULL,
            metric_name TEXT NOT NULL,
            metric_value REAL NOT NULL,
            recorded_at TEXT NOT NULL,
            FOREIGN KEY (session_id) REFERENCES sessions(id) ON DELETE CASCADE
        )
    """)
    
    # Votes table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS votes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            guild_id INTEGER NOT NULL,
            user_id INTEGER NOT NULL,
            target_id INTEGER NOT NULL,
            vote_type TEXT NOT NULL,
            value INTEGER NOT NULL,
            created_at TEXT NOT NULL,
            UNIQUE(guild_id, user_id, target_id, vote_type)
        )
    """)
    
    # Boosts table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS boosts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            guild_id INTEGER NOT NULL,
            user_id INTEGER NOT NULL,
            boost_count INTEGER DEFAULT 0,
            total_boosts INTEGER DEFAULT 0,
            last_boost_at TEXT,
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL,
            UNIQUE(guild_id, user_id)
        )
    """)
    
    # Hosts table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS hosts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            guild_id INTEGER NOT NULL,
            user_id INTEGER NOT NULL,
            total_sessions_hosted INTEGER DEFAULT 0,
            total_participants INTEGER DEFAULT 0,
            average_rating REAL DEFAULT 0.0,
            total_rating_count INTEGER DEFAULT 0,
            is_active BOOLEAN DEFAULT 1,
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL,
            UNIQUE(guild_id, user_id)
        )
    """)
    
    # Create indexes for better performance
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_sessions_guild ON sessions(guild_id)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_sessions_status ON sessions(status)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_sessions_host ON sessions(host_id)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_participants_session ON session_participants(session_id)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_participants_user ON session_participants(user_id)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_stats_session ON session_stats(session_id)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_stats_user ON session_stats(user_id)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_votes_target ON votes(target_id, vote_type)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_boosts_guild_user ON boosts(guild_id, user_id)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_hosts_guild_user ON hosts(guild_id, user_id)")


def migration_001_rollback(cursor: sqlite3.Cursor) -> None:
    """Rollback initial database schema."""
    
    # Drop tables in reverse order due to foreign keys
    cursor.execute("DROP INDEX IF EXISTS idx_hosts_guild_user")
    cursor.execute("DROP INDEX IF EXISTS idx_boosts_guild_user")
    cursor.execute("DROP INDEX IF EXISTS idx_votes_target")
    cursor.execute("DROP INDEX IF EXISTS idx_stats_user")
    cursor.execute("DROP INDEX IF EXISTS idx_stats_session")
    cursor.execute("DROP INDEX IF EXISTS idx_participants_user")
    cursor.execute("DROP INDEX IF EXISTS idx_participants_session")
    cursor.execute("DROP INDEX IF EXISTS idx_sessions_host")
    cursor.execute("DROP INDEX IF EXISTS idx_sessions_status")
    cursor.execute("DROP INDEX IF EXISTS idx_sessions_guild")
    
    cursor.execute("DROP TABLE IF EXISTS hosts")
    cursor.execute("DROP TABLE IF EXISTS boosts")
    cursor.execute("DROP TABLE IF EXISTS votes")
    cursor.execute("DROP TABLE IF EXISTS session_stats")
    cursor.execute("DROP TABLE IF EXISTS session_participants")
    cursor.execute("DROP TABLE IF EXISTS sessions")
    cursor.execute("DROP TABLE IF EXISTS branding")
    cursor.execute("DROP TABLE IF EXISTS guild_config")


def migration_002_merge_branding_to_guild_config(cursor: sqlite3.Cursor) -> None:
    """Merge branding fields into guild_config table."""
    
    # Add branding columns to guild_config
    cursor.execute("""
        ALTER TABLE guild_config ADD COLUMN community_name TEXT DEFAULT 'Community'
    """)
    cursor.execute("""
        ALTER TABLE guild_config ADD COLUMN community_description TEXT
    """)
    cursor.execute("""
        ALTER TABLE guild_config ADD COLUMN logo_url TEXT
    """)
    cursor.execute("""
        ALTER TABLE guild_config ADD COLUMN embed_color INTEGER DEFAULT 5865F2
    """)
    cursor.execute("""
        ALTER TABLE guild_config ADD COLUMN footer_text TEXT
    """)
    cursor.execute("""
        ALTER TABLE guild_config ADD COLUMN footer_icon_url TEXT
    """)
    cursor.execute("""
        ALTER TABLE guild_config ADD COLUMN community_emoji TEXT
    """)
    cursor.execute("""
        ALTER TABLE guild_config ADD COLUMN website_url TEXT
    """)
    cursor.execute("""
        ALTER TABLE guild_config ADD COLUMN discord_invite TEXT
    """)
    
    # Add management role
    cursor.execute("""
        ALTER TABLE guild_config ADD COLUMN management_role_id INTEGER
    """)
    
    # Rename log_channel_id to logs_channel_id for consistency
    cursor.execute("""
        ALTER TABLE guild_config ADD COLUMN logs_channel_id INTEGER
    """)
    
    # Add timezone and API settings
    cursor.execute("""
        ALTER TABLE guild_config ADD COLUMN timezone TEXT DEFAULT 'UTC'
    """)
    cursor.execute("""
        ALTER TABLE guild_config ADD COLUMN api_enabled BOOLEAN DEFAULT 0
    """)
    cursor.execute("""
        ALTER TABLE guild_config ADD COLUMN api_url TEXT
    """)
    cursor.execute("""
        ALTER TABLE guild_config ADD COLUMN api_key TEXT
    """)
    
    # Migrate existing branding data to guild_config
    cursor.execute("""
        UPDATE guild_config 
        SET community_name = (SELECT community_name FROM branding WHERE branding.guild_id = guild_config.guild_id),
            community_description = (SELECT description FROM branding WHERE branding.guild_id = guild_config.guild_id),
            logo_url = (SELECT logo_url FROM branding WHERE branding.guild_id = guild_config.guild_id),
            embed_color = (SELECT embed_color FROM branding WHERE branding.guild_id = guild_config.guild_id),
            footer_text = (SELECT footer_text FROM branding WHERE branding.guild_id = guild_config.guild_id),
            footer_icon_url = (SELECT footer_icon_url FROM branding WHERE branding.guild_id = guild_config.guild_id),
            community_emoji = (SELECT custom_emoji FROM branding WHERE branding.guild_id = guild_config.guild_id),
            website_url = (SELECT website_url FROM branding WHERE branding.guild_id = guild_config.guild_id),
            discord_invite = (SELECT invite_link FROM branding WHERE branding.guild_id = guild_config.guild_id)
        WHERE EXISTS (SELECT 1 FROM branding WHERE branding.guild_id = guild_config.guild_id)
    """)
    
    # Set default community name for guilds without branding
    cursor.execute("""
        UPDATE guild_config SET community_name = 'Community' WHERE community_name IS NULL
    """)


def migration_002_rollback(cursor: sqlite3.Cursor) -> None:
    """Rollback migration 002 - cannot be fully rolled back due to ALTER TABLE limitations."""
    
    # SQLite doesn't support dropping columns, so we need to recreate the table
    cursor.execute("""
        CREATE TABLE guild_config_backup (
            guild_id INTEGER PRIMARY KEY,
            admin_role_id INTEGER,
            moderator_role_id INTEGER,
            host_role_id INTEGER,
            member_role_id INTEGER,
            log_channel_id INTEGER,
            session_channel_id INTEGER,
            welcome_channel_id INTEGER,
            auto_role_enabled BOOLEAN DEFAULT 0,
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL
        )
    """)
    
    cursor.execute("""
        INSERT INTO guild_config_backup 
        SELECT guild_id, admin_role_id, moderator_role_id, host_role_id, member_role_id,
               log_channel_id, session_channel_id, welcome_channel_id, auto_role_enabled,
               created_at, updated_at
        FROM guild_config
    """)
    
    cursor.execute("DROP TABLE guild_config")
    cursor.execute("ALTER TABLE guild_config_backup RENAME TO guild_config")


def migration_003_update_session_schema(cursor: sqlite3.Cursor) -> None:
    """Update session schema for session management core."""
    
    # Create new sessions table with updated schema
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS sessions_new (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            guild_id INTEGER NOT NULL,
            host_id INTEGER NOT NULL,
            server_code TEXT NOT NULL,
            notes TEXT,
            started_at TEXT,
            ended_at TEXT,
            status TEXT NOT NULL DEFAULT 'active',
            session_channel_id INTEGER,
            session_message_id INTEGER,
            vote_count INTEGER DEFAULT 0,
            boost_count INTEGER DEFAULT 0,
            duration INTEGER,
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL,
            FOREIGN KEY (guild_id) REFERENCES guild_config(guild_id)
        )
    """)
    
    # Migrate existing sessions if any
    cursor.execute("""
        INSERT INTO sessions_new 
        SELECT id, guild_id, host_id, 
               COALESCE(title, '') as server_code,
               description as notes,
               start_time as started_at,
               end_time as ended_at,
               CASE 
                   WHEN status = 'completed' THEN 'ended'
                   ELSE status
               END as status,
               channel_id as session_channel_id,
               message_id as session_message_id,
               0 as vote_count,
               0 as boost_count,
               NULL as duration,
               created_at, updated_at
        FROM sessions
    """)
    
    # Drop old table and rename new one
    cursor.execute("DROP TABLE sessions")
    cursor.execute("ALTER TABLE sessions_new RENAME TO sessions")
    
    # Recreate indexes
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_sessions_guild ON sessions(guild_id)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_sessions_status ON sessions(status)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_sessions_host ON sessions(host_id)")


def migration_004_add_vote_boost_tables(cursor: sqlite3.Cursor) -> None:
    """Add vote and boost tables for session engagement."""
    
    # Session votes table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS session_votes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            guild_id INTEGER NOT NULL,
            session_id INTEGER NOT NULL,
            user_id INTEGER NOT NULL,
            created_at TEXT NOT NULL,
            UNIQUE(guild_id, session_id, user_id),
            FOREIGN KEY (session_id) REFERENCES sessions(id) ON DELETE CASCADE
        )
    """)
    
    # Session boosts table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS session_boosts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            guild_id INTEGER NOT NULL,
            session_id INTEGER NOT NULL,
            user_id INTEGER NOT NULL,
            note TEXT,
            created_at TEXT NOT NULL,
            FOREIGN KEY (session_id) REFERENCES sessions(id) ON DELETE CASCADE
        )
    """)
    
    # Create indexes
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_votes_session ON session_votes(session_id)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_votes_user ON session_votes(user_id)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_boosts_session ON session_boosts(session_id)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_boosts_user ON session_boosts(user_id)")


def migration_004_rollback(cursor: sqlite3.Cursor) -> None:
    """Rollback migration 004 - remove vote and boost tables."""
    
    # Drop indexes
    cursor.execute("DROP INDEX IF EXISTS idx_boosts_user")
    cursor.execute("DROP INDEX IF NOT EXISTS idx_boosts_session")
    cursor.execute("DROP INDEX IF NOT EXISTS idx_votes_user")
    cursor.execute("DROP INDEX IF NOT EXISTS idx_votes_session")
    
    # Drop tables
    cursor.execute("DROP TABLE IF EXISTS session_boosts")
    cursor.execute("DROP TABLE IF EXISTS session_votes")


def migration_003_rollback(cursor: sqlite3.Cursor) -> None:
    """Rollback migration 003 - restore old session schema."""
    
    # Create old sessions table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS sessions_old (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            guild_id INTEGER NOT NULL,
            host_id INTEGER NOT NULL,
            session_type TEXT NOT NULL,
            title TEXT NOT NULL,
            description TEXT,
            scheduled_time TEXT,
            start_time TEXT,
            end_time TEXT,
            status TEXT NOT NULL DEFAULT 'active',
            max_participants INTEGER,
            current_participants INTEGER DEFAULT 0,
            message_id INTEGER,
            channel_id INTEGER,
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL,
            FOREIGN KEY (guild_id) REFERENCES guild_config(guild_id)
        )
    """)
    
    # Migrate data back
    cursor.execute("""
        INSERT INTO sessions_old
        SELECT id, guild_id, host_id,
               'training' as session_type,
               server_code as title,
               notes as description,
               NULL as scheduled_time,
               started_at as start_time,
               ended_at as end_time,
               CASE 
                   WHEN status = 'ended' THEN 'completed'
                   ELSE status
               END as status,
               NULL as max_participants,
               0 as current_participants,
               session_message_id as message_id,
               session_channel_id as channel_id,
               created_at, updated_at
        FROM sessions
    """)
    
    # Drop new table and restore old one
    cursor.execute("DROP TABLE sessions")
    cursor.execute("ALTER TABLE sessions_old RENAME TO sessions")
    
    # Recreate indexes
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_sessions_guild ON sessions(guild_id)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_sessions_status ON sessions(status)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_sessions_host ON sessions(host_id)")


# Register migrations
def get_migration_runner(db: Database) -> MigrationRunner:
    """Get configured migration runner."""
    runner = MigrationRunner(db)
    
    # Register migrations in order
    runner.register(Migration(
        version=1,
        name="create_initial_tables",
        up=migration_001_create_tables,
        down=migration_001_rollback
    ))
    
    runner.register(Migration(
        version=2,
        name="merge_branding_to_guild_config",
        up=migration_002_merge_branding_to_guild_config,
        down=migration_002_rollback
    ))
    
    runner.register(Migration(
        version=3,
        name="update_session_schema",
        up=migration_003_update_session_schema,
        down=migration_003_rollback
    ))
    
    runner.register(Migration(
        version=4,
        name="add_vote_boost_tables",
        up=migration_004_add_vote_boost_tables,
        down=migration_004_rollback
    ))
    
    return runner
