"""
Security and authentication configuration
"""

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings

from config.types import SecurityConfigType


class SecurityConfig(BaseSettings):
    """Security and JWT configuration settings"""

    # JWT settings
    SECRET_KEY: str = Field(
        default="change-this-secret-key-in-production-please",
        description="Secret key for JWT encoding (CHANGE IN PRODUCTION!)",
        min_length=32,
    )
    ALGORITHM: str = Field(default="HS256", description="JWT signing algorithm")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(
        default=30, ge=1, description="Access token expiration in minutes"
    )
    REFRESH_TOKEN_EXPIRE_DAYS: int = Field(
        default=7, ge=1, description="Refresh token expiration in days"
    )

    # Password settings
    PASSWORD_MIN_LENGTH: int = Field(default=8, ge=6, description="Minimum password length")
    PASSWORD_REQUIRE_UPPERCASE: bool = Field(
        default=True, description="Require uppercase letters in password"
    )
    PASSWORD_REQUIRE_LOWERCASE: bool = Field(
        default=True, description="Require lowercase letters in password"
    )
    PASSWORD_REQUIRE_DIGIT: bool = Field(default=True, description="Require digits in password")
    PASSWORD_REQUIRE_SPECIAL: bool = Field(
        default=True, description="Require special characters in password"
    )

    # Security headers
    SECURITY_HEADERS_ENABLED: bool = Field(default=True, description="Enable security headers")

    # Rate limiting
    RATE_LIMIT_ENABLED: bool = Field(default=True, description="Enable rate limiting")
    RATE_LIMIT_PER_MINUTE: int = Field(default=60, ge=1, description="Requests per minute per IP")

    # Session settings
    SESSION_COOKIE_NAME: str = Field(default="session", description="Session cookie name")
    SESSION_COOKIE_SECURE: bool = Field(default=True, description="Use secure cookies (HTTPS only)")
    SESSION_COOKIE_HTTPONLY: bool = Field(default=True, description="HTTP-only cookies")
    SESSION_COOKIE_SAMESITE: str = Field(default="lax", description="SameSite cookie policy")

    @field_validator("SECRET_KEY")
    @classmethod
    def validate_secret_key(cls, v: str) -> str:
        """Validate secret key"""
        if v == "change-this-secret-key-in-production-please":
            import warnings

            warnings.warn("Using default SECRET_KEY! Change this in production!", UserWarning)
        if len(v) < 32:
            raise ValueError("SECRET_KEY must be at least 32 characters long")
        return v

    @field_validator("ALGORITHM")
    @classmethod
    def validate_algorithm(cls, v: str) -> str:
        """Validate JWT algorithm"""
        allowed = ["HS256", "HS384", "HS512", "RS256", "RS384", "RS512"]
        if v not in allowed:
            raise ValueError(f"ALGORITHM must be one of {allowed}")
        return v

    def to_dict(self) -> SecurityConfigType:
        """Convert to typed dictionary format."""
        return SecurityConfigType(
            secret_key=self.SECRET_KEY,
            algorithm=self.ALGORITHM,
            access_token_expire_minutes=self.ACCESS_TOKEN_EXPIRE_MINUTES,
            refresh_token_expire_days=self.REFRESH_TOKEN_EXPIRE_DAYS,
            password_min_length=self.PASSWORD_MIN_LENGTH,
            password_require_uppercase=self.PASSWORD_REQUIRE_UPPERCASE,
            password_require_lowercase=self.PASSWORD_REQUIRE_LOWERCASE,
            password_require_digit=self.PASSWORD_REQUIRE_DIGIT,
            password_require_special=self.PASSWORD_REQUIRE_SPECIAL,
            security_headers_enabled=self.SECURITY_HEADERS_ENABLED,
            rate_limit_enabled=self.RATE_LIMIT_ENABLED,
            rate_limit_per_minute=self.RATE_LIMIT_PER_MINUTE,
            session_cookie_name=self.SESSION_COOKIE_NAME,
            session_cookie_secure=self.SESSION_COOKIE_SECURE,
            session_cookie_httponly=self.SESSION_COOKIE_HTTPONLY,
            session_cookie_samesite=self.SESSION_COOKIE_SAMESITE,
        )
