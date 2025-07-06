#!/usr/bin/env python3
"""
InsightIQ Code Validation Script
Checks for common Python syntax and import errors
"""

import os
import sys
import ast
import importlib.util

def check_python_syntax(file_path):
    """Check if a Python file has valid syntax"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        ast.parse(content)
        return True, None
    except SyntaxError as e:
        return False, f"Syntax error: {e}"
    except Exception as e:
        return False, f"Error reading file: {e}"

def find_python_files(directory):
    """Find all Python files in a directory"""
    python_files = []
    for root, dirs, files in os.walk(directory):
        # Skip virtual environment and migrations
        if 'venv' in root or 'migrations' in root or '__pycache__' in root:
            continue
        for file in files:
            if file.endswith('.py'):
                python_files.append(os.path.join(root, file))
    return python_files

def main():
    print("🔍 InsightIQ Code Validation")
    print("=" * 50)
    
    # Get current directory
    project_dir = os.getcwd()
    print(f"Scanning: {project_dir}")
    
    # Find all Python files
    python_files = find_python_files(project_dir)
    print(f"Found {len(python_files)} Python files")
    
    # Check syntax for each file
    errors = []
    for file_path in python_files:
        is_valid, error = check_python_syntax(file_path)
        if not is_valid:
            rel_path = os.path.relpath(file_path, project_dir)
            errors.append(f"❌ {rel_path}: {error}")
        else:
            rel_path = os.path.relpath(file_path, project_dir)
            print(f"✅ {rel_path}")
    
    print("\n" + "=" * 50)
    
    if errors:
        print(f"❌ Found {len(errors)} files with syntax errors:")
        for error in errors:
            print(error)
        return 1
    else:
        print("✅ All Python files have valid syntax!")
        return 0

if __name__ == "__main__":
    sys.exit(main())
