"""Test configuration for pytest."""

# Add the parent directory to the Python path for imports
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

# pytest configuration
pytest_plugins = []
