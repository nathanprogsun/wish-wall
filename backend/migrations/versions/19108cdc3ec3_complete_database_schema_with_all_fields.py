"""Complete database schema with all fields

Revision ID: 19108cdc3ec3
Revises: 
Create Date: 2025-06-02 12:23:12.862862

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '19108cdc3ec3'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Create user table
    op.execute("""
        CREATE TABLE user (
            id VARCHAR(36) PRIMARY KEY,
            username VARCHAR(50) NOT NULL,
            email VARCHAR(120) NOT NULL,
            password_hash VARCHAR(255) NOT NULL,
            created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
            last_login_at TIMESTAMP NULL
        )
    """)
    
    # Add unique constraints and indexes for user table
    op.execute("CREATE UNIQUE INDEX ix_user_username ON user (username)")
    op.execute("CREATE UNIQUE INDEX ix_user_email ON user (email)")
    
    # Create message table
    op.execute("""
        CREATE TABLE message (
            id VARCHAR(36) PRIMARY KEY,
            content TEXT NOT NULL,
            author_id VARCHAR(36) NOT NULL,
            created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (author_id) REFERENCES user(id)
        )
    """)
    
    # Add indexes for message table
    op.execute("CREATE INDEX ix_message_author_id ON message (author_id)")
    op.execute("CREATE INDEX ix_message_created_at ON message (created_at)")
    
    # Create comment table
    op.execute("""
        CREATE TABLE comment (
            id VARCHAR(36) PRIMARY KEY,
            content TEXT NOT NULL,
            author_id VARCHAR(36) NOT NULL,
            message_id VARCHAR(36) NOT NULL,
            parent_id VARCHAR(36) NULL,
            created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
            deleted_at TIMESTAMP NULL,
            FOREIGN KEY (author_id) REFERENCES user(id),
            FOREIGN KEY (message_id) REFERENCES message(id),
            FOREIGN KEY (parent_id) REFERENCES comment(id)
        )
    """)
    
    # Add indexes for comment table
    op.execute("CREATE INDEX ix_comment_author_id ON comment (author_id)")
    op.execute("CREATE INDEX ix_comment_message_id ON comment (message_id)")
    op.execute("CREATE INDEX ix_comment_parent_id ON comment (parent_id)")
    op.execute("CREATE INDEX ix_comment_created_at ON comment (created_at)")


def downgrade() -> None:
    """Downgrade schema."""
    # Drop tables in reverse order due to foreign key constraints
    op.execute("DROP TABLE IF EXISTS comment")
    op.execute("DROP TABLE IF EXISTS message") 
    op.execute("DROP TABLE IF EXISTS user")
