#!/usr/bin/env python3
"""
Twelvelabs Connection Diagnostic Script
This script tests each component separately to identify the exact issue.
"""

import os
import sys
from dotenv import load_dotenv

def test_environment():
    """Test environment variable loading"""
    print("🔍 Testing Environment Variables...")
    
    load_dotenv()
    
    api_key = os.getenv('TWELVELABS_API_KEY')
    google_key = os.getenv('GOOGLE_API_KEY')
    
    print(f"   .env file exists: {os.path.exists('.env')}")
    
    if api_key:
        print(f"   ✅ TWELVELABS_API_KEY found: {api_key[:10]}...")
        print(f"   ✅ Starts with 'tlk_': {api_key.startswith('tlk_')}")
        print(f"   ✅ Length: {len(api_key)} characters")
    else:
        print("   ❌ TWELVELABS_API_KEY not found!")
        return False
    
    if google_key:
        print(f"   ✅ GOOGLE_API_KEY found: {google_key[:10]}...")
    else:
        print("   ⚠️  GOOGLE_API_KEY not found")
    
    return bool(api_key)

def test_package_installation():
    """Test if Twelvelabs package is properly installed"""
    print("\n🔍 Testing Package Installation...")
    
    try:
        import twelvelabs
        print(f"   ✅ twelvelabs package imported successfully")
        print(f"   ✅ Version: {getattr(twelvelabs, '__version__', 'unknown')}")
        return True
    except ImportError as e:
        print(f"   ❌ Failed to import twelvelabs: {e}")
        return False

def test_client_initialization():
    """Test Twelvelabs client initialization"""
    print("\n🔍 Testing Client Initialization...")
    
    try:
        from twelvelabs import TwelveLabs
        api_key = os.getenv('TWELVELABS_API_KEY')
        
        if not api_key:
            print("   ❌ No API key available")
            return False, None
            
        client = TwelveLabs(api_key=api_key)
        print("   ✅ Client initialized successfully")
        return True, client
        
    except Exception as e:
        print(f"   ❌ Client initialization failed: {e}")
        print(f"   ❌ Error type: {type(e).__name__}")
        return False, None

def test_basic_api_call(client):
    """Test basic API connectivity"""
    print("\n🔍 Testing Basic API Connectivity...")
    
    if not client:
        print("   ❌ No client available")
        return False
    
    try:
        # Try to list indexes (simple API call)
        indexes = client.index.list()
        print(f"   ✅ API call successful!")
        print(f"   ✅ Found {len(indexes)} indexes")
        
        # Display index information
        for i, idx in enumerate(indexes):
            print(f"      Index {i+1}: {idx.name} (ID: {idx.id})")
        
        return True, indexes
        
    except Exception as e:
        print(f"   ❌ API call failed: {e}")
        print(f"   ❌ Error type: {type(e).__name__}")
        
        # Check for specific error types
        error_str = str(e).lower()
        if 'unauthorized' in error_str or '401' in error_str:
            print("   💡 This looks like an authentication error - check your API key")
        elif 'connection' in error_str or 'network' in error_str:
            print("   💡 This looks like a network connectivity issue")
        elif 'timeout' in error_str:
            print("   💡 This looks like a timeout issue")
        
        return False, None

def test_index_creation(client):
    """Test index creation (if no indexes exist)"""
    print("\n🔍 Testing Index Creation...")
    
    if not client:
        print("   ❌ No client available")
        return False
    
    try:
        # Check if we have any indexes
        existing_indexes = client.index.list()
        
        if len(existing_indexes) > 0:
            print(f"   ✅ Using existing index: {existing_indexes[0].name}")
            return True, existing_indexes[0]
        
        # Create a test index
        print("   🔄 Creating test index...")
        index = client.index.create(
            name="test_speech_therapy_index",
            models=[
                {
                    "name": "marengo2.7",
                    "options": ["visual", "audio"]
                }
            ]
        )
        print(f"   ✅ Index created successfully: {index.name} (ID: {index.id})")
        return True, index
        
    except Exception as e:
        print(f"   ❌ Index creation failed: {e}")
        print(f"   ❌ Error type: {type(e).__name__}")
        return False, None

def test_small_file_upload(client, index):
    """Test file upload with a very small test file"""
    print("\n🔍 Testing File Upload (with small test file)...")
    
    if not client or not index:
        print("   ❌ No client or index available")
        return False
    
    # Create a small test file
    test_content = b"This is a test file for debugging"
    test_file_path = "debug_test_file.txt"
    
    try:
        # Write test file
        with open(test_file_path, 'wb') as f:
            f.write(test_content)
        
        print(f"   📁 Created test file: {test_file_path} ({len(test_content)} bytes)")
        
        # This will likely fail since it's not a video file, but it tests the upload mechanism
        with open(test_file_path, 'rb') as f:
            task = client.task.create(
                index_id=index.id,
                file=f,
                language="en"
            )
        
        print(f"   ✅ Upload request successful! Task ID: {task.id}")
        
        # Clean up
        if os.path.exists(test_file_path):
            os.remove(test_file_path)
            
        return True
        
    except Exception as e:
        print(f"   ❌ Upload failed: {e}")
        print(f"   ❌ Error type: {type(e).__name__}")
        
        # Clean up
        if os.path.exists(test_file_path):
            os.remove(test_file_path)
        
        # Analyze the error
        error_str = str(e).lower()
        if 'connection' in error_str:
            print("   💡 This confirms a connection issue during file upload")
        elif 'format' in error_str or 'invalid' in error_str:
            print("   💡 File format error (expected for test file)")
        
        return False

def main():
    """Run all diagnostic tests"""
    print("🚀 Twelvelabs Connection Diagnostic Tool")
    print("=" * 50)
    
    # Test 1: Environment
    if not test_environment():
        print("\n❌ Environment test failed. Check your .env file.")
        return
    
    # Test 2: Package installation
    if not test_package_installation():
        print("\n❌ Package installation test failed. Run: pip install twelvelabs")
        return
    
    # Test 3: Client initialization
    client_ok, client = test_client_initialization()
    if not client_ok:
        print("\n❌ Client initialization failed. Check your API key.")
        return
    
    # Test 4: Basic API call
    api_ok, indexes = test_basic_api_call(client)
    if not api_ok:
        print("\n❌ Basic API call failed. This is likely the root cause.")
        return
    
    # Test 5: Index creation/retrieval
    index_ok, index = test_index_creation(client)
    if not index_ok:
        print("\n❌ Index creation failed.")
        return
    
    # Test 6: File upload test
    upload_ok = test_small_file_upload(client, index)
    
    print("\n" + "=" * 50)
    if upload_ok:
        print("✅ All tests passed! Your Twelvelabs setup appears to be working.")
    else:
        print("⚠️  Upload test failed, but basic connectivity works.")
        print("   This suggests the issue is with file upload, not authentication.")
    
    print("\n💡 Next steps:")
    print("   1. If basic API calls work but uploads fail, try with a real video file")
    print("   2. Check video file format and size requirements")
    print("   3. Ensure proper file permissions")

if __name__ == "__main__":
    main()