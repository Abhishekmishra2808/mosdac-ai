#!/usr/bin/env python3
"""
MOSDAC Chatbot Backend Test Script
This script tests if all dependencies are properly installed and configured.
"""

import sys
import os

def test_imports():
    """Test if all required packages can be imported"""
    print("🔍 Testing imports...")
    
    try:
        import fastapi
        print("✅ FastAPI imported successfully")
    except ImportError as e:
        print(f"❌ FastAPI import failed: {e}")
        return False
    
    try:
        import uvicorn
        print("✅ Uvicorn imported successfully")
    except ImportError as e:
        print(f"❌ Uvicorn import failed: {e}")
        return False
    
    try:
        import google.generativeai as genai
        print("✅ Google Generative AI imported successfully")
    except ImportError as e:
        print(f"❌ Google Generative AI import failed: {e}")
        return False
    
    try:
        from dotenv import load_dotenv
        print("✅ Python-dotenv imported successfully")
    except ImportError as e:
        print(f"❌ Python-dotenv import failed: {e}")
        return False
    
    return True

def test_data_access():
    """Test if scraped data can be accessed"""
    print("\n📁 Testing data access...")
    
    # Get the path relative to the project root
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    data_path = os.path.join(project_root, "data", "mosdac_content")
    
    if not os.path.exists(data_path):
        print(f"❌ Data directory not found at: {data_path}")
        return False
    
    print(f"✅ Data directory found at: {data_path}")
    
    import glob
    json_files = glob.glob(os.path.join(data_path, "pages_*.json"))
    
    if not json_files:
        print("❌ No scraped data files found. Please run the scraper first.")
        return False
    
    print(f"✅ Found {len(json_files)} data file(s)")
    return True

def test_env_file():
    """Test if .env file exists"""
    print("\n🔑 Testing environment configuration...")
    
    env_file = ".env"
    if not os.path.exists(env_file):
        print("⚠️  .env file not found. Creating template...")
        with open(env_file, "w") as f:
            f.write("# Add your Google Gemini API key here\n")
            f.write("# Get it from: https://aistudio.google.com/app/apikey\n")
            f.write("GEMINI_API_KEY=your_api_key_here\n")
        print("✅ .env template created")
    else:
        print("✅ .env file found")
    
    from dotenv import load_dotenv
    load_dotenv()
    
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key or api_key == "your_api_key_here":
        print("⚠️  GEMINI_API_KEY not configured. Please add your API key to .env file")
        return False
    
    print("✅ GEMINI_API_KEY configured")
    return True

def test_api_import():
    """Test if the API module can be imported"""
    print("\n🚀 Testing API module...")
    
    try:
        from api import app
        print("✅ API module imported successfully")
        return True
    except Exception as e:
        print(f"❌ API module import failed: {e}")
        return False

def main():
    print("🔧 MOSDAC Chatbot Backend Diagnostic Tool")
    print("=" * 50)
    
    all_tests_passed = True
    
    # Test imports
    if not test_imports():
        all_tests_passed = False
    
    # Test data access
    if not test_data_access():
        all_tests_passed = False
    
    # Test environment
    if not test_env_file():
        all_tests_passed = False
    
    # Test API import
    if not test_api_import():
        all_tests_passed = False
    
    print("\n" + "=" * 50)
    if all_tests_passed:
        print("🎉 All tests passed! Backend should be ready to run.")
        print("\nTo start the backend, run:")
        print("  python api.py")
        print("  or")
        print("  uvicorn api:app --host 0.0.0.0 --port 8000 --reload")
    else:
        print("❌ Some tests failed. Please fix the issues above.")
    
    return all_tests_passed

if __name__ == "__main__":
    main()
