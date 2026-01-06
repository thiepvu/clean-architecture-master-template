"""File path value object"""

from pathlib import Path

from shared.domain.value_objects import ValueObject

from ..exceptions.file_exceptions import InvalidFilePathException


class FilePath(ValueObject):
    """
    File path value object.
    Ensures file paths are valid and normalized.
    """

    def __init__(self, value: str):
        """
        Initialize file path.

        Args:
            value: File path string

        Raises:
            InvalidFilePathException: If path is invalid
        """
        if not value or not isinstance(value, str):
            raise InvalidFilePathException(value)

        # Normalize path
        normalized = str(Path(value).as_posix())

        # Security: prevent path traversal
        if ".." in normalized or normalized.startswith("/"):
            raise InvalidFilePathException(value, "Path traversal detected")

        self._value = normalized
        self._seal()

    @property
    def value(self) -> str:
        """Get path value"""
        return self._value

    @property
    def directory(self) -> str:
        """Get directory part of path"""
        return str(Path(self._value).parent)

    @property
    def filename(self) -> str:
        """Get filename part of path"""
        return Path(self._value).name

    def __str__(self) -> str:
        return self._value
