import os
from pathlib import Path

# Base directory
BASE_DIR = Path(__file__).resolve().parent

# Paths to the encryption key and encrypted API key
ENCRYPTION_KEY_PATH = os.path.join(BASE_DIR, 'encryption_key.txt')
ENCRYPTED_API_KEY_PATH = os.path.join(BASE_DIR, 'encrypted_api_key.txt')
