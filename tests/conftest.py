import os
import sys

# Use in-memory database for tests
os.environ["DATABASE_URL"] = "sqlite:///:memory:"

# Ensure the root directory is in the python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
