#!/usr/bin/env python3
"""Simple Twelvelabs diagnostic without complex dependencies"""

import os
import sys

print("🚀 Quick Twelvelabs Diagnostic")
print("=" * 40)

# Test 1: Check .env file
print("\n1. Checking .env file...")
if os.path.exists('.env'):
    print("   ✅ .env file exists")
    with open('.env', 'r') as f:
        content = f.read()
    
    if 'TWELVELABS_API_KEY=' in content:
        print("   ✅ TWELVELABS_API_KEY found in .env")
        # Extract the key value
        for line in content.split('\n'):
            if line.startswith('TWELVELABS_API_KEY='):
                key = line.split('=', 1)[1].strip()
                print(f"   ✅ Key starts with 'tlk_': {key.startswith('tlk_')}")
                print(f"   ✅ Key length: {len(key)} characters")
                break
    else:
        print("   ❌ TWELVELABS_API_KEY not found in .env")
else:
    print("   ❌ .env file does not exist")

# Test 2: Test import
print("\n2. Testing Twelvelabs import...")
try:
    sys.path.insert(0, '/workspace/venv/lib/python3.9/site-packages')
    import twelvelabs
    print("   ✅ Twelvelabs package imported successfully")
    print(f"   ✅ Package location: {twelvelabs.__file__}")
except ImportError as e:
    print(f"   ❌ Failed to import twelvelabs: {e}")
    print("   💡 Try: pip install twelvelabs")

# Test 3: Test environment loading manually
print("\n3. Testing environment variable loading...")
# Manually load from .env file
env_vars = {}
if os.path.exists('.env'):
    with open('.env', 'r') as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#') and '=' in line:
                key, value = line.split('=', 1)
                env_vars[key] = value
                
    api_key = env_vars.get('TWELVELABS_API_KEY')
    if api_key:
        print(f"   ✅ API key loaded: {api_key[:10]}...")
        
        # Test 4: Try basic client creation
        print("\n4. Testing client creation...")
        try:
            from twelvelabs import TwelveLabs
            client = TwelveLabs(api_key=api_key)
            print("   ✅ Client created successfully")
            
            # Test 5: Try a simple API call
            print("\n5. Testing basic API call...")
            try:
                indexes = client.index.list()
                print(f"   ✅ API call successful! Found {len(indexes)} indexes")
                for i, idx in enumerate(indexes):
                    print(f"      Index {i+1}: {idx.name}")
            except Exception as e:
                print(f"   ❌ API call failed: {e}")
                error_str = str(e).lower()
                if 'unauthorized' in error_str:
                    print("   💡 Authentication error - check your API key")
                elif 'connection' in error_str:
                    print("   💡 Connection error - check internet/firewall")
                    
        except Exception as e:
            print(f"   ❌ Client creation failed: {e}")
    else:
        print("   ❌ No API key found")

print("\n" + "=" * 40)
print("Diagnostic complete!")