#!/usr/bin/env python3
"""
Wish Wall Seed Script - 许愿墙种子数据生成脚本

Seed script to populate the database with wish wall sample data.
Creates users, wishes (messages), and deeply nested comments for testing.

Features:
- Creates sample users
- Creates various wishes (发财、脱单、旅行、学业、健康)
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
    """Initialize database connection and create tables."""
    database_url = settings.database_url
    init_database(database_url)

    # Create tables if they don't exist
    Base.metadata.create_all(bind=get_engine())
    logger.info("✅ Database initialized")


def create_sample_users():
    """Create sample users."""
    logger.info("👥 Creating sample users...")

    users_data = [
        {"username": "admin", "email": "admin@example.com", "password": "admin123"},
        {"username": "alice", "email": "alice@example.com", "password": "alice123"},
        {"username": "bob", "email": "bob@example.com", "password": "bob123"},
        {
            "username": "charlie",
            "email": "charlie@example.com",
            "password": "charlie123",
        },
        {"username": "diana", "email": "diana@example.com", "password": "diana123"},
    ]

    users = []
    for user_data in users_data:
        try:
            user = User.create_user(**user_data)
            users.append(user)
            logger.info(f"  ✅ Created user: {user.username}")
        except Exception as e:
            logger.warning(f"  ⚠️  User {user_data['username']} may already exist: {e}")
            # Try to find existing user
            from app.common.database import get_db_session

            db_session = get_db_session()
            existing_user = (
                db_session.query(User)
                .filter(User.username == user_data["username"])
                .first()
            )
            if existing_user:
                users.append(existing_user)

    logger.info(f"✅ Created/found {len(users)} users")
    return users


def create_sample_messages(users):
    """Create sample messages."""
    logger.info("🌟 Creating sample wishes...")

    messages_data = [
        {
            "content": "🏆 我要发大财！希望今年投资顺利，财源滚滚来！💰💰💰",
            "author": users[0],  # admin
        },
        {
            "content": "💕 我要找个温柔善良的女朋友，希望能遇到那个对的人～",
            "author": users[1],  # alice
        },
        {
            "content": "✈️ 我要去环游世界！特别想去日本看樱花、去瑞士看雪山、去马尔代夫看海！",
            "author": users[2],  # bob
        },
        {
            "content": "📚 希望能顺利通过考试，拿到心仪大学的录取通知书！学业进步！",
            "author": users[3],  # charlie
        },
        {
            "content": "🌈 愿家人身体健康，工作顺利，每天都开开心心的！",
            "author": users[4],  # diana
        },
    ]

    messages = []
    for msg_data in messages_data:
        message = Message.create_message(
            content=msg_data["content"], author_id=msg_data["author"].id
        )
        messages.append(message)
        logger.info(
            f"  ✨ Created wish by {msg_data['author'].username}: '{message.content[:50]}...'"
        )

    logger.info(f"🌟 Created {len(messages)} wishes")
    return messages


def create_deep_nested_comments(message, users, max_depth=20):
    """Create deeply nested comments (20 levels) for a message."""
    logger.info(
        f"💬 Creating 20-level nested comments for wish: '{message.content[:50]}...'"
    )

    comment_templates = [
        "加油！{topic}一定会实现的！💪",
        "我也有同样的愿望！{topic}真的太重要了～",
        "祝福你早日实现{topic}的梦想！🙏",
        "哇，{topic}听起来就很棒！",
        "我觉得{topic}需要这样努力...",
        "支持！{topic}是很多人的梦想呢",
        "想到{topic}就很激动！",
        "关于{topic}，我想分享一些经验...",
        "你的{topic}愿望让我很感动",
        "我也在为{topic}而努力！",
        "希望我们都能实现{topic}！",
        "为{topic}点赞！👍",
        "相信{topic}一定会成功的！",
        "加油加油！{topic}值得拥有！",
        "我的朋友也有{topic}的愿望",
        "关于{topic}，我有个建议...",
        "真心祝福{topic}早日实现！",
        "你的{topic}想法很棒！",
        "一起为{topic}努力吧！",
        "愿{topic}的美好都降临到你身上✨",
    ]

    # Extract wish topic from message content
    if "发大财" in message.content:
        topic = "发财"
    elif "女朋友" in message.content or "男朋友" in message.content:
        topic = "脱单"
    elif "旅游" in message.content or "环游" in message.content:
        topic = "旅行"
    elif "考试" in message.content or "学业" in message.content:
        topic = "学业"
    elif "健康" in message.content:
        topic = "健康"
    else:
        topic = "愿望"

    # Create root comments
    root_comments = []
    for i in range(3):  # 3 root comments
        user = users[i % len(users)]
        content = comment_templates[i].format(topic=topic)

        comment = Comment.create_comment(
            content=content, author_id=user.id, message_id=message.id
        )
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

        nested_comment = Comment.create_comment(
            content=content,
            author_id=user.id,
            message_id=message.id,
            parent_id=current_parent.id,
        )

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
            f"我觉得实现{topic}还需要这样...",
            f"关于{topic}，我有个不同的想法！",
        ]
        for i in range(2):  # 2 branches
            user = users[(i + 2) % len(users)]
            content = branch_comments[i]

            Comment.create_comment(
                content=content,
                author_id=user.id,
                message_id=message.id,
                parent_id=parent_for_branch.id,
            )
            logger.info(f"    🌿 Branch {i + 1}: '{content}'")

    # Add some replies to other root comments
    root_replies = [f"我也想{topic}！一起努力！", f"{topic}真的很棒，支持你！"]
    for i, root in enumerate(root_comments[1:], 1):
        user = users[(i + 1) % len(users)]
        content = root_replies[(i - 1) % len(root_replies)]

        Comment.create_comment(
            content=content, author_id=user.id, message_id=message.id, parent_id=root.id
        )
        logger.info(f"  💬 Reply to root {i + 1}: '{content}'")

    total_comments = 3 + max_depth + 2 + 2  # roots + deep + branches + replies
    logger.info(
        f"✅ Created {total_comments} comments with {max_depth} levels of nesting"
    )

    return nested_comments


def create_regular_comments(message, users):
    """Create regular (non-deeply nested) comments for a message."""
    logger.info(f"💬 Creating regular comments for wish: '{message.content[:50]}...'")

    comments_data = [
        "太棒了！我也为你加油！希望你的愿望成真！🌟",
        "这个愿望很棒呢～我相信你一定可以的！💪",
        "哇，看到你的愿望我也很感动，一起努力吧！",
        "加油加油！我觉得你的想法很棒！",
        "祝福祝福！希望好运一直伴随着你！🍀",
    ]

    comments = []
    for i, content in enumerate(comments_data):
        user = users[i % len(users)]
        comment = Comment.create_comment(
            content=content, author_id=user.id, message_id=message.id
        )
        comments.append(comment)

        # Add some replies
        if i < 2:  # Add replies to first 2 comments
            reply_templates = [
                "谢谢你的祝福！💕",
                "你的话让我很温暖～",
                "一起加油呀！✊",
                "真的很感谢！",
                "我们都会实现愿望的！",
            ]
            reply_content = reply_templates[i % len(reply_templates)]
            reply_user = users[(i + 1) % len(users)]
            Comment.create_comment(
                content=reply_content,
                author_id=reply_user.id,
                message_id=message.id,
                parent_id=comment.id,
            )

    logger.info(f"✨ Created {len(comments_data) + 2} regular comments")
    return comments


def generate_seed_data():
    """Generate all seed data."""
    logger.info("🌟 Starting wish wall seed data generation...")

    start_time = time.time()

    # Initialize database
    init_db()

    # Create sample data
    users = create_sample_users()
    messages = create_sample_messages(users)

    # Create deeply nested comments for the first message
    logger.info("\n" + "=" * 60)
    logger.info("🏗️  CREATING DEEP NESTED COMMENT STRUCTURE")
    logger.info("=" * 60)

    deep_comment_message = messages[0]
    create_deep_nested_comments(deep_comment_message, users, max_depth=20)

    # Create regular comments for other messages
    logger.info("\n" + "=" * 60)
    logger.info("🏗️  CREATING REGULAR WISH COMMENTS")
    logger.info("=" * 60)

    for message in messages[1:]:
        create_regular_comments(message, users)

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
