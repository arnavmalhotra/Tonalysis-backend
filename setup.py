#!/usr/bin/env python3
"""
Setup script for Speech Therapy Practice App with Twelvelabs Integration
"""

import subprocess
import sys
import os
from pathlib import Path

def run_command(command, description):
    """Run a command and handle errors"""
    print(f"\n🔄 {description}...")
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(f"✅ {description} completed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed: {e.stderr}")
        return False

def check_python_version():
    """Check if Python version is compatible"""
    if sys.version_info < (3, 8):
        print("❌ Python 3.8 or higher is required")
        return False
    print(f"✅ Python {sys.version.split()[0]} detected")
    return True

def install_dependencies():
    """Install Python dependencies"""
    print("\n🔄 Installing Python dependencies...")
    
    # Try different pip installation methods
    pip_commands = [
        "pip install -r requirements.txt",
        "pip3 install -r requirements.txt",
        "python -m pip install -r requirements.txt",
        "python3 -m pip install -r requirements.txt"
    ]
    
    for cmd in pip_commands:
        print(f"Trying: {cmd}")
        if run_command(cmd, f"Installing dependencies with {cmd.split()[0]}"):
            return True
    
    # If all fail, try installing individual packages
    print("\n⚠️  Standard pip install failed. Trying individual package installation...")
    
    packages = [
        "fastapi==0.116.1",
        "uvicorn==0.35.0", 
        "websockets==15.0.1",
        "google-genai==1.26.0",
        "python-dotenv==1.1.1",
        "requests==2.32.4",
        "twelvelabs==0.4.10"
    ]
    
    failed_packages = []
    for package in packages:
        if not run_command(f"pip install {package}", f"Installing {package}"):
            failed_packages.append(package)
    
    if failed_packages:
        print(f"\n❌ Failed to install: {', '.join(failed_packages)}")
        print("💡 You may need to install these manually:")
        for package in failed_packages:
            print(f"   pip install {package}")
        return False
    
    return True

def setup_environment():
    """Setup environment configuration"""
    env_file = Path(".env")
    
    if env_file.exists():
        print("\n✅ .env file already exists")
        
        # Check if API keys are configured
        with open(env_file, 'r') as f:
            content = f.read()
            
        if "your_google_api_key_here" in content or "your_twelvelabs_api_key_here" in content:
            print("\n⚠️  Please update your API keys in .env file:")
            print("   - Get Google Gemini API key: https://makersuite.google.com/app/apikey")
            print("   - Get Twelvelabs API key: https://twelvelabs.io")
    else:
        print("\n⚠️  .env file not found. Please create one with your API keys.")
        
    return True

def create_directories():
    """Create necessary directories"""
    directories = ["videos", "models"]
    
    for directory in directories:
        dir_path = Path(directory)
        if not dir_path.exists():
            dir_path.mkdir(exist_ok=True)
            print(f"✅ Created directory: {directory}")
        else:
            print(f"✅ Directory exists: {directory}")
    
    return True

def test_imports():
    """Test if critical imports work"""
    print("\n🔄 Testing imports...")
    
    try:
        import fastapi
        print("✅ FastAPI imported successfully")
    except ImportError:
        print("❌ FastAPI import failed")
        return False
    
    try:
        import twelvelabs
        print("✅ Twelvelabs SDK imported successfully")
    except ImportError:
        print("❌ Twelvelabs SDK import failed - you may need to install it manually:")
        print("   pip install twelvelabs==0.4.10")
        return False
    
    try:
        from google import genai
        print("✅ Google Gemini imported successfully")
    except ImportError:
        print("❌ Google Gemini import failed")
        return False
    
    return True

def main():
    """Main setup function"""
    print("🚀 Setting up Speech Therapy Practice App with Twelvelabs Integration")
    print("=" * 70)
    
    # Check Python version
    if not check_python_version():
        return False
    
    # Install dependencies
    if not install_dependencies():
        print("\n❌ Dependency installation failed. Please check the errors above.")
        return False
    
    # Setup environment
    if not setup_environment():
        return False
    
    # Create directories
    if not create_directories():
        return False
    
    # Test imports
    if not test_imports():
        print("\n⚠️  Some imports failed, but you can still try running the app.")
    
    print("\n" + "=" * 70)
    print("🎉 Setup completed!")
    print("\nNext steps:")
    print("1. Configure your API keys in .env file")
    print("2. Run: python main.py")
    print("3. Open: http://localhost:8000")
    print("\nFor detailed instructions, see README.md")
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)