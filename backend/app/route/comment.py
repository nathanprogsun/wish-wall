"""
Comment routes.
"""

from flask import Blueprint, request

from app.common.response import created_response, success_response
from app.schema.comment import CommentCreateRequest, CommentUpdateRequest
from app.service.comment_service import CommentService
from app.util.auth_decorators import login_required

comment_bp = Blueprint("comment", __name__)


@comment_bp.route("/", methods=["POST"])
@login_required
def create_comment(current_user):
    """
    Create Comment or Reply
    ---
    tags:
      - Comment
    parameters:
      - name: body
        in: body
        required: true
        schema:
          type: object
          required:
            - message_id
            - content
          properties:
            message_id:
              type: string
              example: "msg-uuid-here"
              description: Target message UUID
            parent_id:
              type: string
              description: Parent comment UUID for nested replies (optional)
              example: "comment-uuid-here"
            content:
              type: string
              minLength: 1
              maxLength: 500
              example: "Hope your wish comes true soon!"
              description: Comment content (1-500 characters)
    responses:
      201:
        description: Comment created successfully
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
                  example: "comment-uuid-here"
                content:
                  type: string
                  example: "Hope your wish comes true soon!"
                message_id:
                  type: string
                  example: "msg-uuid-here"
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
                parent_id:
                  type: string
                  nullable: true
                  example: null
                replies:
                  type: array
                  items:
                    type: object
                  example: []
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
      404:
        description: Message or parent comment not found
      422:
        description: Validation error
    """
    comment_request = CommentCreateRequest.model_validate(request.get_json())
    print(comment_request)
    print(current_user)
    comment_response = CommentService.create_comment(
        user_id=current_user.id, request=comment_request
    )

    return created_response(data=comment_response.model_dump())


@comment_bp.route("/<comment_id>", methods=["PUT"])
@login_required
def update_comment(current_user, comment_id):
    """
    Update Comment Content
    ---
    tags:
      - Comment
    parameters:
      - name: comment_id
        in: path
        type: string
        required: true
        description: Comment UUID
        example: "comment-uuid-here"
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
              minLength: 1
              maxLength: 500
              example: "Updated wish content"
              description: Updated comment content (1-500 characters)
    responses:
      200:
        description: Comment updated successfully
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
                  example: "comment-uuid-here"
                content:
                  type: string
                  example: "Updated wish content"
                message_id:
                  type: string
                  example: "msg-uuid-here"
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
                parent_id:
                  type: string
                  nullable: true
                replies:
                  type: array
                  items:
                    type: object
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
      403:
        description: Not authorized to update this comment (not the author)
      404:
        description: Comment not found
      422:
        description: Validation error
    """
    comment_request = CommentUpdateRequest.model_validate(request.get_json())
    comment_response = CommentService.update_comment(
        comment_id=comment_id, user_id=current_user.id, request=comment_request
    )

    return success_response(data=comment_response.model_dump())


@comment_bp.route("/<comment_id>", methods=["DELETE"])
@login_required
def delete_comment(current_user, comment_id):
    """
    Delete Comment
    ---
    tags:
      - Comment
    parameters:
      - name: comment_id
        in: path
        type: string
        required: true
        description: Comment UUID
        example: "comment-uuid-here"
    responses:
      200:
        description: Comment deleted successfully
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
                  example: "Comment deleted successfully"
            error:
              type: null
      401:
        description: Authentication required
      403:
        description: Not authorized to delete this comment (not the author)
      404:
        description: Comment not found
    """
    CommentService.delete_comment(comment_id=comment_id, user_id=current_user.id)

    return success_response(data={"message": "Comment deleted successfully"})
