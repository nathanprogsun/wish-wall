"""
User routes.
"""

from flask import Blueprint, current_app, make_response, request

from app.common.response import created_response, success_response
from app.schema.user import (
    UserLoginRequest,
    UserRegisterRequest,
)
from app.service.user_service import UserService
from app.util.auth_decorators import get_current_user, login_required

user_bp = Blueprint("user", __name__)


@user_bp.route("/register", methods=["POST"])
def register():
    """
    User Registration
    ---
    tags:
      - User
    parameters:
      - name: body
        in: body
        required: true
        schema:
          type: object
          required:
            - username
            - email
            - password
          properties:
            username:
              type: string
              minLength: 5
              maxLength: 20
              pattern: "^[a-zA-Z0-9]+$"
              example: "johndoe123"
              description: Username (5-20 characters, letters and numbers only)
            email:
              type: string
              format: email
              example: "john@example.com"
              description: Valid email address
            password:
              type: string
              minLength: 8
              maxLength: 20
              example: "SecurePass123!"
              description: "Password requirements: 8-20 characters, at least one uppercase, one lowercase, one digit, and one special character (!@#$%^&*()_+-=[]{}|;:,.<>?)"
    responses:
      201:
        description: User registered successfully
        schema:
          type: object
          properties:
            status:
              type: integer
              example: 201
            data:
              type: object
              properties:
                id:
                  type: string
                  example: "user-uuid-here"
                username:
                  type: string
                  example: "johndoe123"
                email:
                  type: string
                  example: "john@example.com"
                created_at:
                  type: string
                  format: date-time
                  example: "2025-06-02T12:34:56Z"
                updated_at:
                  type: string
                  format: date-time
                  example: "2025-06-02T12:34:56Z"
            error:
              type: null
      400:
        description: Validation error (username format, password complexity, etc.)
      409:
        description: User already exists (username or email conflict)
      422:
        description: Request validation failed
    """
    register_request = UserRegisterRequest.model_validate(request.get_json())
    user_response = UserService.register(register_request)

    return created_response(data=user_response.model_dump())


@user_bp.route("/login", methods=["POST"])
def login():
    """
    User Login
    ---
    tags:
      - User
    parameters:
      - name: body
        in: body
        required: true
        schema:
          type: object
          required:
            - login
            - password
          properties:
            login:
              type: string
              description: Username or email address
              example: "johndoe123"
            password:
              type: string
              example: "SecurePass123!"
              description: User password
            remember_me:
              type: boolean
              default: false
              description: Remember user for 30 days
              example: false
    responses:
      200:
        description: Login successful
        schema:
          type: object
          properties:
            status:
              type: integer
              example: 200
            data:
              type: object
              properties:
                id:
                  type: string
                  example: "user-uuid-here"
                username:
                  type: string
                  example: "johndoe123"
                email:
                  type: string
                  example: "john@example.com"
                created_at:
                  type: string
                  format: date-time
                  example: "2025-06-02T12:34:56Z"
                updated_at:
                  type: string
                  format: date-time
                  example: "2025-06-02T12:34:56Z"
            error:
              type: null
      400:
        description: Invalid request format
      401:
        description: Invalid credentials (wrong username/email or password)
      422:
        description: Request validation failed
    """
    login_request = UserLoginRequest.model_validate(request.get_json())
    user_response, cookie_response = UserService.login(login_request)

    if cookie_response:
        # If remember me was requested, return response with cookie
        cookie_response.data = success_response(data=user_response.model_dump()).data
        cookie_response.status_code = 200
        cookie_response.headers["Content-Type"] = "application/json"
        return cookie_response
    return success_response(data=user_response.model_dump())


@user_bp.route("/logout", methods=["POST"])
@login_required
def logout(current_user):
    """
    User Logout
    ---
    tags:
      - User
    responses:
      200:
        description: Logout successful
        schema:
          type: object
          properties:
            status:
              type: integer
              example: 200
            data:
              type: object
              properties:
                message:
                  type: string
                  example: "Logout successful"
            error:
              type: null
      401:
        description: Authentication required
    """
    UserService.logout_user()

    # Clear remember me cookie if it exists
    response = make_response(success_response(data={"message": "Logout successful"}))
    response.set_cookie(
        current_app.config.get("REMEMBER_COOKIE_NAME", "remember_token"),
        "",
        expires=0,
        httponly=True,
        samesite=current_app.config.get("REMEMBER_COOKIE_SAMESITE", "Lax"),
        domain=current_app.config.get("REMEMBER_COOKIE_DOMAIN"),
    )

    return response


@user_bp.route("/profile", methods=["GET"])
@login_required
def get_profile(current_user):
    """
    Get Current User Profile
    ---
    tags:
      - User
    responses:
      200:
        description: User profile retrieved successfully
        schema:
          type: object
          properties:
            status:
              type: integer
              example: 200
            data:
              type: object
              properties:
                id:
                  type: string
                  example: "user-uuid-here"
                username:
                  type: string
                  example: "johndoe123"
                email:
                  type: string
                  example: "john@example.com"
                created_at:
                  type: string
                  format: date-time
                  example: "2025-06-02T12:34:56Z"
                updated_at:
                  type: string
                  format: date-time
                  example: "2025-06-02T12:34:56Z"
            error:
              type: null
      401:
        description: Authentication required (invalid or missing token)
      404:
        description: User not found (account may have been deleted)
    """
    from app.schema.user import UserResponse

    user_response = UserResponse.from_model(current_user)

    return success_response(data=user_response.model_dump())
