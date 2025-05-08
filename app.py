from flask import Flask, render_template, request, jsonify, session
import os
from datetime import datetime
import uuid
import tempfile
from faster_whisper import WhisperModel

# Import our custom modules
from config import Config
from claude_service import ClaudeService
from conversation import ConversationManager
from helpers import log_conversation


# Text to Speech (TTS) and Speech to Text (STT) services
import edge_tts
import asyncio
import base64
import io
from langdetect import detect, LangDetectException

# Initialize Flask app
app = Flask(__name__)
app.config.from_object(Config)
app.secret_key = app.config['SECRET_KEY']

# Initialize services
claude_service = ClaudeService(api_key=app.config['CLAUDE_API_KEY'])
conversation_manager = ConversationManager()

# Initialize the Faster Whisper model
# You can choose different model sizes: "tiny", "base", "small", "medium", "large-v2"
model_size = "base"
try:
    model = WhisperModel(model_size, device="cpu", compute_type="int8")
    app.logger.info(f"WhisperModel initialized with size: {model_size}")
except Exception as e:
    app.logger.error(f"Failed to initialize WhisperModel: {str(e)}")
    model = None

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

@app.route('/api/transcribe', methods=['POST'])
def transcribe():
    if model is None:
        return jsonify({'error': 'Speech recognition model not available'}), 500
        
    if 'audio' not in request.files:
        return jsonify({'error': 'No audio file provided'}), 400

    audio_file = request.files['audio']
    
    # Check if the file is empty
    if audio_file.filename == '':
        return jsonify({'error': 'Empty audio file'}), 400

    # Create a temporary file to store the uploaded audio
    temp_audio_path = None
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix='.wav') as temp_audio:
            audio_file.save(temp_audio.name)
            temp_audio_path = temp_audio.name
        
        # Log file info for debugging
        file_size = os.path.getsize(temp_audio_path)
        app.logger.info(f"Audio file saved: {temp_audio_path}, size: {file_size} bytes")
        
        if file_size == 0:
            os.unlink(temp_audio_path)
            return jsonify({'error': 'Empty audio file (zero bytes)'}), 400

        # Transcribe the audio using Faster Whisper
        segments, info = model.transcribe(temp_audio_path, beam_size=5)

        # Extract the transcription
        transcript = ""
        for segment in segments:
            transcript += segment.text + " "

        # Clean up the temporary file
        os.unlink(temp_audio_path)
        
        if not transcript.strip():
            return jsonify({'transcript': '', 'message': 'No speech detected'}), 200

        return jsonify({'transcript': transcript.strip()})

    except Exception as e:
        app.logger.error(f"Error transcribing audio: {str(e)}")
        # Clean up the temporary file in case of error
        if temp_audio_path and os.path.exists(temp_audio_path):
            os.unlink(temp_audio_path)
        return jsonify({'error': f'Transcription error: {str(e)}'}), 500

LANGUAGE_TO_VOICE = {
    'en': 'en-US-AriaNeural',      # English
    'es': 'es-ES-ElviraNeural',    # Spanish
    'fr': 'fr-FR-DeniseNeural',    # French
    'zh': 'zh-CN-XiaoxiaoNeural',  # Chinese
    'ar': 'ar-SA-ZariyahNeural',   # Arabic
    'pt': 'pt-BR-FranciscaNeural', # Portuguese
    'de': 'de-DE-KatjaNeural',     # German
    'it': 'it-IT-ElsaNeural',      # Italian
    'ja': 'ja-JP-NanamiNeural',    # Japanese
    'ko': 'ko-KR-SunHiNeural',     # Korean
    'ru': 'ru-RU-SvetlanaNeural',  # Russian
    'hi': 'hi-IN-SwaraNeural',     # Hindi
    'tr': 'tr-TR-EmelNeural',      # Turkish
    'nl': 'nl-NL-ColetteNeural',   # Dutch
    'pl': 'pl-PL-AgnieszkaNeural', # Polish
    'sv': 'sv-SE-SofieNeural',     # Swedish
    'el': 'el-GR-AthinaNeural',    # Greek
    'he': 'he-IL-HilaNeural',      # Hebrew
    'id': 'id-ID-GadisNeural',     # Indonesian
    'vi': 'vi-VN-HoaiMyNeural',    # Vietnamese
    'th': 'th-TH-AcharaNeural',    # Thai
}

# Default voice if language detection fails
DEFAULT_VOICE = 'en-US-AriaNeural'

# Add these new routes to your app.py
@app.route('/detect-language', methods=['POST'])
def detect_language():
    try:
        data = request.json
        text = data.get('text', '')
        
        if not text.strip():
            return jsonify({'language': 'unknown', 'voice': DEFAULT_VOICE})
        
        # Detect language
        lang_code = detect(text)
        voice = LANGUAGE_TO_VOICE.get(lang_code, DEFAULT_VOICE)
        
        # Get readable language name
        language_names = {
            'en': 'English',
            'es': 'Spanish',
            'fr': 'French',
            'zh': 'Chinese',
            'ar': 'Arabic',
            'pt': 'Portuguese',
            'de': 'German',
            'it': 'Italian',
            'ja': 'Japanese',
            'ko': 'Korean',
            'ru': 'Russian',
            'hi': 'Hindi',
            'tr': 'Turkish',
            'nl': 'Dutch',
            'pl': 'Polish',
            'sv': 'Swedish',
            'el': 'Greek',
            'he': 'Hebrew',
            'id': 'Indonesian',
            'vi': 'Vietnamese',
            'th': 'Thai',
        }
        
        language_name = language_names.get(lang_code, 'Unknown')
        
        return jsonify({
            'language_code': lang_code,
            'language': language_name,
            'voice': voice
        })
    except LangDetectException:
        return jsonify({'language': 'unknown', 'voice': DEFAULT_VOICE})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/text-to-speech', methods=['POST'])
def text_to_speech():
    try:
        data = request.json
        text = data.get('text', '')
        voice = data.get('voice', DEFAULT_VOICE)
        
        # Use asyncio to handle the async Edge-TTS call
        audio_data = asyncio.run(generate_speech(text, voice))
        
        # Return the audio data as base64
        encoded_audio = base64.b64encode(audio_data).decode('utf-8')
        return jsonify({'audio': encoded_audio})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

async def generate_speech(text, voice):
    communicate = edge_tts.Communicate(text, voice)
    audio_data = io.BytesIO()
    
    # Stream audio data directly to memory instead of file
    async for chunk in communicate.stream():
        if chunk["type"] == "audio":
            audio_data.write(chunk["data"])
    
    audio_data.seek(0)
    return audio_data.read()

if __name__ == '__main__':
    app.run(debug=app.config['DEBUG'], host='0.0.0.0', port=5000)