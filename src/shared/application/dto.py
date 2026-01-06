"""Base DTO (Data Transfer Object) classes"""

from pydantic import BaseModel, ConfigDict


class DTO(BaseModel):
    """
    Base Data Transfer Object.
    DTOs are used to transfer data between layers.
    """

    model_config = ConfigDict(
        from_attributes=True,  # Allow creation from ORM models
        validate_assignment=True,  # Validate on assignment
        arbitrary_types_allowed=False,  # Don't allow arbitrary types
        use_enum_values=True,  # Use enum values instead of enum objects
    )
