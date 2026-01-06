"""Test value object functionality"""

import pytest

from shared.domain.value_objects import ValueObject


class TestValueObject(ValueObject):
    """Test value object implementation"""

    def __init__(self, value: str):
        self._value = value
        self._seal()

    @property
    def value(self) -> str:
        return self._value


class TestValueObjectBehavior:
    """Test ValueObject behavior"""

    def test_value_object_equality(self):
        """Test value objects are equal if attributes match"""
        vo1 = TestValueObject("test")
        vo2 = TestValueObject("test")

        assert vo1 == vo2

    def test_value_object_inequality(self):
        """Test value objects are not equal if attributes differ"""
        vo1 = TestValueObject("test1")
        vo2 = TestValueObject("test2")

        assert vo1 != vo2

    def test_value_object_immutability(self):
        """Test value objects cannot be modified after creation"""
        vo = TestValueObject("test")

        with pytest.raises(AttributeError):
            vo._value = "modified"

    def test_value_object_hash(self):
        """Test value objects can be hashed"""
        vo = TestValueObject("test")

        # Should not raise exception
        hash_value = hash(vo)
        assert isinstance(hash_value, int)
