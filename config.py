import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class Config:
    """Configuration settings for the application."""
    
    # Flask settings
    SECRET_KEY = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')
    DEBUG = os.environ.get('DEBUG', 'True').lower() in ('true', '1', 't')
    
    # Claude API settings
    CLAUDE_API_KEY = os.environ.get('CLAUDE_API_KEY')
    # Model is hard-coded in claude_service.py to match your prompt
    MAX_TOKENS = int(os.environ.get('MAX_TOKENS', '40000'))  # Updated to match your prompt
    
    # Application settings
    MAX_CONVERSATION_HISTORY = int(os.environ.get('MAX_CONVERSATION_HISTORY', '10'))
    LOG_CONVERSATIONS = os.environ.get('LOG_CONVERSATIONS', 'True').lower() in ('true', '1', 't')
    
    # Check required environment variables
    @classmethod
    def validate(cls):
        if not cls.CLAUDE_API_KEY:
            raise ValueError("CLAUDE_API_KEY is not set in environment variables or .env file")