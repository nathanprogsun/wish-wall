#!/usr/bin/env python3
"""
Wish Wall Seed Script

Seed script to populate the database with wish wall sample data.
Creates users, wishes (messages), and deeply nested comments for testing.

Features:
- Creates sample users
- Creates various wishes (wealth, love, travel, education, health)
- Creates deeply nested comments (up to 20 levels)
- Creates regular supportive comments
- Includes emoji and warm interactions
"""

import os
import sys
import time
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from app.common.database import Base, get_engine, init_database
from app.common.logger import get_logger
from app.model.comment import Comment
from app.model.message import Message
from app.model.user import User
from app.settings import settings

logger = get_logger(__name__)


def init_db():
    """Initialize database connection and ensure migrations are up to date."""
    # Initialize database connection
    from app.common.database import init_database
    init_database()
    
    # Run Alembic upgrade to ensure database is up to date
    import subprocess
    
    try:
        logger.info("🔧 Running Alembic upgrade to ensure database is up to date...")
        result = subprocess.run(
            ["alembic", "upgrade", "head"],
            cwd=project_root,
            capture_output=True,
            text=True,
            check=True
        )
        if result.stdout:
            logger.debug(result.stdout.strip())
        logger.info("✅ Database schema is up to date")
        
    except subprocess.CalledProcessError as e:
        logger.error(f"❌ Failed to upgrade database: {e}")
        if e.stdout:
            logger.error(f"STDOUT: {e.stdout}")
        if e.stderr:
            logger.error(f"STDERR: {e.stderr}")
        raise RuntimeError("Database migration failed")
    except FileNotFoundError:
        logger.error("❌ Alembic not found. Please install alembic or check your environment.")
        raise


def create_sample_users():
    """Create sample users."""
    logger.info("👥 Creating sample users...")

    users_data = [
        {"username": "admin", "email": "admin@example.com", "password": "Admin123!"},
        {"username": "alice", "email": "alice@example.com", "password": "Alice123!"},
        {"username": "bob", "email": "bob@example.com", "password": "Bob123!"},
        {"username": "charlie", "email": "charlie@example.com", "password": "Charlie123!"},
        {"username": "diana", "email": "diana@example.com", "password": "Diana123!"},
    ]

    users = []
    from app.common.database import get_db_session

    with get_db_session() as db_session:
        for user_data in users_data:
            try:
                # Check if user already exists
                existing_user = (
                    db_session.query(User)
                    .filter(User.username == user_data["username"])
                    .first()
                )
                
                if existing_user:
                    users.append(existing_user)
                    logger.info(f"  ⚠️  User {user_data['username']} already exists, using existing user")
                else:
                    # Create new user using the User constructor
                    user = User(
                        username=user_data["username"],
                        email=user_data["email"],
                        password=user_data["password"]
                    )
                    db_session.add(user)
                    db_session.flush()  # Get the ID
                    users.append(user)
                    logger.info(f"  ✅ Created user: {user.username}")
                    
            except Exception as e:
                logger.error(f"  ❌ Failed to create user {user_data['username']}: {e}")
                # Try to find existing user as fallback
                existing_user = (
                    db_session.query(User)
                    .filter(User.username == user_data["username"])
                    .first()
                )
                if existing_user:
                    users.append(existing_user)
                    logger.info(f"  🔄 Using existing user: {user_data['username']}")

    logger.info(f"✅ Created/found {len(users)} users")
    return users


