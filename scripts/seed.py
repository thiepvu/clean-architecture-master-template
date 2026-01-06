#!/usr/bin/env python3
"""
Smart Database Seeder Script
============================

A production-ready seeder script with async support and idempotent operations.
Seeds sample/test data for all contexts with smart skip logic.

Features
--------
- **Idempotent**: Only seeds if data doesn't already exist
- **Force Mode**: Delete existing data and reseed when needed
- **Module-Specific**: Seed individual modules or all at once
- **Dry-Run**: Check what needs seeding without making changes
- **Dependency Order**: Seeds modules in correct order (users before files)

Commands
--------

1. SEED ALL (default - seed all modules):
   ```bash
   python scripts/seed.py                   # Smart seed (skip existing data)
   python scripts/seed.py --force           # Force reseed (delete + recreate all)
   ```

2. SEED SPECIFIC MODULE:
   ```bash
   python scripts/seed.py --module user     # Seed only user module
   python scripts/seed.py --module file     # Seed only file module
   python scripts/seed.py --module user --force  # Force reseed user module
   ```

3. CHECK STATUS (no changes):
   ```bash
   python scripts/seed.py --check           # Show what needs seeding
   ```

4. LIST MODULES:
   ```bash
   python scripts/seed.py --list            # List available modules
   ```

Available Modules
-----------------
- **user**: Sample users (admin, john_doe, jane_doe)
- **file**: Sample files (PDF document, JPEG image)

Examples
--------
# First time setup (after migrations)
python scripts/migrate.py --upgrade
python scripts/seed.py

# Check current state
python scripts/seed.py --check

# Reseed everything (development)
python scripts/seed.py --force

# Seed only users
python scripts/seed.py --module user

# Reseed only files
python scripts/seed.py --module file --force

Exit Codes
----------
- 0: Success (seeded or skipped)
- 1: Error (connection failed, seeding failed, etc.)

Notes
-----
- Run migrations first: `python scripts/migrate.py`
- Modules are seeded in dependency order (users → files)
- Force mode will DELETE existing data before reseeding
- Sample data is for development/testing only

Adding New Seeders
------------------
1. Create seeder function: `async def seed_mymodule(session, force=False)`
2. Register in SEEDERS dict: `"mymodule": seed_mymodule`
3. Update check_seed_status() to include the new module
"""
import sys
import asyncio
from pathlib import Path

# Add project root to path
project_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(project_root / "src"))

from sqlalchemy import text

# Import from YOUR project
from infrastructure.database.orm.adapters.sqlalchemy.shared.datasource import datasource as db, get_session
from shared.bootstrap import create_config_service, create_logger

# Initialize config service and logger (bootstrap level - uses helpers)
config_service = create_config_service()
logger = create_logger(config_service=config_service)


# ============================================================================
# SEEDER REGISTRY
# ============================================================================

# Import models to ensure they are registered
from infrastructure.database.orm.adapters.sqlalchemy.contexts.user_management.models import (
    UserModel,
    UserProfileModel,
)
from infrastructure.database.orm.adapters.sqlalchemy.contexts.file_management.models import (
    FileModel,
)


# Seeder functions
async def seed_users(session, force: bool = False):
    """Seed sample users"""
    import uuid
    from datetime import datetime

    # Check if users already exist
    from sqlalchemy import select, func, delete

    result = await session.execute(select(func.count()).select_from(UserModel))
    count = result.scalar()

    if count > 0:
        if not force:
            logger.info(f"  ✓ Users already exist ({count}), skipping...")
            return False  # No changes made
        else:
            logger.info(f"  Deleting existing users ({count})...")
            await session.execute(delete(UserModel))

    # Create sample users
    users_data = [
        {
            "id": uuid.uuid4(),
            "email": "admin@example.com",
            "username": "admin",
            "first_name": "Admin",
            "last_name": "User",
            "is_active": True,
        },
        {
            "id": uuid.uuid4(),
            "email": "john@example.com",
            "username": "john_doe",
            "first_name": "John",
            "last_name": "Doe",
            "is_active": True,
        },
        {
            "id": uuid.uuid4(),
            "email": "jane@example.com",
            "username": "jane_doe",
            "first_name": "Jane",
            "last_name": "Doe",
            "is_active": True,
        },
    ]

    for user_data in users_data:
        user = UserModel(**user_data)
        session.add(user)
        logger.info(f"  Created user: {user_data['email']}")

    logger.info(f"  ✓ Created {len(users_data)} users")
    return True  # Changes made


