"""File repository implementation"""

from typing import List, Optional
from uuid import UUID

from sqlalchemy import or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from contexts.file_management.application.ports.file_repository import IFileRepository
from contexts.file_management.domain.entities.file import File
from contexts.file_management.domain.value_objects.file_path import FilePath
from contexts.file_management.domain.value_objects.file_size import FileSize
from contexts.file_management.domain.value_objects.mime_type import MimeType
from infrastructure.database.orm.adapters.sqlalchemy.shared import BaseRepository

from ..models.file_model import FileModel


class FileRepository(BaseRepository[File, FileModel], IFileRepository):
    """
    File repository implementation.

    Receives session from UoW via constructor injection.
    """

    def __init__(self, session: AsyncSession):
        """
        Initialize file repository with session.

        Args:
            session: SQLAlchemy async session from UoW
        """
        super().__init__(session, File, FileModel)

    async def save(self, file: File) -> File:
        """
        Persist a file entity. Delegates to add() for new entities (no id)
        or update() for existing ones.
        """
        if getattr(file, "id", None) is None:
            return await self.add(file)
        return await self.update(file)

    async def get_by_name(self, name: str) -> Optional[File]:
        """Get file by internal name"""
        stmt = select(FileModel).where(FileModel.name == name, FileModel.is_deleted == False)
        result = await self._session.execute(stmt)
        model = result.scalar_one_or_none()

        return self._to_entity(model) if model else None

    async def get_by_owner(self, owner_id: UUID, skip: int = 0, limit: int = 100) -> List[File]:
        """Get files by owner"""
        stmt = (
            select(FileModel)
            .where(FileModel.owner_id == owner_id, FileModel.is_deleted == False)
            .offset(skip)
            .limit(limit)
            .order_by(FileModel.created_at.desc())
        )

        result = await self._session.execute(stmt)
        models = result.scalars().all()

        return [self._to_entity(model) for model in models]

    async def get_public_files(self, skip: int = 0, limit: int = 100) -> List[File]:
        """Get public files"""
        stmt = (
            select(FileModel)
            .where(FileModel.is_public == True, FileModel.is_deleted == False)
            .offset(skip)
            .limit(limit)
            .order_by(FileModel.created_at.desc())
        )

        result = await self._session.execute(stmt)
        models = result.scalars().all()

        return [self._to_entity(model) for model in models]

    async def get_accessible_by_user(
        self, user_id: UUID, skip: int = 0, limit: int = 100
    ) -> List[File]:
        """Get files accessible by user"""
        stmt = (
            select(FileModel)
            .where(
                or_(
                    FileModel.owner_id == user_id,
                    FileModel.is_public == True,
                    FileModel.shared_with.contains([user_id]),
                ),
                FileModel.is_deleted == False,
            )
            .offset(skip)
            .limit(limit)
            .order_by(FileModel.created_at.desc())
        )

        result = await self._session.execute(stmt)
        models = result.scalars().all()

        return [self._to_entity(model) for model in models]

    async def count_by_owner(self, owner_id: UUID) -> int:
        """Count files by owner"""
        from sqlalchemy import func

        stmt = (
            select(func.count())
            .select_from(FileModel)
            .where(FileModel.owner_id == owner_id, FileModel.is_deleted == False)
        )
        result = await self._session.execute(stmt)
        return result.scalar_one()

    def _to_entity(self, model: FileModel) -> File:
        """Convert ORM model to domain entity"""
        entity = File(
            name=str(model.name),
            original_name=str(model.original_name),
            path=FilePath(str(model.path)),
            size=FileSize(int(model.size)),  # type: ignore[arg-type]
            mime_type=MimeType(str(model.mime_type)),
            owner_id=model.owner_id,  # type: ignore[arg-type]
            description=str(model.description) if model.description else None,
            is_public=bool(model.is_public),
            download_count=int(model.download_count),  # type: ignore[arg-type]
            id=model.id,  # type: ignore[arg-type]
        )

        # Set internal state
        entity._created_at = model.created_at  # type: ignore[assignment]
        entity._updated_at = model.updated_at  # type: ignore[assignment]
        entity._is_deleted = model.is_deleted  # type: ignore[assignment]
        shared = model.shared_with
        entity._shared_with = list(shared) if shared else []

        return entity

    def _to_model(self, entity: File) -> FileModel:
        """Convert domain entity to ORM model"""
        return FileModel(
            id=entity.id,
            name=entity.name,
            original_name=entity.original_name,
            path=entity.path.value,
            size=entity.size.bytes,
            mime_type=entity.mime_type.value,
            owner_id=entity.owner_id,
            description=entity.description,
            is_public=entity.is_public,
            download_count=entity.download_count,
            shared_with=entity.shared_with,
            created_at=entity.created_at,
            updated_at=entity.updated_at,
            is_deleted=entity.is_deleted,
        )
