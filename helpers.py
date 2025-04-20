import os
import json
from datetime import datetime
from config import Config

def log_conversation(user_id, user_message, assistant_message):
    """
    Log conversation for analysis or debugging.
    
    Args:
        user_id (str): User identifier
        user_message (str): Message from the user
        assistant_message (str): Response from the assistant
    """
    if not Config.LOG_CONVERSATIONS:
        return
    
    # Create logs directory if it doesn't exist
    os.makedirs('logs', exist_ok=True)
    
    timestamp = datetime.now().isoformat()
    log_entry = {
        'timestamp': timestamp,
        'user_id': user_id,
        'user_message': user_message,
        'assistant_message': assistant_message
    }
    
    # Log to a daily log file
    log_date = datetime.now().strftime('%Y-%m-%d')
    log_file = f'logs/chat_{log_date}.log'
    
    with open(log_file, 'a', encoding='utf-8') as f:
        f.write(json.dumps(log_entry) + '\n')

def sanitize_input(text):
    """
    Sanitize user input to prevent malicious content.
    
    Args:
        text (str): Input text to sanitize
        
    Returns:
        str: Sanitized text
    """
    # Basic sanitation - remove control characters
    result = ''.join(char for char in text if ord(char) >= 32 or char == '\n')
    
    # Trim excessive whitespace
    result = ' '.join(result.split())
    
    return result

def get_conversation_stats(user_id, conversation_manager):
    """
    Get stats about a user's conversation.
    
    Args:
        user_id (str): User identifier
        conversation_manager (ConversationManager): Conversation manager instance
        
    Returns:
        dict: Statistics about the conversation
    """
    conversation = conversation_manager.get_conversation(user_id)
    if not conversation:
        return {
            'message_count': 0,
            'user_messages': 0,
            'assistant_messages': 0,
            'first_message_time': None,
            'last_message_time': None
        }
    
    # Count different message types
    user_messages = sum(1 for msg in conversation if msg['role'] == 'user')
    assistant_messages = sum(1 for msg in conversation if msg['role'] == 'assistant')
    
    # Get timestamps
    timestamps = [datetime.fromisoformat(msg['timestamp']) for msg in conversation 
                 if 'timestamp' in msg]
    
    first_time = min(timestamps) if timestamps else None
    last_time = max(timestamps) if timestamps else None
    
    return {
        'message_count': len(conversation),
        'user_messages': user_messages,
        'assistant_messages': assistant_messages,
        'first_message_time': first_time.isoformat() if first_time else None,
        'last_message_time': last_time.isoformat() if last_time else None
    }