async def seed_files(session, force: bool = False):
    """Seed sample files"""
    import uuid

    # Check if files already exist
    from sqlalchemy import select, func, delete

    result = await session.execute(select(func.count()).select_from(FileModel))
    count = result.scalar()

    if count > 0:
        if not force:
            logger.info(f"  ✓ Files already exist ({count}), skipping...")
            return False  # No changes made
        else:
            logger.info(f"  Deleting existing files ({count})...")
            await session.execute(delete(FileModel))

    # Get first user for owner_id
    result = await session.execute(select(UserModel).limit(1))
    user = result.scalar_one_or_none()

    if not user:
        logger.warning("  No users found, cannot create files without owner")
        return

    # Create sample files
    files_data = [
        {
            "id": uuid.uuid4(),
            "name": "document_001.pdf",
            "original_name": "Annual Report 2024.pdf",
            "path": "/uploads/documents/document_001.pdf",
            "size": 1024000,
            "mime_type": "application/pdf",
            "owner_id": user.id,
            "description": "Annual company report",
            "is_public": False,
        },
        {
            "id": uuid.uuid4(),
            "name": "image_001.jpg",
            "original_name": "profile_photo.jpg",
            "path": "/uploads/images/image_001.jpg",
            "size": 256000,
            "mime_type": "image/jpeg",
            "owner_id": user.id,
            "description": "Profile photo",
            "is_public": True,
        },
    ]

    for file_data in files_data:
        file = FileModel(**file_data)
        session.add(file)
        logger.info(f"  Created file: {file_data['original_name']}")

    logger.info(f"  ✓ Created {len(files_data)} files")
    return True  # Changes made


SEEDERS = {
    "user": seed_users,
    "file": seed_files,
}


async def check_seed_status() -> dict[str, dict]:
    """
    Check what needs to be seeded.

    Returns:
        dict: {module_name: {"count": int, "needs_seed": bool}}
    """
    from sqlalchemy import select, func

    if not db.is_initialized:
        db.initialize()

    status = {}

    async with db.session_context() as session:
        # Check users
        result = await session.execute(select(func.count()).select_from(UserModel))
        user_count = result.scalar()
        status["user"] = {"count": user_count, "needs_seed": user_count == 0}

        # Check files
        result = await session.execute(select(func.count()).select_from(FileModel))
        file_count = result.scalar()
        status["file"] = {"count": file_count, "needs_seed": file_count == 0}

    return status


# ============================================================================
# MAIN SEEDING LOGIC
# ============================================================================

async def verify_database() -> bool:
    """Verify database connection"""
    logger.info("Step 1: Verifying database connection...")
    
    if not db.is_initialized:
        db.initialize()
    
    try:
        async with db.engine.begin() as conn:
            result = await conn.execute(text("SELECT version()"))
            version = result.scalar()
            logger.info(f"  ✓ Connected to PostgreSQL")
            logger.info(f"  Version: {version}")
            return True
    except Exception as e:
        logger.error(f"  ✗ Database connection failed: {e}")
        return False


async def verify_tables_exist() -> bool:
    """Verify that tables exist (migrations have been run)"""
    logger.info("\nStep 2: Verifying tables exist...")
    
    if not db.is_initialized:
        db.initialize()
    
    try:
        async with db.engine.begin() as conn:
            for schema_name in config_service.database.MODULE_SCHEMAS.values():
                result = await conn.execute(text(f"""
                    SELECT COUNT(*)
                    FROM information_schema.tables
                    WHERE table_schema = '{schema_name}'
                """))
                count = result.scalar()
                
                if count == 0:
                    logger.warning(f"  ⚠ No tables found in schema '{schema_name}'")
                    logger.warning("  Run migrations first: python scripts/migrate.py")
                    return False
                
                logger.info(f"  ✓ Schema '{schema_name}' has {count} tables")
        
        return True
    except Exception as e:
        logger.error(f"  ✗ Table verification failed: {e}")
        return False


