#!/usr/bin/env python3
"""
Verify seed data and demonstrate tree structure.
"""

import sys
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

import os

from app.common.database import get_db_session, init_database
from app.model.comment import Comment
from app.model.message import Message
from app.model.user import User
from app.service.message_service import MessageService
from app.settings import settings


def main():
    database_url = settings.database_url
    init_database(database_url)

    db_session = get_db_session()
    user_count = db_session.query(User).count()
    message_count = db_session.query(Message).count()
    comment_count = db_session.query(Comment).count()

    print("📊 Database Statistics:")
    print(f"👥 Users: {user_count}")
    print(f"📝 Messages: {message_count}")
    print(f"💬 Comments: {comment_count}")

    first_message = db_session.query(Message).first()
    if first_message:
        print(f'\n🔍 First message: "{first_message.content[:50]}..."')

        message_response = MessageService.get_message(first_message.id)
        root_comments = message_response.comments

        print(f"🌲 Root comments: {len(root_comments)}")
        for i, root in enumerate(root_comments, 1):
            print(
                f'  📌 Root {i}: "{root.content[:40]}..." ({len(root.replies)} replies)'
            )
            if root.replies:

                def count_max_depth(comment, current_depth=0):
                    max_depth = current_depth
                    for reply in comment.replies:
                        reply_depth = count_max_depth(reply, current_depth + 1)
                        max_depth = max(max_depth, reply_depth)
                    return max_depth

                max_depth = count_max_depth(root)
                print(f"    🔗 Maximum nesting depth: {max_depth} levels")

                def show_structure(comment, level=0, max_show=3):
                    indent = "  " * level
                    if level <= max_show:
                        print(
                            f'{indent}└── "{comment.content[:30]}..." ({len(comment.replies)} replies)'
                        )
                        for reply in comment.replies[:2]:  # 只显示前2个回复
                            show_structure(reply, level + 1, max_show)
                        if len(comment.replies) > 2:
                            print(
                                f"{indent}    ... and {len(comment.replies) - 2} more replies"
                            )
                    elif level == max_show + 1:
                        print(
                            f"{indent}└── ... (continues for {max_depth - max_show} more levels)"
                        )

                print("    🌲 Structure preview:")
                show_structure(root)


if __name__ == "__main__":
    main()
