"""
Open Notebook - Shared Configuration Module
Production-ready configuration with environment variable support.
"""

import os
import sys
from pathlib import Path

# Try to load python-dotenv if available
try:
    from dotenv import load_dotenv
    # Load .env from multiple possible locations
    possible_env_paths = [
        Path(__file__).parent.parent / '.env',           # skill root
        Path(__file__).parent.parent.parent / '.env',      # .opencode/skills/
        Path(__file__).parent.parent.parent.parent / '.env',  # .opencode/
        Path(__file__).parent.parent.parent.parent.parent / '.env',  # project root
        Path.cwd() / '.env',                               # current working directory
    ]
    for env_path in possible_env_paths:
        if env_path.exists():
            load_dotenv(env_path)
            break
except ImportError:
    pass


def ensure_prefix(identifier: str, prefix: str) -> str:
    """Ensure an ID has the required table prefix (e.g., 'notebook:').

    The SurrealDB backend requires fully-qualified IDs like
    `notebook:uijsrkxorg0t77wl243z`. Bare UUIDs cause 500 errors.
    If the ID already contains a colon, return it as-is.
    Otherwise, prefix it with `<prefix>:`.

    Args:
        identifier: The ID string (bare UUID or already prefixed)
        prefix: The table prefix without colon (e.g., 'notebook', 'source')

    Returns:
        Fully-qualified ID string
    """
    if not identifier or not isinstance(identifier, str):
        return identifier
    if ':' in identifier:
        return identifier
    return f"{prefix}:{identifier}"


def get_config():
    """Load configuration from environment variables.
    
    Required:
        OPEN_NOTEBOOK_URL: Base URL (e.g., https://<your-domain.com>)
        OPEN_NOTEBOOK_PASSWORD: Authentication password
    
    Optional:
        OPEN_NOTEBOOK_INSECURE: Set to 'true' to disable SSL verification
    """
    url = os.getenv('OPEN_NOTEBOOK_URL')
    password = os.getenv('OPEN_NOTEBOOK_PASSWORD')
    
    if not url:
        print("Error: OPEN_NOTEBOOK_URL not set.", file=sys.stderr)
        print("Set it via environment variable or .env file:", file=sys.stderr)
        print("  export OPEN_NOTEBOOK_URL='https://<your-domain.com>'", file=sys.stderr)
        sys.exit(1)
    
    if not password:
        print("Error: OPEN_NOTEBOOK_PASSWORD not set.", file=sys.stderr)
        print("Set it via environment variable or .env file:", file=sys.stderr)
        print("  export OPEN_NOTEBOOK_PASSWORD='your-password'", file=sys.stderr)
        sys.exit(1)
    
    # Normalize URL
    url = url.rstrip('/')
    if not url.startswith('http'):
        url = f"https://{url}"
    
    return {
        'base_url': url,
        'api_url': f"{url}/api",
        'password': password,
        'insecure': os.getenv('OPEN_NOTEBOOK_INSECURE', '').lower() == 'true',
    }


if __name__ == '__main__':
    config = get_config()
    print(f"URL: {config['base_url']}")
    print(f"API: {config['api_url']}")
    print(f"Password: {'*' * len(config['password'])}")
