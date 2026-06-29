import atexit
import os
import sys
import tempfile

# Use temporary file database for tests to support multiple engines properly
db_fd, db_path = tempfile.mkstemp(suffix=".db")
os.close(db_fd)
os.environ["DATABASE_URL"] = f"sqlite:///{db_path}"


def cleanup_db():
    try:
        os.remove(db_path)
    except OSError:
        pass


atexit.register(cleanup_db)

# Ensure the root directory is in the python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
