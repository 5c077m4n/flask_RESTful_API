"""Configuration file.
"""
import secrets


DEBUG, HOST, PORT = True, '127.0.0.1', 8000
SECERT_KEY = secrets.token_urlsafe(64)
DEFAULT_RATE = '100/hour'
