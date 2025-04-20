import re
from config import Config

class ClaudeService:
    """Service for interacting with the Claude API."""
    
    def __init__(self, api_key=None):
        """Initialize the Claude service with API credentials."""
        self.api_key = api_key or Config.CLAUDE_API_KEY
        self.model = "claude-3-5-haiku-20241022"  # Keep the model as specified in your code
        self.max_tokens = Config.MAX_TOKENS
        self.temperature = 1  # As specified in your prompt
    
    def get_response(self, conversation):
        """
        Get a response from Claude based on the conversation history.
        
        Args:
            conversation (list): List of message dicts with 'role' and 'content'
            
        Returns:
            str: Claude's response text
        """
        try:
            # Check if there are any user messages
            user_messages = [msg for msg in conversation if msg["role"] == "user"]
            if not user_messages:
                return "¡Hola! ¿En qué puedo ayudarte hoy? 😊"
            
            # Format system message
            system_message = (
                "You are an AI assistant named Flooky.You should never claim to be Claude, ChatGPT, or any other AI. Always respond in whatever language. You are genius in everything specially in IT."

            )
            
            # Make API call using requests directly
            import requests
            import json
            
            # Headers for API call - Updated for Messages API
            headers = {
                "Content-Type": "application/json",
                "x-api-key": self.api_key,
                "anthropic-version": "2023-06-01"
            }
            
            # Prepare the messages array for Claude's Messages API
            messages = []
            
            # Add all conversation history (excluding system messages)
            for msg in conversation:
                if msg["role"] != "system":
                    messages.append({
                        "role": msg["role"],
                        "content": msg["content"]
                    })
            
            # Data payload for the Messages API format
            data = {
                "model": self.model,
                "system": system_message,  # System message as a separate parameter
                "messages": messages,
                "max_tokens": self.max_tokens,
                "temperature": self.temperature
            }
            
            # Make the API call using the Messages API
            response = requests.post(
                "https://api.anthropic.com/v1/messages",
                headers=headers,
                json=data
            )
            
            # Check response status
            if response.status_code != 200:
                print(f"API Error: {response.status_code} - {response.text}")
                error_details = response.text
                return f"Error: API request failed with status {response.status_code}. Details: {error_details}"
            
            # Parse the response
            resp_json = response.json()
            
            # Extract content from the Messages API response
            content = resp_json.get("content", [])
            raw_response = ""
            
            for item in content:
                if item.get("type") == "text":
                    raw_response += item.get("text", "")
            
            return raw_response
            
        except Exception as e:
            # Return a user-friendly error
            error_message = f"Error: {str(e)}"
            print(error_message)
            return f"Lo siento, estoy teniendo problemas técnicos. 😔 {error_message}"
    
    def health_check(self):
        """
        Check if the Claude API is accessible.
        
        Returns:
            bool: True if API is accessible, False otherwise
        """
        try:
            # Make a simple API call to check health
            import requests
            
            headers = {
                "Content-Type": "application/json",
                "x-api-key": self.api_key,
                "anthropic-version": "2023-06-01"
            }
            
            data = {
                "model": self.model,
                "messages": [
                    {
                        "role": "user",
                        "content": "Hello"
                    }
                ],
                "max_tokens": 10
            }
            
            response = requests.post(
                "https://api.anthropic.com/v1/messages",
                headers=headers,
                json=data
            )
            
            return response.status_code == 200
        except:
            return False