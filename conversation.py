from datetime import datetime
from config import Config

class ConversationManager:
    """Manages chat conversation history."""
    
    def __init__(self):
        """Initialize the conversation manager."""
        # In-memory storage for conversations
        # In a production app, this should use a database
        self.conversations = {}
        self.max_history = Config.MAX_CONVERSATION_HISTORY
    
    def create_conversation(self, user_id, system_message=None):
        """
        Create a new conversation for a user.
        
        Args:
            user_id (str): Unique identifier for the user
            system_message (str, optional): System message for Claude
            
        Returns:
            list: The new conversation
        """
        conversation = []
        
        # Add system message if provided
        if system_message:
            conversation.append({
                "role": "system",
                "content": system_message,
                "timestamp": datetime.now().isoformat()
            })
        
        self.conversations[user_id] = conversation
        return conversation
    
    def get_conversation(self, user_id):
        """
        Get the conversation history for a user.
        
        Args:
            user_id (str): Unique identifier for the user
            
        Returns:
            list: Conversation history or None if not found
        """
        return self.conversations.get(user_id)
    
    def add_message(self, user_id, role, content):
        """
        Add a message to a user's conversation.
        
        Args:
            user_id (str): Unique identifier for the user
            role (str): Message role ('user', 'assistant', or 'system')
            content (str): Message content
            
        Returns:
            list: Updated conversation
        """
        if user_id not in self.conversations:
            self.create_conversation(user_id)
        
        # Add the new message
        self.conversations[user_id].append({
            "role": role,
            "content": content,
            "timestamp": datetime.now().isoformat()
        })
        
        # Trim conversation if it exceeds max history (but keep system message)
        conversation = self.conversations[user_id]
        if len(conversation) > self.max_history + 1:
            # Keep the system message (if any) at index 0
            if conversation[0]["role"] == "system":
                self.conversations[user_id] = [conversation[0]] + conversation[-(self.max_history):]
            else:
                self.conversations[user_id] = conversation[-(self.max_history):]
        
        return self.conversations[user_id]
    
    def delete_conversation(self, user_id):
        """
        Delete a user's conversation history.
        
        Args:
            user_id (str): Unique identifier for the user
            
        Returns:
            bool: True if deleted, False if not found
        """
        if user_id in self.conversations:
            del self.conversations[user_id]
            return True
        return False
    
    def get_conversation_for_claude(self, user_id):
        """
        Get the conversation in the format expected by Claude API.
        
        Args:
            user_id (str): Unique identifier for the user
            
        Returns:
            list: Conversation formatted for Claude API
        """
        conversation = self.get_conversation(user_id)
        if not conversation:
            return []
        
        # Format for Claude API (exclude timestamps)
        return [
            {"role": msg["role"], "content": msg["content"]}
            for msg in conversation
        ]