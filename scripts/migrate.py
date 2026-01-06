#!/usr/bin/env python3
"""
Smart Database Migration Script
===============================

A production-ready migration script with async support, smart change detection,
and multi-schema architecture support using Alembic.

Features
--------
- **Smart Detection**: Only creates migrations if model changes are detected
- **Pending Check**: Only upgrades if there are pending migrations
- **Multi-Schema**: Works with MODULE_BASES architecture (user_schema, file_schema, etc.)
- **Force Mode**: Override smart checks when needed
- **Dry-Run**: Check status without making changes

Commands
--------

1. UPGRADE (default - apply pending migrations):
   ```bash
   python scripts/migrate.py                    # Smart upgrade (skip if up-to-date)
   python scripts/migrate.py --upgrade          # Explicit upgrade
   python scripts/migrate.py --upgrade --force  # Force upgrade even if up-to-date
   ```

2. CREATE (generate new migration from model changes):
   ```bash
   python scripts/migrate.py --create "add_user_avatar"     # Smart create (skip if no changes)
   python scripts/migrate.py --create "init" --force        # Force create migration
   ```

3. CHECK (status without changes):
   ```bash
   python scripts/migrate.py --check            # Show pending migrations & model changes
   ```

4. DOWNGRADE (rollback migrations):
   ```bash
   python scripts/migrate.py --downgrade -1     # Rollback 1 migration
   python scripts/migrate.py --downgrade base   # Rollback all migrations
   python scripts/migrate.py --downgrade abc123 # Rollback to specific revision
   ```

5. INFO (show migration info):
   ```bash
   python scripts/migrate.py --current          # Show current revision
   python scripts/migrate.py --history          # Show migration history
   ```

Examples
--------
# Initial setup (first time)
python scripts/migrate.py --create "init" --force
python scripts/migrate.py --upgrade

# After modifying models
python scripts/migrate.py --check               # See what changed
python scripts/migrate.py --create "add_email_verified_field"
python scripts/migrate.py --upgrade

# Reset database (development only!)
python scripts/migrate.py --downgrade base
python scripts/migrate.py --upgrade

Exit Codes
----------
- 0: Success
- 1: Error (connection failed, migration failed, etc.)

Notes
-----
- Always run migrations before seeding: `python scripts/seed.py`
- Migration files are stored in `alembic/versions/`
- Configuration is in `alembic.ini`
"""
import sys
import os
import asyncio
from pathlib import Path

# Ensure we're in the right directory and add to path
project_root = Path(__file__).resolve().parent.parent
os.chdir(project_root)
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(project_root / "src"))

import logging
from sqlalchemy import text

# Import from YOUR project
from infrastructure.database.orm.adapters.sqlalchemy.shared.datasource import DataSource
from infrastructure.database.orm.adapters.sqlalchemy.shared.base_model import MODULE_BASES

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Color codes for terminal output
class Colors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'


async def verify_database_connection() -> bool:
    """Verify database connection before migration"""
    logger.info("Step 1: Verifying database connection...")
    
    db = DataSource()
    try:
        db.initialize()
        
        async with db.engine.begin() as conn:
            result = await conn.execute(text("SELECT version()"))
            version = result.scalar()
            logger.info(f"  ✓ Connected to PostgreSQL")
            logger.info(f"  Version: {version}")
            return True
    except Exception as e:
        logger.error(f"  ✗ Database connection failed: {e}")
        logger.error("\n  Troubleshooting:")
        logger.error("  - Is PostgreSQL running? → docker-compose ps")
        logger.error("  - Check DATABASE_URL in .env")
        logger.error("  - Try: docker-compose up -d")
        return False
    finally:
        if db.is_initialized:
            await db.close()


async def verify_schemas_exist() -> bool:
    """Ensure all required schemas exist"""
    logger.info("\nStep 2: Verifying schemas exist...")
    
    db = DataSource()
    try:
        db.initialize()
        
        async with db.engine.begin() as conn:
            # Get schemas from MODULE_BASES
            for module_name, module_base in MODULE_BASES.items():
                schema_name = module_base.schema_name
                
                result = await conn.execute(text(f"""
                    SELECT schema_name 
                    FROM information_schema.schemata 
                    WHERE schema_name = '{schema_name}'
                """))
                exists = result.fetchone()
                
                if not exists:
                    logger.warning(f"  ⚠ Schema '{schema_name}' not found, creating...")
                    await conn.execute(text(f"CREATE SCHEMA {schema_name}"))
                    logger.info(f"  ✓ Created schema '{schema_name}'")
                else:
                    logger.info(f"  ✓ Schema '{schema_name}' exists")
        
        return True
    except Exception as e:
        logger.error(f"  ✗ Schema verification failed: {e}")
        return False
    finally:
        if db.is_initialized:
            await db.close()


