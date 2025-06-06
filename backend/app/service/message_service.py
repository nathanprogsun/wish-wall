from sqlalchemy import asc, desc, text

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
        """Create a new message with proper transaction management."""
        with get_db_session() as session:
            # Verify user exists
            user = session.query(User).filter(User.id == user_id).first()
            if not user:
                raise NotFoundException("User not found")

            # Create message directly in this session instead of using Message.create_message
            message = Message(
                content=request.content,
                author_id=user_id,
            )
            session.add(message)
            session.flush()  # Get the message ID
            
            # Create response objects while both user and message are attached to session
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
        """Get a single message with its comments tree."""
        with get_db_session() as session:
            message = session.query(Message).filter(Message.id == message_id).first()
            if not message:
                raise NotFoundException("Message not found")

            author = session.query(User).filter(User.id == message.author_id).first()
            if not author:
                raise ConflictException("The author of the message does not exist")

            author_data = UserResponse.from_model(author)
            
            # Use optimized recursive SQL query for comments tree
            comments = MessageService.get_comments_tree_optimized(session, message.id)
            comment_count = len(comments)

            return MessageResponse(
                id=message.id,
                content=message.content,
                author=author_data,
                comments=comments,
                comment_count=comment_count,
                created_at=message.created_at,
                updated_at=message.updated_at,
            )

    @staticmethod
    def list_messages(request: MessageListRequest) -> MessageListResponse:
        """List messages with pagination and filtering."""
        with get_db_session() as session:
            # Build query
            query = session.query(Message).filter()
            
            # Apply filters
            if request.search:
                search_pattern = f"%{request.search}%"
                query = query.filter(Message.content.ilike(search_pattern))

            # Get total count before pagination
            total = query.count()

            # Apply sorting
            query = query.order_by(desc(Message.created_at))

            # Apply pagination
            offset = (request.page_index - 1) * request.page_size
            messages = query.offset(offset).limit(request.page_size).all()

            # Convert to response format
            message_list = []
            for message in messages:
                author = session.query(User).filter(User.id == message.author_id).first()
                if not author:
                    raise ConflictException("The author of the message does not exist")
                    
                author_data = UserResponse.from_model(author)
                
                # Use optimized recursive SQL query for comments tree
                comments = MessageService.get_comments_tree_optimized(session, message.id)

                message_list.append(
                    MessageResponse(
                        id=message.id,
                        content=message.content,
                        author=author_data,
                        comments=comments,
                        comment_count=len(comments),
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
    def get_comments_tree_optimized(session, message_id: str) -> list[CommentResponse]:
        """
        Optimized comments tree using recursive SQL query.
        Avoids N+1 problem by using database-level recursive CTE.
        
        Args:
            session: Database session
            message_id: Message ID to get comments for
            
        Returns:
            List of root CommentResponse objects with nested replies
        """
        # MySQL recursive CTE query to get the full comment tree in one query
        recursive_sql = text("""
            WITH RECURSIVE comment_tree AS (
                -- Base case: Root comments (no parent)
                SELECT 
                    c.id,
                    c.content,
                    c.author_id,
                    c.parent_id,
                    c.message_id,
                    c.created_at,
                    c.updated_at,
                    0 as level,
                    CAST(c.id AS CHAR(1000)) as path
                FROM comment c
                WHERE c.message_id = :message_id 
                AND c.parent_id IS NULL
                
                UNION ALL
                
                -- Recursive case: Child comments
                SELECT 
                    c.id,
                    c.content,
                    c.author_id,
                    c.parent_id,
                    c.message_id,
                    c.created_at,
                    c.updated_at,
                    ct.level + 1,
                    CONCAT(ct.path, '/', c.id) as path
                FROM comment c
                INNER JOIN comment_tree ct ON c.parent_id = ct.id
                WHERE c.message_id = :message_id
                AND ct.level < 10  -- Prevent infinite recursion, max 10 levels
            )
            SELECT 
                ct.*,
                u.id as user_id,
                u.username as user_username,
                u.email as user_email,
                u.created_at as user_created_at
            FROM comment_tree ct
            LEFT JOIN user u ON ct.author_id = u.id
            ORDER BY ct.level, ct.created_at ASC
        """)
        
        # Execute the recursive query
        result = session.execute(recursive_sql, {"message_id": message_id})
        rows = result.fetchall()
        
        if not rows:
            return []
        
        # Build the tree structure from the flat result
        return MessageService._build_tree_from_flat_data(rows)

    @staticmethod
    def _build_tree_from_flat_data(rows) -> list[CommentResponse]:
        """
        Build tree structure from flat recursive query result.
        
        Args:
            rows: Result rows from recursive SQL query
            
        Returns:
            List of root CommentResponse objects with nested replies
        """
        # Create dictionaries to store comments and their children
        comments_dict = {}
        children_map = {}
        
        # First pass: Create all comment objects
        for row in rows:
            # Create user object from row data
            user_data = UserResponse(
                id=row.user_id,
                username=row.user_username,
                email=row.user_email,
                created_at=row.user_created_at,
                updated_at=row.user_created_at,  # Use created_at as fallback for updated_at
            )
            
            # Create comment response object
            comment_response = CommentResponse(
                id=row.id,
                content=row.content,
                message_id=row.message_id,
                author=user_data,
                parent_id=row.parent_id,
                replies=[],  # Will be populated in second pass
                created_at=row.created_at,
                updated_at=row.updated_at,
            )
            
            comments_dict[row.id] = comment_response
            
            # Track parent-child relationships
            parent_id = row.parent_id or "root"
            if parent_id not in children_map:
                children_map[parent_id] = []
            children_map[parent_id].append(row.id)
        
        # Second pass: Build parent-child relationships
        def attach_children(comment_id: str):
            """Recursively attach children to their parent comments."""
            if comment_id in children_map:
                child_ids = children_map[comment_id]
                for child_id in child_ids:
                    child_comment = comments_dict[child_id]
                    if comment_id == "root":
                        # This is a root comment, will be added to result later
                        pass
                    else:
                        # Add child to parent's replies
                        parent_comment = comments_dict[comment_id]
                        parent_comment.replies.append(child_comment)
                    
                    # Recursively attach this child's children
                    attach_children(child_id)
        
        # Start from root
        attach_children("root")
        
        # Get root comments (those with no parent)
        root_comments = []
        if "root" in children_map:
            for root_comment_id in children_map["root"]:
                root_comments.append(comments_dict[root_comment_id])
        
        # Sort root comments by creation time (newest first)
        root_comments.sort(key=lambda x: x.created_at, reverse=True)
        
        return root_comments

    @staticmethod
    def to_comments_tree(
        db_comments: list[Comment], user_map: dict[str, User]
    ) -> list[CommentResponse]:
        """
        Legacy method - Convert flat list of comments into hierarchical tree structure.
        
        Note: This method is kept for backwards compatibility.
        Use get_comments_tree_optimized() for better performance.

        Args:
            db_comments: Flat list of Comment models
            user_map: Dictionary mapping user IDs to User models

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
