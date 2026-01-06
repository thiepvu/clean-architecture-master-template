"""File size value object"""

from shared.domain.value_objects import ValueObject

from ..exceptions.file_exceptions import InvalidFileSizeException


class FileSize(ValueObject):
    """
    File size value object.
    Handles file size with human-readable formatting.
    """

    def __init__(self, bytes_value: int):
        """
        Initialize file size.

        Args:
            bytes_value: File size in bytes

        Raises:
            InvalidFileSizeException: If size is invalid
        """
        if not isinstance(bytes_value, int) or bytes_value < 0:
            raise InvalidFileSizeException(bytes_value)

        self._bytes = bytes_value
        self._seal()

    @property
    def bytes(self) -> int:
        """Get size in bytes"""
        return self._bytes

    @property
    def kilobytes(self) -> float:
        """Get size in kilobytes"""
        return self._bytes / 1024

    @property
    def megabytes(self) -> float:
        """Get size in megabytes"""
        return self._bytes / (1024 * 1024)

    @property
    def gigabytes(self) -> float:
        """Get size in gigabytes"""
        return self._bytes / (1024 * 1024 * 1024)

    def human_readable(self) -> str:
        """
        Get human-readable size string.

        Returns:
            Formatted size (e.g., "1.5 MB")
        """
        if self._bytes < 1024:
            return f"{self._bytes} B"
        elif self._bytes < 1024 * 1024:
            return f"{self.kilobytes:.2f} KB"
        elif self._bytes < 1024 * 1024 * 1024:
            return f"{self.megabytes:.2f} MB"
        else:
            return f"{self.gigabytes:.2f} GB"

    def __str__(self) -> str:
        return self.human_readable()