async def seed_module(module_name: str, force: bool = False) -> bool:
    """
    Seed a specific module.

    Args:
        module_name: Name of the module to seed
        force: If True, delete existing data and reseed

    Returns:
        True if seeding succeeded (or was skipped), False on error
    """
    if module_name not in SEEDERS:
        logger.error(f"✗ Unknown context: {module_name}")
        logger.info(f"Available contexts: {', '.join(SEEDERS.keys())}")
        return False

    logger.info(f"\nSeeding module: {module_name}")
    logger.info("─" * 60)

    if not db.is_initialized:
        db.initialize()

    try:
        # Get async session using context manager
        async with db.session_context() as session:
            try:
                # Run seeder - pass session and force flag
                result = await SEEDERS[module_name](session, force=force)
                # Commit is done here, not in seeder
                await session.commit()

                if result:
                    logger.info(f"✓ Module '{module_name}' seeded successfully\n")
                else:
                    logger.info(f"✓ Module '{module_name}' unchanged (data exists)\n")
                return True
            except Exception as e:
                await session.rollback()
                logger.error(f"✗ Error seeding {module_name}: {e}")
                import traceback
                traceback.print_exc()
                return False
    except Exception as e:
        logger.error(f"✗ Failed to get session: {e}")
        return False


async def seed_all_contexts(force: bool = False) -> bool:
    """Seed all contexts in order"""
    logger.info("\n" + "=" * 60)
    logger.info("SEEDING ALL CONTEXTS")
    if force:
        logger.info("(FORCE MODE - will delete and recreate data)")
    logger.info("=" * 60)

    success_count = 0
    failed_count = 0
    
    # Seed in order (users first, then files - dependency order)
    for module_name in SEEDERS.keys():
        if await seed_module(module_name, force=force):
            success_count += 1
        else:
            failed_count += 1
    
    logger.info("=" * 60)
    logger.info("SEEDING SUMMARY")
    logger.info("=" * 60)
    logger.info(f"✓ Successful: {success_count}")
    if failed_count > 0:
        logger.info(f"✗ Failed: {failed_count}")
    logger.info("=" * 60)
    
    return failed_count == 0


async def main():
    """Main seeding function"""
    import argparse

    parser = argparse.ArgumentParser(description="Smart database seeder (async)")
    parser.add_argument(
        "--module",
        type=str,
        help="Seed specific module",
        choices=list(SEEDERS.keys())
    )
    parser.add_argument(
        "--list",
        action="store_true",
        help="List available contexts"
    )
    parser.add_argument(
        "--check",
        action="store_true",
        help="Check seed status (no changes made)"
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Force reseed (delete existing data and recreate)"
    )
    args = parser.parse_args()

    logger.info("=" * 60)
    logger.info("DATABASE SEEDER (Smart)")
    logger.info("=" * 60)

    # List contexts
    if args.list:
        logger.info("\nAvailable contexts:")
        for context in SEEDERS.keys():
            logger.info(f"  - {context}")
        return 0

    try:
        # Pre-checks
        logger.info("\nRunning pre-checks...")
        logger.info("─" * 60)

        if not await verify_database():
            logger.error("\n✗ Database check failed")
            return 1

        if not await verify_tables_exist():
            logger.error("\n✗ Tables check failed")
            logger.error("Run migrations first: python scripts/migrate.py")
            return 1

        logger.info("\n✓ All pre-checks passed")

        # Check mode - just show status
        if args.check:
            logger.info("\n" + "=" * 60)
            logger.info("SEED STATUS CHECK")
            logger.info("=" * 60)

            status = await check_seed_status()
            needs_any = False

            for module, info in status.items():
                if info["needs_seed"]:
                    logger.info(f"  ⚠ {module}: needs seeding (0 records)")
                    needs_any = True
                else:
                    logger.info(f"  ✓ {module}: {info['count']} records exist")

            if needs_any:
                logger.info("\nRun: python scripts/seed.py")
            else:
                logger.info("\n✓ All modules have data, nothing to seed")
                logger.info("  Use --force to reseed anyway")

            return 0

        # Seed
        if args.module:
            success = await seed_module(args.module, force=args.force)
        else:
            success = await seed_all_contexts(force=args.force)

        if success:
            logger.info(f"\n✅ SEEDING COMPLETED SUCCESSFULLY!")
            return 0
        else:
            logger.error(f"\n✗ SEEDING FAILED")
            return 1
            
    except Exception as e:
        logger.error(f"\n✗ Seeding failed: {e}")
        import traceback
        traceback.print_exc()
        return 1
    finally:
        # Clean up
        if db.is_initialized:
            await db.close()


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)