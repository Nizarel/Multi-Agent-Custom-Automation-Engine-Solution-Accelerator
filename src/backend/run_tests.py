#!/usr/bin/env python3
"""
Test runner for MCP module tests.
Run with: python run_tests.py
"""

import sys
import os
import subprocess

# Add the backend directory to the path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def run_tests():
    """Run the MCP module tests."""
    try:
        # Check if pytest is available
        result = subprocess.run([sys.executable, '-m', 'pytest', '--version'], 
                               capture_output=True, text=True)
        if result.returncode != 0:
            print("❌ pytest not installed. Installing...")
            subprocess.run([sys.executable, '-m', 'pip', 'install', 'pytest', 'pytest-asyncio'])
        
        # Run the tests
        print("🧪 Running MCP module tests...")
        test_dir = os.path.join(os.path.dirname(__file__), 'mcp', 'tests')
        
        cmd = [
            sys.executable, '-m', 'pytest', 
            test_dir,
            '-v',
            '--tb=short',
            '-x'  # Stop on first failure
        ]
        
        result = subprocess.run(cmd, cwd=os.path.dirname(__file__))
        
        if result.returncode == 0:
            print("✅ All tests passed!")
        else:
            print("❌ Some tests failed. Check output above.")
            
        return result.returncode
        
    except Exception as e:
        print(f"❌ Error running tests: {e}")
        return 1

if __name__ == "__main__":
    exit_code = run_tests()
    sys.exit(exit_code)
