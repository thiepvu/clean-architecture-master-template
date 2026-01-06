"""Test Email value object"""

import pytest

from contexts.user_management.domain.exceptions.user_exceptions import InvalidEmailException
from contexts.user_management.domain.value_objects.email import Email


class TestEmailValueObject:
    """Test Email value object"""

    def test_valid_email(self):
        """Test creating valid email"""
        email = Email("test@example.com")

        assert email.value == "test@example.com"
        assert email.domain == "example.com"
        assert email.local_part == "test"

    def test_email_lowercase_conversion(self):
        """Test email is converted to lowercase"""
        email = Email("Test@EXAMPLE.COM")

        assert email.value == "test@example.com"

    def test_email_strip_whitespace(self):
        """Test email whitespace is stripped"""
        email = Email("  test@example.com  ")

        assert email.value == "test@example.com"

    @pytest.mark.parametrize(
        "invalid_email",
        [
            "invalid",
            "invalid@",
            "@example.com",
            "invalid@.com",
            "invalid@example",
            "",
            "a" * 255 + "@example.com",  # Too long
        ],
    )
    def test_invalid_email(self, invalid_email):
        """Test invalid email formats raise exception"""
        with pytest.raises(InvalidEmailException):
            Email(invalid_email)

    def test_email_equality(self):
        """Test email value objects are equal if values match"""
        email1 = Email("test@example.com")
        email2 = Email("test@example.com")

        assert email1 == email2

    def test_email_immutability(self):
        """Test email cannot be modified"""
        email = Email("test@example.com")

        with pytest.raises(AttributeError):
            email._value = "modified@example.com"

    def test_email_string_representation(self):
        """Test email string representation"""
        email = Email("test@example.com")

        assert str(email) == "test@example.com"
