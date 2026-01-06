"""User-specific domain exceptions"""

from shared.errors.exceptions import DomainException


class InvalidEmailException(DomainException):
    """Invalid email exception"""

    def __init__(self, email: str):
        super().__init__(message=f"Invalid email format: {email}", details={"email": email})


class UserAlreadyExistsException(DomainException):
    """User already exists exception"""

    def __init__(self, identifier: str, field: str = "email"):
        super().__init__(
            message=f"User with {field} '{identifier}' already exists",
            details={"identifier": identifier, "field": field},
        )


class InvalidUserStateException(DomainException):
    """Invalid user state exception"""

    def __init__(self, message: str):
        super().__init__(message=message, details={})
