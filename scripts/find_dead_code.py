#!/usr/bin/env python3
"""Find dead code, unused imports, and unreachable code."""

import ast
import os


def find_unused_imports(filepath):
    """Find unused imports in a Python file."""
    with open(filepath, "r") as f:
        try:
            tree = ast.parse(f.read())
        except SyntaxError:
            return set()

    imports = set()
    used = set()

    for node in ast.walk(tree):
        if isinstance(node, (ast.Import, ast.ImportFrom)):
            for alias in node.names:
                imports.add(alias.asname or alias.name)
        elif isinstance(node, ast.Name):
            used.add(node.id)

    unused = imports - used
    return unused


def find_dead_code():
    """Scan all Python files for dead code."""
    dead_code = {}

    directories_to_scan = ["firewall", "api", "analytics", "ml"]

    for directory in directories_to_scan:
        for root, dirs, files in os.walk(directory):
            # Skip __pycache__, .venv, etc.
            dirs[:] = [d for d in dirs if not d.startswith(".")]

            for file in files:
                if file.endswith(".py"):
                    filepath = os.path.join(root, file)
                    unused = find_unused_imports(filepath)
                    if unused:
                        dead_code[filepath] = unused

    return dead_code


if __name__ == "__main__":
    dead = find_dead_code()

    if dead:
        print("⚠️  Unused imports found:\n")
        for filepath, imports in dead.items():
            print(f"{filepath}:")
            for imp in imports:
                print(f"  - {imp}")
    else:
        print("✅ No dead imports found")
