#!/usr/bin/env python3
import os
import sys
import logging
from dotenv import load_dotenv

# Add the src directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def test_s3_swagger_tool():
    """Test s3_swagger_tool directly to see actual output"""
    print("=" * 60)
    print("TESTING S3_SWAGGER_TOOL OUTPUT")
    print("=" * 60)
    
    try:
        from src.tools.supervisor_tools import s3_swagger_tool
        
        # Test the tool directly
        result = s3_swagger_tool("Get API specifications for test case generation")
        
        print(f"SUCCESS: s3_swagger_tool executed")
        print(f"Result length: {len(result)} characters")
        print(f"Full result:")
        print("-" * 60)
        print(result)
        print("-" * 60)
        
        # Check for specific endpoint patterns
        if "execute-api.us-west-2.amazonaws.com" in result:
            print("✅ Contains expected AWS API Gateway URL")
        else:
            print("❌ Missing expected AWS API Gateway URL")
            
        if "/graphql" in result:
            print("✅ Contains GraphQL endpoint")
        else:
            print("❌ Missing GraphQL endpoint")
            
        return True
        
    except Exception as e:
        print(f"ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    test_s3_swagger_tool()