def verify_models_loaded() -> bool:
    """Verify all models are loaded"""
    logger.info("\nStep 3: Verifying models are loaded...")

    try:
        # Import all models - using new project structure
        from infrastructure.database.orm.adapters.sqlalchemy.contexts.user_management.models import (
            UserModel,
            UserProfileModel,
        )
        logger.info("  ✓ User management models loaded")

        from infrastructure.database.orm.adapters.sqlalchemy.contexts.file_management.models import (
            FileModel,
        )
        logger.info("  ✓ File management models loaded")

        # Import outbox model (shared Base) - import registers it in metadata
        from infrastructure.database.orm.adapters.sqlalchemy.shared.outbox import (
            OutboxEventModel,  # noqa: F401
        )
        logger.info("  ✓ Outbox models loaded")

        # Add more contexts as you create them:
        # from infrastructure.database.orm.adapters.sqlalchemy.contexts.order_management.models import OrderModel
        # logger.info("  ✓ Order management models loaded")

        return True
    except ImportError as e:
        logger.error(f"  ✗ Failed to import models: {e}")
        logger.error("\n  Troubleshooting:")
        logger.error("  - Check that model files exist")
        logger.error("  - Verify import paths in this script")
        logger.error("  - Make sure models call register_module_base()")
        return False


def verify_metadata() -> bool:
    """Verify metadata is properly configured"""
    logger.info("\nStep 4: Verifying metadata...")
    
    try:
        if not MODULE_BASES:
            logger.error("  ✗ No contexts registered in MODULE_BASES")
            logger.error("  Make sure your models.py files call register_module_base()")
            return False
        
        from sqlalchemy import MetaData
        
        target_metadata = MetaData()
        total_tables = 0
        
        for module_name, module_base in MODULE_BASES.items():
            tables = list(module_base.Base.metadata.tables.keys())
            total_tables += len(tables)
            logger.info(f"  ✓ {module_name} ({module_base.schema_name}): {len(tables)} tables")
            
            # Show table names
            if tables:
                logger.info(f"    Tables: {', '.join(tables)}")
            
            # Copy to combined metadata
            for table in module_base.Base.metadata.tables.values():
                table.to_metadata(target_metadata)
        
        logger.info(f"  ✓ Total: {total_tables} tables in metadata")
        
        if total_tables == 0:
            logger.warning("  ⚠ No tables found in metadata")
            logger.warning("  Make sure your models inherit from module_base.BaseModel")
        
        return total_tables > 0
        
    except Exception as e:
        logger.error(f"  ✗ Metadata error: {e}")
        import traceback
        traceback.print_exc()
        return False


async def cleanup_after_downgrade(target_revision: str) -> bool:
    """
    Clean up PostgreSQL artifacts after downgrade.

    When downgrading (especially to 'base'), PostgreSQL enum types
    are not automatically dropped with the tables. This function
    cleans up orphaned enum types.

    Args:
        target_revision: The revision we downgraded to ('base', '-1', or specific revision)

    Returns:
        True if cleanup succeeded, False otherwise
    """
    logger.info("\nStep 6: Cleaning up PostgreSQL artifacts...")

    db = DataSource()
    try:
        db.initialize()

        async with db.engine.begin() as conn:
            # Get all custom enum types in public schema
            result = await conn.execute(text("""
                SELECT t.typname as enum_name
                FROM pg_type t
                JOIN pg_catalog.pg_namespace n ON n.oid = t.typnamespace
                WHERE t.typtype = 'e'
                AND n.nspname = 'public'
            """))
            enum_types = [row[0] for row in result.fetchall()]

            if enum_types:
                logger.info(f"  Found {len(enum_types)} enum type(s) to clean up")
                for enum_name in enum_types:
                    try:
                        await conn.execute(text(f"DROP TYPE IF EXISTS {enum_name} CASCADE"))
                        logger.info(f"  ✓ Dropped enum type: {enum_name}")
                    except Exception as e:
                        logger.warning(f"  ⚠ Could not drop enum {enum_name}: {e}")
            else:
                logger.info("  ✓ No orphaned enum types found")

        return True

    except Exception as e:
        logger.error(f"  ✗ Cleanup failed: {e}")
        return False
    finally:
        if db.is_initialized:
            await db.close()


