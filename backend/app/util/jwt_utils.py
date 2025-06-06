"""
JWT utilities for token generation and validation.
"""

import jwt
from datetime import datetime, timedelta, timezone
from typing import Dict, Any, Optional
from flask import current_app

from app.common.logger import get_logger

logger = get_logger(__name__)


class JWTTokenType:
    """Token type constants."""
    ACCESS = "access"
    REMEMBER = "remember"
    REFRESH = "refresh"


def generate_token(user_id: str, token_type: str = JWTTokenType.ACCESS, remember_me: bool = False) -> str:
    """
    Generate JWT token for user.
    
    Args:
        user_id: User ID
        token_type: Type of token (access, remember, refresh)
        remember_me: If True, use remember token expiration time
        
    Returns:
        JWT token string
    """
    now = datetime.now(timezone.utc)
    
    # Determine expiration time based on token type and remember_me flag
    if token_type == JWTTokenType.REMEMBER or remember_me:
        expires_delta = current_app.config["JWT_REMEMBER_TOKEN_EXPIRES"]
    elif token_type == JWTTokenType.REFRESH:
        expires_delta = current_app.config["JWT_REFRESH_TOKEN_EXPIRES"]
    else:  # ACCESS token
        expires_delta = current_app.config["JWT_ACCESS_TOKEN_EXPIRES"]
    
    payload = {
        "user_id": user_id,
        "token_type": token_type,
        "iat": now,
        "exp": now + expires_delta,
        "remember_me": remember_me
    }
    
    token = jwt.encode(
        payload,
        current_app.config["JWT_SECRET_KEY"],
        algorithm=current_app.config["JWT_ALGORITHM"]
    )
    
    logger.debug(f"Generated {token_type} token for user {user_id}, remember_me: {remember_me}")
    return token


def generate_access_token(user_id: str, remember_me: bool = False) -> str:
    """Generate access token for user."""
    return generate_token(user_id, JWTTokenType.ACCESS, remember_me)


def generate_remember_token(user_id: str) -> str:
    """Generate remember me token for user."""
    return generate_token(user_id, JWTTokenType.REMEMBER, remember_me=True)


def generate_refresh_token(user_id: str) -> str:
    """Generate refresh token for user."""
    return generate_token(user_id, JWTTokenType.REFRESH)


def decode_token(token: str) -> Optional[Dict[str, Any]]:
    """
    Decode and validate JWT token.
    
    Args:
        token: JWT token string
        
    Returns:
        Decoded payload if valid, None otherwise
    """
    try:
        payload = jwt.decode(
            token,
            current_app.config["JWT_SECRET_KEY"],
            algorithms=[current_app.config["JWT_ALGORITHM"]]
        )
        return payload
    except jwt.ExpiredSignatureError:
        logger.warning("Token has expired")
        return None
    except jwt.InvalidTokenError as e:
        logger.warning(f"Invalid token: {e}")
        return None


def validate_token(token: str, expected_type: Optional[str] = None) -> Optional[str]:
    """
    Validate JWT token and return user ID if valid.
    
    Args:
        token: JWT token string
        expected_type: Expected token type (optional)
        
    Returns:
        User ID if valid, None otherwise
    """
    payload = decode_token(token)
    if not payload:
        return None
    
    user_id = payload.get("user_id")
    token_type = payload.get("token_type")
    
    # Check token type if specified
    if expected_type and token_type != expected_type:
        logger.warning(f"Token type mismatch: expected {expected_type}, got {token_type}")
        return None
    
    if not isinstance(user_id, str):
        logger.warning("Invalid user_id in token")
        return None
    
    return user_id


def validate_access_token(token: str) -> Optional[str]:
    """Validate access token and return user ID if valid."""
    return validate_token(token, JWTTokenType.ACCESS)


def validate_remember_token(token: str) -> Optional[str]:
    """Validate remember me token and return user ID if valid."""
    return validate_token(token, JWTTokenType.REMEMBER)


def validate_refresh_token(token: str) -> Optional[str]:
    """Validate refresh token and return user ID if valid."""
    return validate_token(token, JWTTokenType.REFRESH)


def extract_token_from_header(auth_header: Optional[str]) -> Optional[str]:
    """
    Extract JWT token from Authorization header.
    
    Args:
        auth_header: Authorization header value
        
    Returns:
        Token string if valid format, None otherwise
    """
    if not auth_header:
        return None
    
    # Expected format: "Bearer <token>"
    parts = auth_header.split()
    if len(parts) != 2 or parts[0].lower() != "bearer":
        return None
    
    return parts[1]


def get_token_expiry_info(token: str) -> Optional[Dict[str, Any]]:
    """
    Get token expiry information.
    
    Args:
        token: JWT token string
        
    Returns:
        Dictionary with expiry info if valid, None otherwise
    """
    payload = decode_token(token)
    if not payload:
        return None
    
    exp_timestamp = payload.get("exp")
    iat_timestamp = payload.get("iat")
    
    if not exp_timestamp:
        return None
    
    exp_datetime = datetime.fromtimestamp(exp_timestamp, timezone.utc)
    iat_datetime = datetime.fromtimestamp(iat_timestamp, timezone.utc) if iat_timestamp else None
    now = datetime.now(timezone.utc)
    
    return {
        "expires_at": exp_datetime,
        "issued_at": iat_datetime,
        "is_expired": exp_datetime < now,
        "time_until_expiry": exp_datetime - now if exp_datetime > now else timedelta(0),
        "token_type": payload.get("token_type"),
        "remember_me": payload.get("remember_me", False)
    } 