"""Security configuration type."""

from typing import TypedDict


class SecurityConfigType(TypedDict):
    """Security configuration type."""

    # JWT
    secret_key: str
    algorithm: str
    access_token_expire_minutes: int
    refresh_token_expire_days: int

    # Password
    password_min_length: int
    password_require_uppercase: bool
    password_require_lowercase: bool
    password_require_digit: bool
    password_require_special: bool

    # Security headers
    security_headers_enabled: bool

    # Rate limiting
    rate_limit_enabled: bool
    rate_limit_per_minute: int

    # Session
    session_cookie_name: str
    session_cookie_secure: bool
    session_cookie_httponly: bool
    session_cookie_samesite: str