def check_pending_migrations() -> tuple[bool, list[str]]:
    """
    Check if there are pending migrations to apply.

    Returns:
        tuple: (has_pending, list of pending revision ids)
    """
    try:
        from alembic.config import Config
        from alembic.script import ScriptDirectory
        from alembic.runtime.migration import MigrationContext
        from sqlalchemy import create_engine
        from shared.bootstrap import create_config_service

        config_service = create_config_service()
        url = config_service.database.DATABASE_URL.replace('postgresql+asyncpg://', 'postgresql://')

        alembic_cfg = Config("alembic.ini")
        script = ScriptDirectory.from_config(alembic_cfg)

        engine = create_engine(url)
        with engine.connect() as conn:
            context = MigrationContext.configure(conn)
            current_rev = context.get_current_revision()
            head_rev = script.get_current_head()

            if current_rev == head_rev:
                return False, []

            # Get list of pending revisions
            pending = []
            for rev in script.iterate_revisions(head_rev, current_rev):
                if rev.revision != current_rev:
                    pending.append(rev.revision)

            return len(pending) > 0, pending

    except Exception as e:
        logger.warning(f"Could not check pending migrations: {e}")
        return True, []  # Assume there are pending migrations on error


def check_model_changes() -> tuple[bool, list[str]]:
    """
    Check if there are model changes that need a new migration.
    Uses Alembic's autogenerate compare to detect changes.

    Returns:
        tuple: (has_changes, list of change descriptions)
    """
    try:
        from alembic.config import Config
        from alembic.script import ScriptDirectory
        from alembic.runtime.migration import MigrationContext
        from alembic.autogenerate import compare_metadata
        from sqlalchemy import create_engine, MetaData
        from shared.bootstrap import create_config_service

        config_service = create_config_service()
        url = config_service.database.DATABASE_URL.replace('postgresql+asyncpg://', 'postgresql://')

        # Get target metadata from MODULE_BASES
        target_metadata = MetaData()
        for module_name, module_base in MODULE_BASES.items():
            for table in module_base.Base.metadata.tables.values():
                table.to_metadata(target_metadata)

        # Also include shared Base tables
        from infrastructure.database.orm.adapters.sqlalchemy.shared.base_model import Base as SharedBase
        for table in SharedBase.metadata.tables.values():
            if table.name not in target_metadata.tables:
                table.to_metadata(target_metadata)

        engine = create_engine(url)
        with engine.connect() as conn:
            context = MigrationContext.configure(
                conn,
                opts={
                    "include_schemas": True,
                    "compare_type": True,
                    "compare_server_default": True,
                }
            )
            diff = compare_metadata(context, target_metadata)

            if not diff:
                return False, []

            # Format changes for display
            changes = []
            for change in diff:
                change_type = change[0]
                if change_type == 'add_table':
                    changes.append(f"Add table: {change[1].name}")
                elif change_type == 'remove_table':
                    changes.append(f"Remove table: {change[1].name}")
                elif change_type == 'add_column':
                    changes.append(f"Add column: {change[3].name} to {change[2]}")
                elif change_type == 'remove_column':
                    changes.append(f"Remove column: {change[3].name} from {change[2]}")
                elif change_type == 'add_index':
                    changes.append(f"Add index: {change[1].name}")
                elif change_type == 'remove_index':
                    changes.append(f"Remove index: {change[1].name}")
                else:
                    changes.append(f"{change_type}: {change[1:]}")

            return True, changes

    except Exception as e:
        logger.warning(f"Could not check model changes: {e}")
        return True, []  # Assume there are changes on error


