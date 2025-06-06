from flask import Blueprint, request

from app.common.response import created_response, success_response
from app.schema.message import MessageCreateRequest, MessageListRequest
from app.service.message_service import MessageService
from app.util.auth_decorators import login_required

message_bp = Blueprint("message", __name__)


@message_bp.route("/", methods=["GET"])
def get_messages():
    """
    Get All Messages
    ---
    tags:
      - Message
    parameters:
      - name: page_index
        in: query
        type: integer
        default: 1
        description: Page number (1-based)
      - name: page_size
        in: query
        type: integer
        default: 10
        description: Messages per page (1-100)
      - name: search
        in: query
        type: string
        description: Search in message content (minimum 2 characters)
    responses:
      200:
        description: Messages retrieved successfully
        schema:
          type: object
          properties:
            status:
              type: integer
              example: 200
            data:
              type: object
              properties:
                page_index:
                  type: integer
                  example: 1
                page_size:
                  type: integer
                  example: 10
                total:
                  type: integer
                  example: 42
                messages:
                  type: array
                  items:
                    type: object
                    properties:
                      id:
                        type: string
                        example: "msg-uuid-here"
                      content:
                        type: string
                        example: "I hope for world peace and happiness for everyone"
                      author:
                        type: object
                        properties:
                          id:
                            type: string
                          username:
                            type: string
                          email:
                            type: string
                          created_at:
                            type: string
                          updated_at:
                            type: string
                      comments:
                        type: array
                        items:
                          type: object
                      comment_count:
                        type: integer
                        example: 5
                      created_at:
                        type: string
                        format: date-time
                      updated_at:
                        type: string
                        format: date-time
            error:
              type: null
      400:
        description: Invalid query parameters
    """
    message_list_request = MessageListRequest.model_validate(request.args.to_dict())

    messages_response = MessageService.list_messages(
        request=message_list_request,
    )

    return success_response(data=messages_response.model_dump())


@message_bp.route("/<message_id>", methods=["GET"])
def get_message(message_id):
    """
    Get Single Message with Comments
    ---
    tags:
      - Message
    parameters:
      - name: message_id
        in: path
        type: string
        required: true
        description: Message UUID
        example: "msg-uuid-here"
    responses:
      200:
        description: Message retrieved successfully
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
                  example: "msg-uuid-here"
                content:
                  type: string
                  example: "I hope for world peace and happiness for everyone"
                author:
                  type: object
                  properties:
                    id:
                      type: string
                    username:
                      type: string
                    email:
                      type: string
                    created_at:
                      type: string
                    updated_at:
                      type: string
                comments:
                  type: array
                  items:
                    type: object
                    properties:
                      id:
                        type: string
                      content:
                        type: string
                      message_id:
                        type: string
                      author:
                        type: object
                      parent_id:
                        type: string
                        nullable: true
                      replies:
                        type: array
                        items:
                          type: object
                      created_at:
                        type: string
                      updated_at:
                        type: string
                comment_count:
                  type: integer
                  example: 5
                created_at:
                  type: string
                  format: date-time
                updated_at:
                  type: string
                  format: date-time
            error:
              type: null
      404:
        description: Message not found
      409:
        description: Data conflict (message author no longer exists)
    """
    message_response = MessageService.get_message(
        message_id=message_id,
    )

    return success_response(data=message_response.model_dump())


@message_bp.route("/", methods=["POST"])
@login_required
def create_message(current_user):
    """
    Create New Message
    ---
    tags:
      - Message
    parameters:
      - name: body
        in: body
        required: true
        schema:
          type: object
          required:
            - content
          properties:
            content:
              type: string
              minLength: 3
              maxLength: 200
              example: "I hope for world peace and happiness for everyone"
              description: Message content (3-200 characters)
    responses:
      201:
        description: Message created successfully
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
                  example: "msg-uuid-here"
                content:
                  type: string
                  example: "I hope for world peace and happiness for everyone"
                author:
                  type: object
                  properties:
                    id:
                      type: string
                    username:
                      type: string
                    email:
                      type: string
                    created_at:
                      type: string
                    updated_at:
                      type: string
                created_at:
                  type: string
                  format: date-time
                updated_at:
                  type: string
                  format: date-time
            error:
              type: null
      400:
        description: Invalid input (content validation failed)
      401:
        description: Authentication required
      422:
        description: Validation error
    """
    message_request = MessageCreateRequest.model_validate(request.get_json())
    message_response = MessageService.create_message(
        user_id=current_user.id, request=message_request
    )

    return created_response(data=message_response.model_dump())
