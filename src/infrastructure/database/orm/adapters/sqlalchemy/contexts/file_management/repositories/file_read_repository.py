"""
File Read Repository Implementation.

Read-optimized repository for File queries.
Returns Read Models directly for efficient query operations.

NOTE: This repository manages its own sessions (short-lived).
It does NOT use UnitOfWork - that's for Write operations only.
"""

from typing import List, Optional
from uuid import UUID

from sqlalchemy import func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from contexts.file_management.application.ports.file_read_repository import IFileReadRepository
from contexts.file_management.application.read_models import (
    FileDownloadReadModel,
    FileListItemReadModel,
    FileReadModel,
)

from ..models.file_model import FileModel


class FileReadRepository(IFileReadRepository):
    """
    Read-optimized repository for File queries.

    This repository:
    - Returns Read Models directly (not domain entities)
    - Is optimized for query performance
    - Never modifies data
    - Manages its own sessions (no UoW dependency)
    - Can use caching in the future
    """

    def __init__(self, session_factory: async_sessionmaker[AsyncSession]):
        """
        Initialize repository with session factory.

        Args:
            session_factory: Factory for creating new sessions
        """
        self._session_factory = session_factory

    async def get_by_id(self, file_id: UUID) -> Optional[FileReadModel]:
        """Get file by ID."""
        async with self._session_factory() as session:
            stmt = select(FileModel).where(
                FileModel.id == file_id,
                FileModel.is_deleted == False,
            )
            result = await session.execute(stmt)
            model = result.scalar_one_or_none()

            return self._to_read_model(model) if model else None

    async def get_download_info(self, file_id: UUID) -> Optional[FileDownloadReadModel]:
        """Get file download information."""
        async with self._session_factory() as session:
            stmt = select(FileModel).where(
                FileModel.id == file_id,
                FileModel.is_deleted == False,
            )
            result = await session.execute(stmt)
            model = result.scalar_one_or_none()

            return self._to_download_model(model) if model else None

    async def list_files(
        self,
        skip: int = 0,
        limit: int = 100,
        owner_id: Optional[UUID] = None,
        is_public: Optional[bool] = None,
        accessible_by: Optional[UUID] = None,
    ) -> List[FileListItemReadModel]:
        """List files with pagination and optional filtering."""
        async with self._session_factory() as session:
            stmt = select(FileModel).where(FileModel.is_deleted == False)

            # Apply filters
            if accessible_by is not None:
                # User can access: owned, public, or shared with them
                stmt = stmt.where(
                    or_(
                        FileModel.owner_id == accessible_by,
                        FileModel.is_public == True,
                        FileModel.shared_with.contains([accessible_by]),
                    )
                )
            else:
                if owner_id is not None:
                    stmt = stmt.where(FileModel.owner_id == owner_id)
                if is_public is not None:
                    stmt = stmt.where(FileModel.is_public == is_public)

            # Apply pagination and ordering
            stmt = stmt.offset(skip).limit(limit).order_by(FileModel.created_at.desc())

            result = await session.execute(stmt)
            models = result.scalars().all()

            return [self._to_list_item_model(m) for m in models]

    async def count(
        self,
        owner_id: Optional[UUID] = None,
        is_public: Optional[bool] = None,
        accessible_by: Optional[UUID] = None,
    ) -> int:
        """Count files matching criteria."""
        async with self._session_factory() as session:
            stmt = select(func.count()).select_from(FileModel).where(FileModel.is_deleted == False)

            # Apply filters
            if accessible_by is not None:
                stmt = stmt.where(
                    or_(
                        FileModel.owner_id == accessible_by,
                        FileModel.is_public == True,
                        FileModel.shared_with.contains([accessible_by]),
                    )
                )
            else:
                if owner_id is not None:
                    stmt = stmt.where(FileModel.owner_id == owner_id)
                if is_public is not None:
                    stmt = stmt.where(FileModel.is_public == is_public)

            result = await session.execute(stmt)
            return result.scalar_one()

    async def exists(self, file_id: UUID) -> bool:
        """Check if file exists."""
        async with self._session_factory() as session:
            stmt = (
                select(func.count())
                .select_from(FileModel)
                .where(FileModel.id == file_id, FileModel.is_deleted == False)
            )
            result = await session.execute(stmt)
            return result.scalar_one() > 0

    async def can_access(self, file_id: UUID, user_id: UUID) -> bool:
        """Check if user can access file."""
        async with self._session_factory() as session:
            stmt = (
                select(func.count())
                .select_from(FileModel)
                .where(
                    FileModel.id == file_id,
                    FileModel.is_deleted == False,
                    or_(
                        FileModel.owner_id == user_id,
                        FileModel.is_public == True,
                        FileModel.shared_with.contains([user_id]),
                    ),
                )
            )
            result = await session.execute(stmt)
            return result.scalar_one() > 0

    async def is_owner(self, file_id: UUID, user_id: UUID) -> bool:
        """Check if user is the file owner."""
        async with self._session_factory() as session:
            stmt = (
                select(func.count())
                .select_from(FileModel)
                .where(
                    FileModel.id == file_id,
                    FileModel.owner_id == user_id,
                    FileModel.is_deleted == False,
                )
            )
            result = await session.execute(stmt)
            return result.scalar_one() > 0

    def _to_read_model(self, model: FileModel) -> FileReadModel:
        """Convert ORM model to read model."""
        shared = model.shared_with
        return FileReadModel(
            id=model.id,  # type: ignore[arg-type]
            name=str(model.name),
            original_name=str(model.original_name),
            path=str(model.path),
            size=int(model.size),  # type: ignore[arg-type]
            mime_type=str(model.mime_type),
            owner_id=model.owner_id,  # type: ignore[arg-type]
            description=str(model.description) if model.description else None,
            is_public=bool(model.is_public),
            download_count=int(model.download_count),  # type: ignore[arg-type]
            shared_with=list(shared) if shared else [],
            is_deleted=bool(model.is_deleted),
            created_at=model.created_at,  # type: ignore[arg-type]
            updated_at=model.updated_at,  # type: ignore[arg-type]
        )

    def _to_list_item_model(self, model: FileModel) -> FileListItemReadModel:
        """Convert ORM model to list item read model."""
        return FileListItemReadModel(
            id=model.id,  # type: ignore[arg-type]
            original_name=str(model.original_name),
            size=int(model.size),  # type: ignore[arg-type]
            mime_type=str(model.mime_type),
            is_public=bool(model.is_public),
            download_count=int(model.download_count),  # type: ignore[arg-type]
            owner_id=model.owner_id,  # type: ignore[arg-type]
            created_at=model.created_at,  # type: ignore[arg-type]
        )

    def _to_download_model(self, model: FileModel) -> FileDownloadReadModel:
        """Convert ORM model to download read model."""
        return FileDownloadReadModel(
            id=model.id,  # type: ignore[arg-type]
            name=str(model.name),
            original_name=str(model.original_name),
            path=str(model.path),
            mime_type=str(model.mime_type),
            size=int(model.size),  # type: ignore[arg-type]
        )
