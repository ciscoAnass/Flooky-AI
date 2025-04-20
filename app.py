from flask import Flask, render_template, request, jsonify, session
import os
from datetime import datetime
import uuid

# Import our custom modules
from config import Config
from claude_service import ClaudeService
from conversation import ConversationManager
from helpers import log_conversation

# Initialize Flask app
app = Flask(__name__)
app.config.from_object(Config)
app.secret_key = app.config['SECRET_KEY']

# Initialize services
claude_service = ClaudeService(api_key=app.config['CLAUDE_API_KEY'])
conversation_manager = ConversationManager()

@app.route('/')
def home():
    # Generate a session ID if not present
    if 'user_id' not in session:
        session['user_id'] = str(uuid.uuid4())
    
    return render_template('index.html')

@app.route('/about')
def about():
    return render_template('about.html')
@app.route('/donate')
def donate():
    return render_template('donation.html')
@app.route('/contact')
def contact():
    """Render the contact page."""
    return render_template('contact.html')

# Optionally, if you want to handle form submissions:
@app.route('/api/contact', methods=['POST'])
def handle_contact():
    """Handle contact form submissions."""
    # In a real implementation, you would:
    # 1. Get the form data from request.json
    # 2. Validate the data
    # 3. Send an email or save to database
    # 4. Return a success or error response
    
    data = request.json
    
    # Simple validation
    if not data.get('name') or not data.get('email') or not data.get('message'):
        return jsonify({'success': False, 'error': 'Missing required fields'}), 400
    
    try:
        # Send email logic would go here
        # For example, using Flask-Mail:
        # msg = Message(
        #     subject=f"Flooky AI Contact: {data.get('subject', 'No Subject')}",
        #     sender=app.config['MAIL_DEFAULT_SENDER'],
        #     recipients=["hello@flooky.space"],
        #     body=f"From: {data['name']} ({data['email']})\n\n{data['message']}"
        # )
        # mail.send(msg)
        
        # For now, just log it
        app.logger.info(f"Contact form submission from {data.get('name')} ({data.get('email')})")
        
        return jsonify({'success': True}), 200
    except Exception as e:
        app.logger.error(f"Error processing contact form: {str(e)}")
        return jsonify({'success': False, 'error': 'Server error'}), 500

@app.route('/api/chat', methods=['POST'])
def chat():
    data = request.json
    user_message = data['message']
    user_id = session.get('user_id', str(uuid.uuid4()))
    
    # Get or create conversation history
    conversation = conversation_manager.get_conversation(user_id)
    if not conversation:
        # Initialize with system message for chatbot personality
        conversation = conversation_manager.create_conversation(
            user_id,
            system_message="You are a friendly chatbot that responds with short sentences and uses emojis frequently. Keep your responses brief and cheerful!"
        )
    
    # Add user message to history
    conversation_manager.add_message(user_id, "user", user_message)
    
    # Get response from Claude
    try:
        assistant_message = claude_service.get_response(conversation)
        
        # Store Claude's response
        conversation_manager.add_message(user_id, "assistant", assistant_message)
        
        # Log the conversation (for analysis/debugging)
        log_conversation(user_id, user_message, assistant_message)
        
        return jsonify({
            'message': assistant_message,
            'conversation_id': user_id
        })
    
    except Exception as e:
        app.logger.error(f"Error getting response from Claude: {str(e)}")
        return jsonify({
            'message': "Sorry, I'm having trouble connecting right now. Please try again in a moment! 😅",
            'error': str(e)
        }), 500

@app.route('/api/reset', methods=['POST'])
def reset_conversation():
    user_id = session.get('user_id', str(uuid.uuid4()))
    conversation_manager.delete_conversation(user_id)
    
    return jsonify({
        'status': 'success',
        'message': 'Conversation reset successfully'
    })

if __name__ == '__main__':
    app.run(debug=app.config['DEBUG'], host='0.0.0.0', port=5000)