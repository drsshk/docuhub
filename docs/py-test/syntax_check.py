#!/usr/bin/env python3
"""
Quick syntax check for Python files
"""
import py_compile
import sys
import os

def check_file_syntax(filepath):
    """Check if a Python file has valid syntax"""
    try:
        py_compile.compile(filepath, doraise=True)
        return True, None
    except py_compile.PyCompileError as e:
        return False, str(e)

def main():
    files_to_check = [
        'apps/projects/api_views.py',
        'apps/projects/views.py',
        'apps/projects/permissions.py',
        'apps/projects/services.py',
        'apps/core/middleware.py',
        'docuhub/settings/base.py',
    ]
    
    print("🔍 Checking Python syntax...")
    all_good = True
    
    for filepath in files_to_check:
        if os.path.exists(filepath):
            is_valid, error = check_file_syntax(filepath)
            if is_valid:
                print(f"✅ {filepath}")
            else:
                print(f"❌ {filepath}: {error}")
                all_good = False
        else:
            print(f"⚠️  {filepath}: File not found")
    
    if all_good:
        print("\n🎉 All files have valid syntax!")
        return True
    else:
        print("\n💥 Some files have syntax errors!")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)