def run_alembic_command(args) -> tuple[bool, str | None]:
    """
    Run Alembic command.

    Returns:
        tuple: (success, downgrade_target or None)
            - success: True if command succeeded
            - downgrade_target: The revision we downgraded to (for cleanup), or None
    """
    logger.info("\nStep 5: Running Alembic migration...")
    logger.info("=" * 60)

    try:
        from alembic.config import Config
        from alembic import command

        # Create Alembic config
        alembic_cfg = Config("alembic.ini")

        # Note: Alembic uses ASYNC operations via env.py

        if args.create:
            # Check if there are actual model changes before creating migration
            if not args.force:
                has_changes, changes = check_model_changes()
                if not has_changes:
                    logger.info(f"{Colors.OKGREEN}✓ No model changes detected, skipping migration creation{Colors.ENDC}")
                    logger.info("  Use --force to create migration anyway")
                    return True, None

                logger.info("Detected model changes:")
                for change in changes[:10]:  # Show first 10 changes
                    logger.info(f"  - {change}")
                if len(changes) > 10:
                    logger.info(f"  ... and {len(changes) - 10} more")

            logger.info(f"Creating migration: {args.create}")
            command.revision(
                alembic_cfg,
                message=args.create,
                autogenerate=True
            )
            logger.info(f"{Colors.OKGREEN}✓ Migration created successfully{Colors.ENDC}")
            return True, None

        elif args.downgrade:
            logger.info(f"Downgrading to: {args.downgrade}")
            command.downgrade(alembic_cfg, args.downgrade)
            logger.info(f"{Colors.OKGREEN}✓ Downgrade completed{Colors.ENDC}")
            # Return downgrade target for cleanup
            return True, args.downgrade

        elif args.current:
            logger.info("Current revision:")
            command.current(alembic_cfg)
            return True, None

        elif args.history:
            logger.info("Migration history:")
            command.history(alembic_cfg)
            return True, None

        elif args.check:
            # Check for pending migrations and model changes
            logger.info("Checking migration status...")

            has_pending, pending = check_pending_migrations()
            if has_pending:
                logger.info(f"{Colors.WARNING}⚠ Pending migrations: {len(pending)}{Colors.ENDC}")
                for rev in pending[:5]:
                    logger.info(f"  - {rev}")
            else:
                logger.info(f"{Colors.OKGREEN}✓ Database is up to date{Colors.ENDC}")

            has_changes, changes = check_model_changes()
            if has_changes:
                logger.info(f"{Colors.WARNING}⚠ Model changes detected:{Colors.ENDC}")
                for change in changes[:10]:
                    logger.info(f"  - {change}")
                logger.info("  Run: python scripts/migrate.py --create \"migration_name\"")
            else:
                logger.info(f"{Colors.OKGREEN}✓ No model changes detected{Colors.ENDC}")
            return True, None

        else:  # Default: upgrade
            # Check if there are pending migrations before upgrading
            has_pending, pending = check_pending_migrations()
            if not has_pending and not args.force:
                logger.info(f"{Colors.OKGREEN}✓ Database is already up to date, no migrations to apply{Colors.ENDC}")
                return True, None

            if has_pending:
                logger.info(f"Found {len(pending)} pending migration(s)")

            logger.info("Upgrading to head...")
            command.upgrade(alembic_cfg, "head")
            logger.info(f"{Colors.OKGREEN}✓ Upgrade completed{Colors.ENDC}")
            return True, None
        
    except Exception as e:
        logger.error(f"\n{Colors.FAIL}✗ Alembic error: {e}{Colors.ENDC}")
        logger.error("\nFull error details:")
        import traceback
        traceback.print_exc()

        logger.error("\n" + "=" * 60)
        logger.error("TROUBLESHOOTING TIPS:")
        logger.error("=" * 60)
        logger.error("1. Check that models.py files call register_module_base()")
        logger.error("2. Verify alembic/env.py imports MODULE_BASES correctly")
        logger.error("3. Check that alembic/env.py imports all model files")
        logger.error("4. Ensure models are registered BEFORE env.py runs")
        logger.error("5. Check alembic/script.py.mako exists")

        return False, None


async def main():
    """Main function with async pre-checks"""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Migration script with async support and multi-schema"
    )
    parser.add_argument(
        "--create", 
        type=str, 
        help="Create new migration with message"
    )
    parser.add_argument(
        "--upgrade", 
        action="store_true", 
        help="Upgrade to head (default)"
    )
    parser.add_argument(
        "--downgrade", 
        type=str, 
        help="Downgrade to revision"
    )
    parser.add_argument(
        "--current", 
        action="store_true", 
        help="Show current revision"
    )
    parser.add_argument(
        "--history",
        action="store_true",
        help="Show migration history"
    )
    parser.add_argument(
        "--check",
        action="store_true",
        help="Check for pending migrations and model changes (no changes made)"
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Force operation even if no changes detected"
    )
    args = parser.parse_args()
    
    # Print header
    logger.info("=" * 60)
    logger.info("MIGRATION SCRIPT (Multi-Schema Support)")
    logger.info("=" * 60)
    logger.info(f"Working directory: {os.getcwd()}")
    logger.info(f"Python path: {sys.path[0]}")
    logger.info("=" * 60)
    
    # Run async pre-checks
    try:
        # Check 1: Database connection
        if not await verify_database_connection():
            logger.error("\n✗ Database connection check failed")
            return 1
        
        # Check 2: Schemas
        if not await verify_schemas_exist():
            logger.error("\n✗ Schema verification failed")
            return 1
        
        # Check 3: Models (sync)
        if not verify_models_loaded():
            logger.error("\n✗ Model import check failed")
            return 1
        
        # Check 4: Metadata (sync)
        if not verify_metadata():
            logger.error("\n✗ Metadata verification failed")
            return 1
        
        # All checks passed, run Alembic
        logger.info(f"\n{Colors.OKGREEN}✓ All pre-checks passed!{Colors.ENDC}")

        success, downgrade_target = run_alembic_command(args)
        if not success:
            return 1

        # Run cleanup after downgrade
        if downgrade_target is not None:
            if not await cleanup_after_downgrade(downgrade_target):
                logger.warning("Cleanup had issues, but downgrade was successful")

        # Success!
        logger.info("\n" + "=" * 60)
        logger.info(f"{Colors.OKGREEN}✅ Migration completed successfully!{Colors.ENDC}")
        logger.info("=" * 60)

        return 0
        
    except Exception as e:
        logger.error(f"\n{Colors.FAIL}✗ Migration failed: {e}{Colors.ENDC}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)