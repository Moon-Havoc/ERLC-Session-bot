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
    
    return runner