def create_sample_messages(users):
    """Create sample messages."""
    logger.info("🌟 Creating sample wishes...")

    messages_data = [
        {
            "content": "🏆 I wish to achieve financial success! Hope my investments do well this year! 💰💰💰",
            "author": users[0],  # admin
        },
        {
            "content": "💕 I wish to find a kind and loving partner, hoping to meet the right person soon!",
            "author": users[1],  # alice
        },
        {
            "content": "✈️ I want to travel around the world! Especially to see cherry blossoms in Japan, mountains in Switzerland, and beaches in Maldives!",
            "author": users[2],  # bob
        },
        {
            "content": "📚 I hope to pass my exams and get accepted to my dream university! Academic success!",
            "author": users[3],  # charlie
        },
        {
            "content": "🌈 I wish for my family's health and happiness, and for everyone to have a smooth career!",
            "author": users[4],  # diana
        },
    ]

    messages = []
    from app.common.database import get_db_session

    with get_db_session() as db_session:
        for msg_data in messages_data:
            try:
                message = Message(
                    content=msg_data["content"], 
                    author_id=msg_data["author"].id
                )
                db_session.add(message)
                db_session.flush()  # Get the ID
                messages.append(message)
                logger.info(
                    f"  ✨ Created wish by {msg_data['author'].username}: '{message.content[:50]}...'"
                )
            except Exception as e:
                logger.error(f"  ❌ Failed to create message: {e}")

    logger.info(f"🌟 Created {len(messages)} wishes")
    return messages


def create_deep_nested_comments_in_session(db_session, message, users, max_depth=20):
    """Create deeply nested comments (20 levels) for a message within an existing session."""
    logger.info(
        f"💬 Creating 20-level nested comments for wish: '{message.content[:50]}...'"
    )

    comment_templates = [
        "Good luck! {topic} will definitely come true! 💪",
        "I have the same wish! {topic} is so important!",
        "Blessings for your {topic} dream to come true! 🙏",
        "Wow, {topic} sounds amazing!",
        "I think {topic} requires this kind of effort...",
        "Support! {topic} is many people's dream",
        "Thinking about {topic} makes me excited!",
        "About {topic}, I want to share some experience...",
        "Your {topic} wish really touches me",
        "I'm also working towards {topic}!",
        "Hope we can all achieve {topic}!",
        "Thumbs up for {topic}! 👍",
        "Believe {topic} will definitely succeed!",
        "Keep going! {topic} is worth having!",
        "My friend also has a {topic} wish",
        "About {topic}, I have a suggestion...",
        "Sincere blessings for {topic} to come true soon!",
        "Your {topic} idea is great!",
        "Let's work together for {topic}!",
        "May all the beauty of {topic} come to you ✨",
    ]

    # Extract wish topic from message content
    if "financial" in message.content.lower() or "money" in message.content.lower():
        topic = "wealth"
    elif "partner" in message.content.lower() or "love" in message.content.lower():
        topic = "love"
    elif "travel" in message.content.lower() or "world" in message.content.lower():
        topic = "travel"
    elif "exam" in message.content.lower() or "university" in message.content.lower():
        topic = "education"
    elif "health" in message.content.lower():
        topic = "health"
    else:
        topic = "wish"

    # Create root comments
    root_comments = []
    for i in range(3):  # 3 root comments
        user = users[i % len(users)]
        content = comment_templates[i].format(topic=topic)

        comment = Comment(
            content=content, 
            author_id=user.id, 
            message_id=message.id
        )
        db_session.add(comment)
        db_session.flush()  # Get the ID
        root_comments.append(comment)
        logger.info(f"  📌 Root comment {i + 1}: '{content[:40]}...'")

    # Create deep nesting under the first root comment
    current_parent = root_comments[0]
    nested_comments = [current_parent]

    logger.info(f"  🔗 Creating {max_depth} levels of nesting...")
    start_time = time.time()

    for level in range(1, max_depth + 1):
        user = users[level % len(users)]
        content = comment_templates[level % len(comment_templates)].format(topic=topic)
        content += f" (Level {level})"

        nested_comment = Comment(
            content=content,
            author_id=user.id,
            message_id=message.id,
            parent_id=current_parent.id,
        )
        db_session.add(nested_comment)
        db_session.flush()  # Get the ID
        nested_comments.append(nested_comment)
        current_parent = nested_comment

        if level % 5 == 0:
            logger.info(f"    └── Level {level}: '{content[:30]}...'")

    nesting_time = time.time() - start_time
    logger.info(f"  ✅ Deep nesting completed in {nesting_time:.3f} seconds")

    # Create some branching comments
    logger.info("  🌿 Creating branching comments...")

    # Branch from level 5
    if len(nested_comments) > 5:
        parent_for_branch = nested_comments[5]
        branch_comments = [
            f"I think achieving {topic} also requires this approach...",
            f"About {topic}, I have a different perspective!",
        ]
        for i in range(2):  # 2 branches
            user = users[(i + 2) % len(users)]
            content = branch_comments[i]

            branch_comment = Comment(
                content=content,
                author_id=user.id,
                message_id=message.id,
                parent_id=parent_for_branch.id,
            )
            db_session.add(branch_comment)
            logger.info(f"    🌿 Branch {i + 1}: '{content}'")

    # Add some replies to other root comments
    root_replies = [f"I also want {topic}! Let's work together!", f"{topic} is really great, I support you!"]
    for i, root in enumerate(root_comments[1:], 1):
        user = users[(i + 1) % len(users)]
        content = root_replies[(i - 1) % len(root_replies)]

        reply_comment = Comment(
            content=content, 
            author_id=user.id, 
            message_id=message.id, 
            parent_id=root.id
        )
        db_session.add(reply_comment)
        logger.info(f"  💬 Reply to root {i + 1}: '{content}'")

    total_comments = 3 + max_depth + 2 + 2  # roots + deep + branches + replies
    logger.info(
        f"✅ Created {total_comments} comments with {max_depth} levels of nesting"
    )

    return nested_comments


