import pytest
from app.security.password import hash_password, verify_password
from app.security.jwt import create_access_token, verify_access_token, create_refresh_token


def test_password_hash_and_verify():
    password = "MySecret@123"
    hashed = hash_password(password)
    assert hashed != password
    assert verify_password(password, hashed) is True
    assert verify_password("WrongPassword", hashed) is False


def test_access_token_creation_and_verification():
    token = create_access_token("user-id-123", "ADMIN")
    payload = verify_access_token(token)
    assert payload["sub"] == "user-id-123"
    assert payload["role"] == "ADMIN"
    assert payload["type"] == "access"


def test_refresh_token_type():
    from app.security.jwt import verify_refresh_token
    token = create_refresh_token("user-id-456")
    payload = verify_refresh_token(token)
    assert payload["sub"] == "user-id-456"
    assert payload["type"] == "refresh"


def test_invalid_token_raises():
    from app.core.exceptions import UnauthorizedException
    with pytest.raises(UnauthorizedException):
        verify_access_token("not.a.valid.token")
