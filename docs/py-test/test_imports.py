#!/usr/bin/env python3
"""
Test script to check Django imports and configuration
"""
import os
import sys
import django

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Set Django settings module
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'docuhub.settings.development')

def test_syntax():
    """Test Python syntax of key files"""
    import py_compile
    
    print("🔍 Testing file syntax...")
    files_to_check = [
        'apps/projects/api_views.py',
        'apps/projects/views.py',
        'apps/projects/permissions.py',
        'apps/projects/services.py',
    ]
    
    for filepath in files_to_check:
        if os.path.exists(filepath):
            try:
                py_compile.compile(filepath, doraise=True)
                print(f"✅ {filepath} - syntax OK")
            except py_compile.PyCompileError as e:
                print(f"❌ {filepath} - syntax error: {e}")
                return False
        else:
            print(f"⚠️  {filepath} - file not found")
    
    return True

def test_django_setup():
    """Test Django configuration and imports"""
    try:
        print("\n🔧 Testing Django setup...")
        django.setup()
        print("✅ Django setup successful!")
        
        print("\n📦 Testing app imports...")
        
        # Test core imports
        try:
            from apps.core.models import *
            print("✅ Core models imported successfully")
        except Exception as e:
            print(f"⚠️  Core models: {e}")
        
        try:
            from apps.accounts.models import *
            print("✅ Accounts models imported successfully")
        except Exception as e:
            print(f"⚠️  Accounts models: {e}")
        
        try:
            from apps.projects.models import *
            print("✅ Projects models imported successfully")
        except Exception as e:
            print(f"❌ Projects models: {e}")
            return False
        
        try:
            from apps.notifications.models import *
            print("✅ Notifications models imported successfully")
        except Exception as e:
            print(f"⚠️  Notifications models: {e}")
        
        # Test new permissions
        try:
            from apps.projects.permissions import IsProjectManager, CanViewProject
            print("✅ New permissions imported successfully")
        except Exception as e:
            print(f"❌ Permissions import failed: {e}")
            return False
        
        # Test services
        try:
            from apps.projects.services import ProjectBulkOperationsService
            print("✅ Services imported successfully")
        except Exception as e:
            print(f"❌ Services import failed: {e}")
            return False
        
        # Test views
        try:
            from apps.projects.views import dashboard
            print("✅ Views imported successfully")
        except Exception as e:
            print(f"❌ Views import failed: {e}")
            return False
        
        # Test API views
        try:
            from apps.projects.api_views import ProjectViewSet
            print("✅ API views imported successfully")
        except Exception as e:
            print(f"❌ API views import failed: {e}")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ Django setup failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    print("🧪 DocuHub Import Test Suite")
    print("="*40)
    
    # Test syntax first
    if not test_syntax():
        print("\n💥 Syntax errors found! Fix these first.")
        return False
    
    # Test Django setup
    if not test_django_setup():
        print("\n💥 Django import errors found!")
        return False
    
    print("\n🎉 All tests passed! Django is configured correctly.")
    print("\n🚀 You can now run: python manage.py runserver")
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)