def create_regular_comments_in_session(db_session, message, users):
    """Create regular (non-deeply nested) comments for a message within an existing session."""
    logger.info(f"💬 Creating regular comments for wish: '{message.content[:50]}...'")

    comments_data = [
        "Fantastic! I'm cheering for you too! Hope your wish comes true! 🌟",
        "This wish is wonderful! I believe you can definitely do it! 💪",
        "Wow, seeing your wish really touches me, let's work together!",
        "Keep going! I think your idea is amazing!",
        "Blessings! Hope good luck always accompanies you! 🍀",
    ]

    comments = []
    for i, content in enumerate(comments_data):
        user = users[i % len(users)]
        comment = Comment(
            content=content, 
            author_id=user.id, 
            message_id=message.id
        )
        db_session.add(comment)
        db_session.flush()  # Get the ID
        comments.append(comment)

        # Add some replies
        if i < 2:  # Add replies to first 2 comments
            reply_templates = [
                "Thank you for your blessing! 💕",
                "Your words make me feel so warm!",
                "Let's work together! ✊",
                "Really appreciate it!",
                "We will all achieve our wishes!",
            ]
            reply_content = reply_templates[i % len(reply_templates)]
            reply_user = users[(i + 1) % len(users)]
            reply_comment = Comment(
                content=reply_content,
                author_id=reply_user.id,
                message_id=message.id,
                parent_id=comment.id,
            )
            db_session.add(reply_comment)

    logger.info(f"✨ Created {len(comments_data) + 2} regular comments")
    return comments


