"""
Base repository implementation with SQLAlchemy.
Provides common CRUD operations for all entities.

Session is injected via constructor from UoW.
"""

from typing import TYPE_CHECKING, Any, Dict, Generic, List, Optional, Type, TypeVar
from uuid import UUID

from sqlalchemy import delete, func, or_, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from infrastructure.database.orm.adapters.sqlalchemy.shared.base_model import BaseModel
from shared.application.ports.repositories import IRepository
from shared.domain.base_entity import BaseEntity

if TYPE_CHECKING:
    from shared.application.ports import ILogger

TEntity = TypeVar("TEntity", bound=BaseEntity)
TModel = TypeVar("TModel", bound=BaseModel)


class BaseRepository(IRepository[TEntity], Generic[TEntity, TModel]):
    """
    Base repository implementation with SQLAlchemy.
    Implements common CRUD operations.

    Session is injected via constructor - typically from UoW.
    """

    def __init__(
        self,
        session: AsyncSession,
        entity_class: Type[TEntity],
        model_class: Type[TModel],
        logger: Optional["ILogger"] = None,
    ):
        """
        Initialize repository.

        Args:
            session: SQLAlchemy async session (from UoW)
            entity_class: Domain entity class
            model_class: SQLAlchemy model class
            logger: Optional logger instance (injected via DI)
        """
        self._session = session
        self._entity_class = entity_class
        self._model_class = model_class
        self._logger = logger

    async def get_by_id(self, id: UUID) -> Optional[TEntity]:
        """
        Get entity by ID.

        Args:
            id: Entity UUID

        Returns:
            Entity if found, None otherwise
        """
        if self._logger:
            self._logger.debug(f"Getting {self._model_class.__name__} by id: {id}")

        stmt = select(self._model_class).where(
            self._model_class.id == id, self._model_class.is_deleted == False
        )
        result = await self._session.execute(stmt)
        model = result.scalar_one_or_none()

        if model is None:
            if self._logger:
                self._logger.debug(f"{self._model_class.__name__} not found: {id}")
            return None

        return self._to_entity(model)

    async def get_all(
        self, skip: int = 0, limit: int = 100, include_deleted: bool = False
    ) -> List[TEntity]:
        """
        Get all entities with pagination.

        Args:
            skip: Number of records to skip
            limit: Maximum number of records to return
            include_deleted: Include soft-deleted records

        Returns:
            List of entities
        """
        if self._logger:
            self._logger.debug(
                f"Getting all {self._model_class.__name__} "
                f"(skip={skip}, limit={limit}, include_deleted={include_deleted})"
            )

        stmt = select(self._model_class)

        if not include_deleted:
            stmt = stmt.where(self._model_class.is_deleted == False)

        stmt = stmt.offset(skip).limit(limit).order_by(self._model_class.created_at.desc())

        result = await self._session.execute(stmt)
        models = result.scalars().all()

        if self._logger:
            self._logger.debug(f"Found {len(models)} {self._model_class.__name__} records")

        return [self._to_entity(model) for model in models]

    async def add(self, entity: TEntity) -> TEntity:
        """
        Add new entity.

        Args:
            entity: Entity to add

        Returns:
            Added entity with generated ID
        """
        if self._logger:
            self._logger.debug(f"Adding new {self._entity_class.__name__}")

        model = self._to_model(entity)
        self._session.add(model)
        await self._session.flush()
        await self._session.refresh(model)

        if self._logger:
            self._logger.info(f"Added {self._entity_class.__name__} with id: {model.id}")

        return self._to_entity(model)

    async def add_many(self, entities: List[TEntity]) -> List[TEntity]:
        """
        Add multiple entities.

        Args:
            entities: List of entities to add

        Returns:
            List of added entities
        """
        if self._logger:
            self._logger.debug(f"Adding {len(entities)} {self._entity_class.__name__} records")

        models = [self._to_model(entity) for entity in entities]
        self._session.add_all(models)
        await self._session.flush()

        for model in models:
            await self._session.refresh(model)

        if self._logger:
            self._logger.info(f"Added {len(models)} {self._entity_class.__name__} records")

        return [self._to_entity(model) for model in models]

    async def update(self, entity: TEntity) -> TEntity:
        """
        Update existing entity.

        Args:
            entity: Entity to update

        Returns:
            Updated entity
        """
        if self._logger:
            self._logger.debug(f"Updating {self._entity_class.__name__} with id: {entity.id}")

        entity.update_timestamp()
        model = self._to_model(entity)

        merged = await self._session.merge(model)
        await self._session.flush()
        await self._session.refresh(merged)

        if self._logger:
            self._logger.info(f"Updated {self._entity_class.__name__} with id: {entity.id}")

        return self._to_entity(merged)

    async def delete(self, id: UUID, soft: bool = True) -> None:
        """
        Delete entity (soft or hard delete).

        Args:
            id: Entity UUID
            soft: If True, perform soft delete; if False, hard delete
        """
        if self._logger:
            self._logger.debug(f"Deleting {self._model_class.__name__} with id: {id} (soft={soft})")

        if soft:
            stmt = (
                update(self._model_class).where(self._model_class.id == id).values(is_deleted=True)
            )
        else:
            stmt = delete(self._model_class).where(self._model_class.id == id)

        result = await self._session.execute(stmt)
        await self._session.flush()

        if result.rowcount == 0:
            if self._logger:
                self._logger.warning(f"{self._model_class.__name__} not found for deletion: {id}")
        else:
            if self._logger:
                self._logger.info(
                    f"{'Soft' if soft else 'Hard'} deleted "
                    f"{self._model_class.__name__} with id: {id}"
                )

    async def delete_many(self, ids: List[UUID], soft: bool = True) -> int:
        """
        Delete multiple entities.

        Args:
            ids: List of entity UUIDs
            soft: If True, perform soft delete

        Returns:
            Number of deleted records
        """
        if self._logger:
            self._logger.debug(
                f"Deleting {len(ids)} {self._model_class.__name__} records (soft={soft})"
            )

        if soft:
            stmt = (
                update(self._model_class)
                .where(self._model_class.id.in_(ids))
                .values(is_deleted=True)
            )
        else:
            stmt = delete(self._model_class).where(self._model_class.id.in_(ids))

        result = await self._session.execute(stmt)
        await self._session.flush()

        if self._logger:
            self._logger.info(f"Deleted {result.rowcount} {self._model_class.__name__} records")

        return result.rowcount

    async def exists(self, id: UUID) -> bool:
        """
        Check if entity exists.

        Args:
            id: Entity UUID

        Returns:
            True if exists, False otherwise
        """
        stmt = (
            select(func.count())
            .select_from(self._model_class)
            .where(self._model_class.id == id, self._model_class.is_deleted == False)
        )
        result = await self._session.execute(stmt)
        count = result.scalar_one()

        return count > 0

    async def count(self, include_deleted: bool = False) -> int:
        """
        Count entities.

        Args:
            include_deleted: Include soft-deleted records

        Returns:
            Total count
        """
        stmt = select(func.count()).select_from(self._model_class)

        if not include_deleted:
            stmt = stmt.where(self._model_class.is_deleted == False)

        result = await self._session.execute(stmt)
        return result.scalar_one()

    async def find_by_criteria(
        self,
        filters: Dict[str, Any],
        skip: int = 0,
        limit: int = 100,
        order_by: Optional[str] = None,
        order_desc: bool = True,
    ) -> List[TEntity]:
        """
        Find entities by criteria.

        Args:
            filters: Dictionary of field:value filters
            skip: Number of records to skip
            limit: Maximum number of records
            order_by: Field to order by
            order_desc: Order descending if True

        Returns:
            List of matching entities
        """
        if self._logger:
            self._logger.debug(f"Finding {self._model_class.__name__} by criteria: {filters}")

        stmt = select(self._model_class).where(self._model_class.is_deleted == False)

        # Apply filters
        for field, value in filters.items():
            if hasattr(self._model_class, field):
                column = getattr(self._model_class, field)
                if isinstance(value, list):
                    stmt = stmt.where(column.in_(value))
                else:
                    stmt = stmt.where(column == value)

        # Apply ordering
        if order_by and hasattr(self._model_class, order_by):
            order_column = getattr(self._model_class, order_by)
            stmt = stmt.order_by(order_column.desc() if order_desc else order_column.asc())
        else:
            stmt = stmt.order_by(self._model_class.created_at.desc())

        # Apply pagination
        stmt = stmt.offset(skip).limit(limit)

        result = await self._session.execute(stmt)
        models = result.scalars().all()

        if self._logger:
            self._logger.debug(f"Found {len(models)} matching records")

        return [self._to_entity(model) for model in models]

    async def search(
        self, search_term: str, search_fields: List[str], skip: int = 0, limit: int = 100
    ) -> List[TEntity]:
        """
        Search entities by text in specified fields.

        Args:
            search_term: Text to search for
            search_fields: List of field names to search in
            skip: Number of records to skip
            limit: Maximum number of records

        Returns:
            List of matching entities
        """
        if self._logger:
            self._logger.debug(
                f"Searching {self._model_class.__name__} for '{search_term}' "
                f"in fields: {search_fields}"
            )

        stmt = select(self._model_class).where(self._model_class.is_deleted == False)

        # Build search conditions
        search_conditions = []
        for field in search_fields:
            if hasattr(self._model_class, field):
                column = getattr(self._model_class, field)
                search_conditions.append(column.ilike(f"%{search_term}%"))

        if search_conditions:
            stmt = stmt.where(or_(*search_conditions))

        stmt = stmt.offset(skip).limit(limit).order_by(self._model_class.created_at.desc())

        result = await self._session.execute(stmt)
        models = result.scalars().all()

        if self._logger:
            self._logger.debug(f"Found {len(models)} matching records")

        return [self._to_entity(model) for model in models]

    async def find_one_by_criteria(self, filters: Dict[str, Any]) -> Optional[TEntity]:
        """
        Find single entity by criteria.

        Args:
            filters: Dictionary of field:value filters

        Returns:
            Entity if found, None otherwise
        """
        results = await self.find_by_criteria(filters, limit=1)
        return results[0] if results else None

    def _to_entity(self, model: TModel) -> TEntity:
        """
        Convert ORM model to domain entity.
        Must be implemented by subclasses.

        Args:
            model: ORM model

        Returns:
            Domain entity

        Raises:
            NotImplementedError: If not implemented by subclass
        """
        raise NotImplementedError(
            f"Subclass must implement _to_entity method for {self._entity_class.__name__}"
        )

    def _to_model(self, entity: TEntity) -> TModel:
        """
        Convert domain entity to ORM model.
        Must be implemented by subclasses.

        Args:
            entity: Domain entity

        Returns:
            ORM model

        Raises:
            NotImplementedError: If not implemented by subclass
        """
        raise NotImplementedError(
            f"Subclass must implement _to_model method for {self._entity_class.__name__}"
        )
