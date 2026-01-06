"""MIME type value object"""

from shared.domain.value_objects import ValueObject

from ..exceptions.file_exceptions import InvalidMimeTypeException


class MimeType(ValueObject):
    """
    MIME type value object.
    Validates and categorizes file MIME types.
    """

    def __init__(self, value: str):
        """
        Initialize MIME type.

        Args:
            value: MIME type string

        Raises:
            InvalidMimeTypeException: If MIME type is invalid
        """
        if not value or "/" not in value:
            raise InvalidMimeTypeException(value)

        self._value = value.lower().strip()
        self._seal()

    @property
    def value(self) -> str:
        """Get MIME type value"""
        return self._value

    @property
    def category(self) -> str:
        """Get MIME type category (e.g., 'image', 'application')"""
        return self._value.split("/")[0]

    @property
    def subtype(self) -> str:
        """Get MIME type subtype (e.g., 'jpeg', 'pdf')"""
        return self._value.split("/")[1]

    def is_image(self) -> bool:
        """Check if MIME type is an image"""
        return self.category == "image"

    def is_video(self) -> bool:
        """Check if MIME type is a video"""
        return self.category == "video"

    def is_audio(self) -> bool:
        """Check if MIME type is audio"""
        return self.category == "audio"

    def is_text(self) -> bool:
        """Check if MIME type is text"""
        return self.category == "text"

    def __str__(self) -> str:
        return self._value
