"""
Base value object class.
Value objects are immutable objects defined by their attributes.
"""

from abc import ABC
from typing import Any


class ValueObject(ABC):
    """
    Base value object - immutable.
    Value objects have no identity, they are defined by their attributes.
    """

    def __eq__(self, other: Any) -> bool:
        """
        Compare value objects by attributes.
        Two value objects are equal if all their attributes are equal.
        """
        if not isinstance(other, self.__class__):
            return False
        return self.__dict__ == other.__dict__

    def __hash__(self) -> int:
        """Hash based on all attributes"""
        return hash(tuple(sorted(self.__dict__.items())))

    def __repr__(self) -> str:
        """String representation showing all attributes"""
        attrs = ", ".join(f"{k}={v}" for k, v in self.__dict__.items())
        return f"{self.__class__.__name__}({attrs})"

    def __setattr__(self, key: str, value: Any) -> None:
        """
        Prevent modification after initialization.
        Value objects are immutable.
        """
        if hasattr(self, "_initialized"):
            raise AttributeError(f"Cannot modify immutable value object {self.__class__.__name__}")
        super().__setattr__(key, value)

    def _seal(self) -> None:
        """Mark value object as initialized (immutable)"""
        super().__setattr__("_initialized", True)
