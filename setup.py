#!/usr/bin/env python3
"""
Setup script for AI-Powered Stateful Personal Firewall
This script helps configure the environment for first-time setup.
"""

import os
import sys
import secrets
import getpass
from pathlib import Path


def generate_api_key():
    """Generate a secure random API key."""
    return secrets.token_urlsafe(32)


def setup_backend_env():
    """Setup backend .env file."""
    env_path = Path("backend/.env")
    env_example_path = Path("backend/.env.example")

    if env_path.exists():
        print("Backend .env file already exists.")
        overwrite = input("Do you want to overwrite it? (y/N): ").strip().lower()
        if overwrite != 'y':
            print("Skipping backend environment setup.")
            return

    if not env_example_path.exists():
        print("Error: .env.example not found!")
        return False

    # Read example file
    with open(env_example_path, 'r') as f:
        env_content = f.read()

    # Generate secure API key
    api_key = generate_api_key()
    print(f"\nGenerated secure API key: {api_key}")
    print("Please save this key securely. You'll need it for API authentication.")

    # Replace placeholder with actual key
    env_content = env_content.replace("your_secure_api_key_here", api_key)

    # Ask for optional threat intelligence API key
    abuseipdb_key = input("\nEnter AbuseIPDB API key (optional, press Enter to skip): ").strip()
    if abuseipdb_key:
        env_content = env_content.replace("your_abuseipdb_api_key_here", abuseipdb_key)
    else:
        env_content = env_content.replace("ABUSEIPDB_API_KEY=your_abuseipdb_api_key_here", "ABUSEIPDB_API_KEY=")

    # Ask for CORS configuration
    cors_choice = input("\nCORS configuration:\n1. Development (wildcard '*')\n2. Production (specific origins)\nChoose [1/2]: ").strip()
    if cors_choice == "2":
        cors_origins = input("Enter allowed origins (comma-separated, e.g., http://localhost:5173,https://example.com): ").strip()
        if cors_origins:
            origins_list = ', '.join(f'"{origin.strip()}"' for origin in cors_origins.split(','))
            env_content = env_content.replace('["http://localhost:5173"]', f'[{origins_list}]')
        print(f"✓ CORS origins set to: {origins_list}")
    else:
        # Use wildcard for development
        env_content = env_content.replace('["http://localhost:5173"]', '["*"]')
        print("✓ CORS origins set to wildcard for development")

    # Write .env file
    with open(env_path, 'w') as f:
        f.write(env_content)

    print(f"✓ Backend .env file created at {env_path}")
    return True


def setup_frontend_env():
    """Setup frontend .env file."""
    frontend_dir = Path("frontend")
    env_path = frontend_dir / ".env"
    env_example_path = frontend_dir / ".env.example"

    if env_path.exists():
        print("Frontend .env file already exists.")
        overwrite = input("Do you want to overwrite it? (y/N): ").strip().lower()
        if overwrite != 'y':
            print("Skipping frontend environment setup.")
            return

    if not env_example_path.exists():
        print("Error: frontend/.env.example not found!")
        return False

    # Read example file
    with open(env_example_path, 'r') as f:
        env_content = f.read()

    # Get the API key from backend .env
    backend_env_path = Path("backend/.env")
    if backend_env_path.exists():
        with open(backend_env_path, 'r') as f:
            for line in f:
                if line.startswith("API_KEY="):
                    api_key = line.split("=")[1].strip()
                    env_content = env_content.replace("your_secure_api_key_here", api_key)
                    break

    # Write frontend .env file
    with open(env_path, 'w') as f:
        f.write(env_content)

    print(f"✓ Frontend .env file created at {env_path}")
    return True


def setup_directories():
    """Create necessary directories."""
    directories = ["backend/data", "backend/data/logs", "backend/ml/models", "backend/ml/data"]
    for directory in directories:
        Path(directory).mkdir(parents=True, exist_ok=True)
        print(f"✓ Directory created: {directory}")


def initialize_database():
    """Initialize the database with migrations."""
    print("\nInitializing database...")
    try:
        import subprocess
        result = subprocess.run(
            ["python", "-m", "alembic", "upgrade", "head"],
            cwd="backend",
            capture_output=True,
            text=True
        )
        if result.returncode == 0:
            print("✓ Database initialized successfully")
            return True
        else:
            print(f"✗ Database initialization failed: {result.stderr}")
            return False
    except Exception as e:
        print(f"✗ Error running database migrations: {e}")
        return False


def main():
    """Main setup function."""
    print("=" * 60)
    print("AI-Powered Stateful Personal Firewall - Setup")
    print("=" * 60)

    # Check if we're in the right directory
    if not Path("backend/requirements.txt").exists():
        print("Error: Please run this script from the project root directory.")
        sys.exit(1)

    print("\nThis script will help you set up the firewall environment.")
    print("It will create configuration files and initialize the database.\n")

    # Setup directories
    print("Creating necessary directories...")
    setup_directories()

    # Setup backend environment
    print("\nSetting up backend environment...")
    setup_backend_env()

    # Setup frontend environment
    print("\nSetting up frontend environment...")
    setup_frontend_env()

    # Initialize database
    print("\nInitializing database...")
    initialize_database()

    print("\n" + "=" * 60)
    print("Setup complete!")
    print("=" * 60)
    print("\nNext steps:")
    print("1. Install Python dependencies: cd backend && pip install -r requirements.txt")
    print("2. Install frontend dependencies: cd frontend && npm install")
    print("3. Start the backend: cd backend && python -m api.main")
    print("4. Start the frontend (in another terminal): cd frontend && npm run dev")
    print("\nFor production deployment, see README.md")


if __name__ == "__main__":
    main()