def generate_seed_data():
    """Generate all seed data."""
    logger.info("🌟 Starting wish wall seed data generation...")

    start_time = time.time()

    # Initialize database
    init_db()

    from app.common.database import get_db_session

    # Create all data within a single session context to avoid detached instance issues
    with get_db_session() as db_session:
        # Create sample users
        logger.info("👥 Creating sample users...")
        users_data = [
            {"username": "admin", "email": "admin@example.com", "password": "Admin123!"},
            {"username": "alice", "email": "alice@example.com", "password": "Alice123!"},
            {"username": "bob", "email": "bob@example.com", "password": "Bob123!"},
            {"username": "charlie", "email": "charlie@example.com", "password": "Charlie123!"},
            {"username": "diana", "email": "diana@example.com", "password": "Diana123!"},
        ]

        users = []
        for user_data in users_data:
            try:
                # Check if user already exists
                existing_user = (
                    db_session.query(User)
                    .filter(User.username == user_data["username"])
                    .first()
                )
                
                if existing_user:
                    users.append(existing_user)
                    logger.info(f"  ⚠️  User {user_data['username']} already exists, using existing user")
                else:
                    # Create new user
                    user = User(
                        username=user_data["username"],
                        email=user_data["email"],
                        password=user_data["password"]
                    )
                    db_session.add(user)
                    db_session.flush()  # Get the ID
                    users.append(user)
                    logger.info(f"  ✅ Created user: {user.username}")
                    
            except Exception as e:
                logger.error(f"  ❌ Failed to create user {user_data['username']}: {e}")

        logger.info(f"✅ Created/found {len(users)} users")

        # Create sample messages
        logger.info("🌟 Creating sample wishes...")
        messages_data = [
            {
                "content": "🏆 I wish to achieve financial success! Hope my investments do well this year! 💰💰💰",
                "author_index": 0,  # admin
            },
            {
                "content": "💕 I wish to find a kind and loving partner, hoping to meet the right person soon!",
                "author_index": 1,  # alice
            },
            {
                "content": "✈️ I want to travel around the world! Especially to see cherry blossoms in Japan, mountains in Switzerland, and beaches in Maldives!",
                "author_index": 2,  # bob
            },
            {
                "content": "📚 I hope to pass my exams and get accepted to my dream university! Academic success!",
                "author_index": 3,  # charlie
            },
            {
                "content": "🌈 I wish for my family's health and happiness, and for everyone to have a smooth career!",
                "author_index": 4,  # diana
            },
        ]

        messages = []
        for msg_data in messages_data:
            try:
                author = users[msg_data["author_index"]]
                message = Message(
                    content=msg_data["content"], 
                    author_id=author.id
                )
                db_session.add(message)
                db_session.flush()  # Get the ID
                messages.append(message)
                logger.info(
                    f"  ✨ Created wish by {author.username}: '{message.content[:50]}...'"
                )
            except Exception as e:
                logger.error(f"  ❌ Failed to create message: {e}")

        logger.info(f"🌟 Created {len(messages)} wishes")

        if not messages:
            logger.error("❌ No messages created, cannot continue with comments")
            return

        # Create deeply nested comments for the first message
        logger.info("\n" + "=" * 60)
        logger.info("🏗️  CREATING DEEP NESTED COMMENT STRUCTURE")
        logger.info("=" * 60)

        deep_comment_message = messages[0]
        create_deep_nested_comments_in_session(db_session, deep_comment_message, users, max_depth=20)

        # Create regular comments for other messages
        logger.info("\n" + "=" * 60)
        logger.info("🏗️  CREATING REGULAR WISH COMMENTS")
        logger.info("=" * 60)

        for message in messages[1:]:
            create_regular_comments_in_session(db_session, message, users)

    total_time = time.time() - start_time

    logger.info("\n" + "=" * 60)
    logger.info("🎉 WISH WALL SEED DATA GENERATION COMPLETED!")
    logger.info("=" * 60)
    logger.info(f"⏱️  Total time: {total_time:.3f} seconds")
    logger.info(f"👥 Users created: {len(users)}")
    logger.info(f"🌟 Wishes created: {len(messages)}")
    logger.info("💬 Comments: Multiple levels including 20-deep nesting")
    logger.info("\n🚀 You can now test the wish wall system!")
    logger.info("💡 Try the API endpoints to see wishes and their nested comments.")
    logger.info("✨ May all wishes come true! 🌈")


def main():
    """Main function."""
    try:
        generate_seed_data()
    except Exception as e:
        logger.error(f"❌ Seed generation failed: {e}")
        import traceback

        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
