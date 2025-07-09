#!/usr/bin/env python3
"""
Quick fix and run script for DocuHub
"""
import os
import sys
import subprocess

def main():
    print("🔧 DocuHub Quick Fix and Run Script")
    print("="*50)
    
    # Change to the correct directory
    script_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(script_dir)
    print(f"📁 Working directory: {script_dir}")
    
    # Set environment variable
    os.environ['DJANGO_SETTINGS_MODULE'] = 'docuhub.settings.development'
    print("🔧 Set DJANGO_SETTINGS_MODULE to docuhub.settings.development")
    
    try:
        # Test Django configuration
        print("\n📋 Testing Django configuration...")
        result = subprocess.run([sys.executable, 'test_imports.py'], 
                              capture_output=True, text=True, timeout=30)
        
        if result.returncode == 0:
            print("✅ Django configuration test passed!")
            print(result.stdout)
        else:
            print("❌ Django configuration test failed:")
            print(result.stderr)
            return False
            
        # Try to start the development server
        print("\n🚀 Starting Django development server...")
        print("Press Ctrl+C to stop the server")
        print("-"*50)
        
        # Run the server
        subprocess.run([sys.executable, 'manage.py', 'runserver', '0.0.0.0:8000'])
        
    except subprocess.TimeoutExpired:
        print("⏰ Test timed out - there might be an import issue")
        return False
    except KeyboardInterrupt:
        print("\n👋 Server stopped by user")
        return True
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)