"""Test base entity functionality"""

from datetime import datetime
from uuid import uuid4

import pytest

from shared.domain.base_entity import BaseEntity


class TestBaseEntity:
    """Test BaseEntity class"""

    def test_entity_creation(self):
        """Test entity is created with auto-generated ID"""
        entity = BaseEntity()

        assert entity.id is not None
        assert isinstance(entity.created_at, datetime)
        assert isinstance(entity.updated_at, datetime)
        assert entity.is_deleted is False

    def test_entity_with_provided_id(self):
        """Test entity creation with provided ID"""
        entity_id = uuid4()
        entity = BaseEntity(id=entity_id)

        assert entity.id == entity_id

    def test_entity_equality(self):
        """Test entities are equal if IDs match"""
        entity_id = uuid4()
        entity1 = BaseEntity(id=entity_id)
        entity2 = BaseEntity(id=entity_id)

        assert entity1 == entity2

    def test_entity_inequality(self):
        """Test entities are not equal if IDs differ"""
        entity1 = BaseEntity()
        entity2 = BaseEntity()

        assert entity1 != entity2

    def test_entity_hash(self):
        """Test entity can be hashed"""
        entity = BaseEntity()

        # Should not raise exception
        hash(entity)

    def test_mark_as_deleted(self):
        """Test soft delete functionality"""
        entity = BaseEntity()
        initial_updated_at = entity.updated_at

        entity.mark_as_deleted()

        assert entity.is_deleted is True
        assert entity.updated_at > initial_updated_at

    def test_restore(self):
        """Test restore soft-deleted entity"""
        entity = BaseEntity()
        entity.mark_as_deleted()

        entity.restore()

        assert entity.is_deleted is False

    def test_update_timestamp(self):
        """Test timestamp update"""
        entity = BaseEntity()
        initial_updated_at = entity.updated_at

        import time

        time.sleep(0.01)  # Small delay

        entity.update_timestamp()

        assert entity.updated_at > initial_updated_at
