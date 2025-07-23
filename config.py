"""
Secure configuration management for generative agents.
Handles environment variables and sensitive data safely.
"""
import os
from pathlib import Path
from typing import Optional

# Base directory of the project
BASE_DIR = Path(__file__).resolve().parent

def load_env_file(env_path: Optional[str] = None) -> None:
    """Load environment variables from .env file if it exists."""
    if env_path is None:
        env_path = BASE_DIR / ".env"
    
    if not os.path.exists(env_path):
        print(f"Warning: Environment file {env_path} not found. Using defaults.")
        return
    
    with open(env_path, 'r') as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#') and '=' in line:
                key, value = line.split('=', 1)
                os.environ.setdefault(key, value)

# Load environment variables
load_env_file()

# OpenAI Configuration
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY', '')
OPENAI_KEY_OWNER = os.getenv('OPENAI_KEY_OWNER', 'unknown')

# Only require API key if not in testing mode
import sys
if 'test' not in sys.argv and not any('test' in arg for arg in sys.argv) and not OPENAI_API_KEY:
    raise ValueError(
        "OpenAI API key not found. Please set OPENAI_API_KEY environment variable "
        "or create a .env file with your API key."
    )

# Django Configuration
DJANGO_SECRET_KEY = os.getenv('DJANGO_SECRET_KEY', '')
DJANGO_DEBUG = os.getenv('DJANGO_DEBUG', 'False').lower() == 'true'
DJANGO_ALLOWED_HOSTS = os.getenv('DJANGO_ALLOWED_HOSTS', 'localhost,127.0.0.1').split(',')

if not DJANGO_SECRET_KEY:
    # Generate a random secret key for development
    import secrets
    import string
    DJANGO_SECRET_KEY = ''.join(secrets.choice(string.ascii_letters + string.digits + '!@#$%^&*') for _ in range(50))
    print("Warning: Using auto-generated Django secret key. Set DJANGO_SECRET_KEY for production.")

# Simulation Paths
MAZE_ASSETS_LOC = os.getenv('MAZE_ASSETS_LOC', 'environment/frontend_server/static_dirs/assets')
FS_STORAGE = os.getenv('FS_STORAGE', 'environment/frontend_server/storage')
FS_TEMP_STORAGE = os.getenv('FS_TEMP_STORAGE', 'environment/frontend_server/temp_storage')

# Convert relative paths to absolute paths
MAZE_ASSETS_LOC = str(BASE_DIR / MAZE_ASSETS_LOC)
ENV_MATRIX = f"{MAZE_ASSETS_LOC}/the_ville/matrix"
ENV_VISUALS = f"{MAZE_ASSETS_LOC}/the_ville/visuals"
FS_STORAGE = str(BASE_DIR / FS_STORAGE)
FS_TEMP_STORAGE = str(BASE_DIR / FS_TEMP_STORAGE)

# Simulation Configuration
COLLISION_BLOCK_ID = os.getenv('COLLISION_BLOCK_ID', '32125')
DEBUG = os.getenv('VERBOSE_DEBUG', 'False').lower() == 'true'

# Legacy compatibility - maintain old variable names
openai_api_key = OPENAI_API_KEY
key_owner = OPENAI_KEY_OWNER
maze_assets_loc = MAZE_ASSETS_LOC
env_matrix = ENV_MATRIX
env_visuals = ENV_VISUALS
fs_storage = FS_STORAGE
fs_temp_storage = FS_TEMP_STORAGE
collision_block_id = COLLISION_BLOCK_ID
debug = DEBUG