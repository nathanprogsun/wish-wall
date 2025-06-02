#!/usr/bin/env python3
"""
Code quality tools CLI script.
Usage: python scripts/lint.py [command]

Commands:
  format    - Format code with ruff
  lint      - Run ruff linting
  typecheck - Run mypy type checking
  all       - Run all quality checks
"""

import subprocess
import sys
from pathlib import Path


def run_command(cmd: list[str], description: str) -> bool:
    """Run a command and return success status."""
    print(f"\n🔍 {description}...")
    print(f"Running: {' '.join(cmd)}")

    try:
        result = subprocess.run(cmd, check=True, capture_output=True, text=True)
        if result.stdout:
            print(result.stdout)
        print(f"✅ {description} completed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed")
        if e.stdout:
            print("STDOUT:", e.stdout)
        if e.stderr:
            print("STDERR:", e.stderr)
        return False


def format_code() -> bool:
    """Format code with ruff."""
    return run_command(
        ["ruff", "format", "app/", "tests/", "scripts/"], "Code formatting"
    )


def lint_code() -> bool:
    """Run ruff linting."""
    return run_command(
        ["ruff", "check", "app/", "tests/", "scripts/", "--fix"], "Linting"
    )


def run_all() -> bool:
    """Run all quality checks."""
    success = True

    # Format first
    if not format_code():
        success = False

    # Then lint
    if not lint_code():
        success = False

    return success


def main() -> None:
    """Main CLI entry point."""
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)

    command = sys.argv[1].lower()

    # Change to project root
    project_root = Path(__file__).parent.parent
    sys.path.insert(0, str(project_root))

    success = False

    if command == "format":
        success = format_code()
    elif command == "lint":
        success = lint_code()
    elif command == "all":
        success = run_all()
    else:
        print(f"Unknown command: {command}")
        print(__doc__)
        sys.exit(1)

    if success:
        print("\n🎉 All checks passed!")
        sys.exit(0)
    else:
        print("\n💥 Some checks failed!")
        sys.exit(1)


if __name__ == "__main__":
    main()
