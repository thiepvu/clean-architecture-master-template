"""
User module models using BaseModel.
Fixed for multi-schema foreign key references.
"""

from sqlalchemy import Boolean, Column, DateTime, ForeignKey, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

# Import register_module_base
from infrastructure.database.orm.adapters.sqlalchemy.shared.base_model import register_module_base

# Register module and get Base + BaseModel (uses default schema from registry)
# No config service needed - schema comes from DEFAULT_MODULE_SCHEMAS
module_base = register_module_base("user")


class UserModel(module_base.BaseModel):  # type: ignore[name-defined]
    """
    User model inheriting from BaseModel.

    Gets these fields automatically from BaseModel:
    - id (UUID, primary key)
    - created_at (DateTime)
    - updated_at (DateTime)
    - is_deleted (Boolean)
    """

    __tablename__ = "users"

    # Only define fields specific to User
    email = Column(
        String(255), unique=True, nullable=False, index=True, comment="User email address"
    )
    username = Column(
        String(100), unique=True, nullable=False, index=True, comment="Unique username"
    )
    first_name = Column(String(100), nullable=False, comment="User first name")
    last_name = Column(String(100), nullable=False, comment="User last name")
    is_active = Column(
        Boolean, default=True, nullable=False, index=True, comment="Whether user is active"
    )

    # Relationships
    profile = relationship(
        "UserProfileModel",  # Fixed: Use actual class name
        back_populates="user",
        uselist=False,
        cascade="all, delete-orphan",
    )

    def __repr__(self):
        return f"<UserModel(id={self.id}, email={self.email}, username={self.username})>"


class UserProfileModel(module_base.BaseModel):  # type: ignore[name-defined]
    """
    User profile model.

    Also inherits from BaseModel, so it gets:
    - id, created_at, updated_at, is_deleted
    """

    __tablename__ = "user_profiles"

    # Reference to User (using UUID foreign key)
    # CRITICAL FIX: Use schema.table for multi-schema
    user_id = Column(
        UUID(as_uuid=True),
        ForeignKey(f"{module_base.schema_name}.users.id", ondelete="CASCADE"),
        nullable=False,
        unique=True,
    )

    first_name = Column(String(100))
    last_name = Column(String(100))
    phone = Column(String(20))
    avatar_url = Column(String(500))
    bio = Column(String(1000))

    # Relationships
    user = relationship("UserModel", back_populates="profile")  # Fixed: Use actual class name

    @property
    def full_name(self) -> str:
        """Get user's full name"""
        first = str(self.first_name) if self.first_name else ""
        last = str(self.last_name) if self.last_name else ""
        if first and last:
            return f"{first} {last}"
        return first or last or ""

    def __repr__(self):
        return f"<UserProfileModel(id={self.id}, user_id={self.user_id}, name={self.full_name})>"


class UserSessionModel(module_base.Base):  # type: ignore[name-defined]
    """
    Example: Model that does NOT inherit from BaseModel.

    This is useful when you want custom primary key or don't need
    the common fields (id, timestamps, is_deleted).
    """

    __tablename__ = "user_sessions"

    # Custom primary key (not UUID)
    session_token = Column(String(255), primary_key=True)

    # Custom user reference
    # CRITICAL FIX: Use schema.table for multi-schema
    user_id = Column(
        UUID(as_uuid=True),
        ForeignKey(f"{module_base.schema_name}.users.id", ondelete="CASCADE"),
        nullable=False,
    )

    # Custom fields
    ip_address = Column(String(45))
    user_agent = Column(String(500))
    expires_at = Column(DateTime, nullable=False)

    # Note: No created_at, updated_at, is_deleted
    # because we inherit from Base, not BaseModel


# ============================================================================
# Usage Examples
# ============================================================================


# Example 1: Create user with profile
async def example_create_user(session):
    """Example: Create user using BaseModel"""
    from datetime import datetime

    # Create user
    user = UserModel(email="john@example.com", username="john_doe", is_active=True)
    # id, created_at, updated_at, is_deleted are set automatically!

    session.add(user)
    await session.flush()  # Get user.id

    # Create profile
    profile = UserProfileModel(
        user_id=user.id, first_name="John", last_name="Doe", phone="+1234567890"
    )
    # This also gets id, created_at, updated_at, is_deleted automatically!

    session.add(profile)
    await session.commit()

    return user


# Example 2: Soft delete
async def example_soft_delete(session, user_id):
    """Example: Soft delete using BaseModel method"""
    from sqlalchemy import select

    # Get user
    result = await session.execute(select(UserModel).where(UserModel.id == user_id))
    user = result.scalar_one_or_none()

    if user:
        # Soft delete (sets is_deleted = True)
        user.soft_delete()
        await session.commit()


# Example 3: Query excluding soft-deleted
async def example_query_active_users(session):
    """Example: Query only non-deleted users"""
    from sqlalchemy import select

    # Get all active (non-deleted) users
    result = await session.execute(select(UserModel).where(UserModel.is_deleted == False))
    active_users = result.scalars().all()

    return active_users


# Example 4: Restore soft-deleted record
async def example_restore_user(session, user_id):
    """Example: Restore soft-deleted user"""
    from sqlalchemy import select

    # Get user (including soft-deleted)
    result = await session.execute(select(UserModel).where(UserModel.id == user_id))
    user = result.scalar_one_or_none()

    if user and user.is_deleted:
        # Restore
        user.restore()
        await session.commit()
