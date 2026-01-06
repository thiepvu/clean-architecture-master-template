"""Email value object"""

import re

from shared.domain.value_objects import ValueObject

from ..exceptions.user_exceptions import InvalidEmailException


class Email(ValueObject):
    """
    Email value object.
    Ensures email addresses are always valid.
    """

    # RFC 5322 compliant email regex (simplified)
    EMAIL_REGEX = re.compile(r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$")

    def __init__(self, value: str):
        """
        Initialize email value object.

        Args:
            value: Email address string

        Raises:
            InvalidEmailException: If email format is invalid
        """
        if not self._is_valid(value):
            raise InvalidEmailException(value)

        self._value = value.lower().strip()
        self._seal()  # Make immutable

    @property
    def value(self) -> str:
        """Get email value"""
        return self._value

    @property
    def domain(self) -> str:
        """Get email domain"""
        return self._value.split("@")[1]

    @property
    def local_part(self) -> str:
        """Get email local part (before @)"""
        return self._value.split("@")[0]

    @classmethod
    def _is_valid(cls, value: str) -> bool:
        """
        Validate email format.

        Args:
            value: Email to validate

        Returns:
            True if valid, False otherwise
        """
        if not value or not isinstance(value, str):
            return False

        # Basic length check
        if len(value) > 254:  # RFC 5321
            return False

        # Regex validation
        return bool(cls.EMAIL_REGEX.match(value))

    def __str__(self) -> str:
        """String representation"""
        return self._value
