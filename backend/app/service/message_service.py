from sqlalchemy import asc, desc

from app.common.database import get_db_session
from app.common.exception import (
    ConflictException,
    NotFoundException,
)
from app.model.comment import Comment
from app.model.message import Message
from app.model.user import User
from app.schema.comment import CommentResponse
from app.schema.message import (
    MessageCreateRequest,
    MessageListRequest,
    MessageListResponse,
    MessageResponse,
)
from app.schema.user import UserResponse


class MessageService:
    @staticmethod
    def create_message(user_id: str, request: MessageCreateRequest) -> MessageResponse:
        db_session = get_db_session()
        # Verify user exists
        user = db_session.query(User).filter(User.id == user_id).first()
        if not user:
            raise NotFoundException("User not found")

        message = Message.create_message(
            content=request.content,
            author_id=user_id,
        )
        author_data = UserResponse.from_model(user)
        return MessageResponse(
            id=message.id,
            content=message.content,
            author=author_data,
            created_at=message.created_at,
            updated_at=message.updated_at,
        )

    @staticmethod
    def get_message(message_id: str) -> MessageResponse:
        db_session = get_db_session()
        message = (
            db_session.query(Message)
            .filter(
                Message.id == message_id,
            )
            .first()
        )
        if not message:
            raise NotFoundException("Message not found")

        author = db_session.query(User).filter(User.id == message.author_id).first()
        if not author:
            raise ConflictException("The author of the message does not exist")

        author_data = UserResponse.from_model(author)
        db_comments = Comment.find_all_comments_by_message_id(message.id)

        users = (
            db_session.query(User)
            .filter(User.id.in_(list({comment.author_id for comment in db_comments})))
            .all()
        )
        user_map = {user.id: user for user in users}
        comments = MessageService.to_comments_tree(db_comments, user_map)

        return MessageResponse(
            id=message.id,
            content=message.content,
            author=author_data,
            comments=comments,
            comment_count=len(db_comments),
            created_at=message.created_at,
            updated_at=message.updated_at,
        )

    @staticmethod
    def list_messages(request: MessageListRequest) -> MessageListResponse:
        db_session = get_db_session()

        # Build query
        query = db_session.query(Message).filter()
        # Apply filters
        if request.search:
            search_pattern = f"%{request.search}%"
            query = query.filter(Message.content.ilike(search_pattern))

        # Get total count
        total = query.count()

        # Apply sorting
        query = query.order_by(desc(Message.created_at))

        # Apply pagination
        offset = (request.page_index - 1) * request.page_size
        messages = query.offset(offset).limit(request.page_size).all()

        # Convert to response format
        message_list = []
        for message in messages:
            author = db_session.query(User).filter(User.id == message.author_id).first()
            if not author:
                raise ConflictException("The author of the message does not exist")
            author_data = UserResponse.from_model(author)
            db_comments = Comment.find_all_comments_by_message_id(message.id)

            users = (
                db_session.query(User)
                .filter(
                    User.id.in_(list({comment.author_id for comment in db_comments}))
                )
                .all()
            )
            user_map = {user.id: user for user in users}
            comments = MessageService.to_comments_tree(db_comments, user_map)

            message_list.append(
                MessageResponse(
                    id=message.id,
                    content=message.content,
                    author=author_data,
                    comments=comments,
                    comment_count=len(db_comments),
                    created_at=message.created_at,
                    updated_at=message.updated_at,
                )
            )

        return MessageListResponse(
            page_index=request.page_index,
            page_size=request.page_size,
            total=total,
            messages=message_list,
        )

    @staticmethod
    def to_comments_tree(
        db_comments: list[Comment], user_map: dict[str, User]
    ) -> list[CommentResponse]:
        """
        Convert flat list of comments into hierarchical tree structure.

        Args:
            db_comments: Flat list of Comment models

        Returns:
            List of root CommentResponse objects with nested replies
        """
        if not db_comments:
            return []
        root_id = "root"
        # Create mapping of parent_id -> list of children
        children_map: dict[str, list[Comment]] = {}

        for comment in db_comments:
            parent_id = comment.parent_id or root_id
            if parent_id not in children_map:
                children_map[parent_id] = []
            children_map[parent_id].append(comment)

        def build_comment_with_replies(comment: Comment) -> CommentResponse:
            """Recursively build comment with its replies."""
            # Get children for this comment
            child_comments = children_map.get(comment.id, [])

            # Sort children by creation time (oldest first for conversation flow)
            child_comments.sort(key=lambda x: x.created_at)

            # Recursively build replies
            replies = [build_comment_with_replies(child) for child in child_comments]
            user = user_map.get(comment.author_id)
            if not user:
                raise ConflictException("The author of the comment does not exist")
            # Create CommentResponse with replies
            return CommentResponse.from_model(comment, user, replies)

        # Get root comments (no parent)
        root_comments = children_map.get(root_id, [])

        # Sort root comments by creation time (newest first)
        root_comments.sort(key=lambda x: x.created_at, reverse=True)

        # Build tree structure
        return [build_comment_with_replies(comment) for comment in root_comments]
