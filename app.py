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
from video_analyzer import VideoAnalyzer
from hr_helper import HRHelper
from bill_processor import BillProcessor
from contract_processor import ContractProcessor
from financial_processor import FinancialProcessor

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

# Initialize all AI services
try:
    video_analyzer = VideoAnalyzer(api_key=app.config['CLAUDE_API_KEY'])
    hr_helper = HRHelper(api_key=app.config['CLAUDE_API_KEY'])
    bill_processor = BillProcessor(api_key=app.config['CLAUDE_API_KEY'])
    contract_processor = ContractProcessor(api_key=app.config['CLAUDE_API_KEY'])
    financial_processor = FinancialProcessor(api_key=app.config['CLAUDE_API_KEY'])
    print("All AI services initialized successfully")
except Exception as e:
    print(f"Error initializing AI services: {e}")
    video_analyzer = None
    hr_helper = None
    bill_processor = None
    contract_processor = None
    financial_processor = None

# Initialize the Faster Whisper model
model_size = "base"
try:
    model = WhisperModel(model_size, device="cpu", compute_type="int8")
    app.logger.info(f"WhisperModel initialized with size: {model_size}")
except Exception as e:
    app.logger.error(f"Failed to initialize WhisperModel: {str(e)}")
    model = None

@app.route('/')
def home():
    if 'user_id' not in session:
        session['user_id'] = str(uuid.uuid4())
    return render_template('index.html')

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/contact')
def contact():
    return render_template('contact.html')

@app.route('/tools')
def tools():
    return render_template('tools.html')

# Video Summary App
@app.route('/app/flooky-video-summary')
def video_summary():
    return render_template('video_summary.html')

@app.route('/app/flooky-video-summary/analyze', methods=['POST'])
def analyze_video():
    if video_analyzer is None:
        return jsonify({'error': 'Video analyzer not available'}), 500
    
    data = request.get_json()
    video_url = data.get('video_url')
    
    if not video_url:
        return jsonify({'error': 'No video URL provided'}), 400
    
    result = video_analyzer.analyze_video(video_url)
    
    if 'error' in result:
        return jsonify(result), 500
    
    return jsonify(result)

# HR Helper App
@app.route('/app/flooky-hr-helper')
def hr_helper_page():
    return render_template('hr_helper.html')

@app.route('/app/flooky-hr-helper/analyze', methods=['POST'])
def analyze_cvs():
    if hr_helper is None:
        return jsonify({'error': 'HR Helper not available'}), 500
    
    job_role = request.form.get('job_role')
    top_count = request.form.get('top_count')
    files = request.files.getlist('cv_files')
    
    result = hr_helper.analyze_cvs(job_role, files, top_count)
    
    if 'error' in result:
        return jsonify(result), 500
    
    return jsonify(result)

# Bill Analyzer App
@app.route('/app/flooky-bill-analyzer')
def bill_analyzer_page():
    return render_template('bill_analyzer.html')

@app.route('/app/flooky-bill-analyzer/upload', methods=['POST'])
def upload_bill():
    if bill_processor is None:
        return jsonify({'error': 'Bill processor not available'}), 500
    
    if 'file' not in request.files:
        return jsonify({'error': 'No file provided'}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400
    
    # Save file temporarily
    from werkzeug.utils import secure_filename
    filename = secure_filename(file.filename)
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S_')
    filename = timestamp + filename
    
    temp_dir = tempfile.mkdtemp()
    filepath = os.path.join(temp_dir, filename)
    file.save(filepath)
    
    # Process the bill
    result = bill_processor.process_bill(filepath)
    
    # Clean up
    try:
        os.remove(filepath)
        os.rmdir(temp_dir)
    except:
        pass
    
    if result['success']:
        return jsonify({
            'success': True,
            'data': result['data']
        })
    else:
        return jsonify({
            'success': False,
            'error': result['error']
        }), 500

# Legal Document Checker App
@app.route('/app/flooky-legal-checker')
def legal_checker_page():
    return render_template('contract_analyzer.html')

@app.route('/app/flooky-legal-checker/upload', methods=['POST'])
def upload_contract():
    if contract_processor is None:
        return jsonify({'error': 'Contract processor not available'}), 500
    
    if 'file' not in request.files:
        return jsonify({'error': 'No file provided'}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400
    
    # Save file temporarily
    from werkzeug.utils import secure_filename
    filename = secure_filename(file.filename)
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S_')
    filename = timestamp + filename
    
    temp_dir = tempfile.mkdtemp()
    filepath = os.path.join(temp_dir, filename)
    file.save(filepath)
    
    # Process the contract
    result = contract_processor.process_contract(filepath)
    
    # Clean up
    try:
        os.remove(filepath)
        os.rmdir(temp_dir)
    except:
        pass
    
    if result['success']:
        return jsonify({
            'success': True,
            'data': result['data']
        })
    else:
        return jsonify({
            'success': False,
            'error': result['error']
        }), 500

# Financial Advisor App
@app.route('/app/flooky-financial-advisor')
def financial_advisor_page():
    return render_template('financial_advisor.html')

@app.route('/app/flooky-financial-advisor/analyze', methods=['POST'])
def analyze_finances():
    if financial_processor is None:
        return jsonify({'error': 'Financial processor not available'}), 500
    
    if 'file' not in request.files:
        return jsonify({'error': 'No file provided'}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400
    
    # Get form data
    financial_goal = request.form.get('financial_goal', '')
    goal_amount = request.form.get('goal_amount', '')
    goal_timeframe = request.form.get('goal_timeframe', '')
    
    if not financial_goal:
        return jsonify({'error': 'Financial goal is required'}), 400
    
    # Save file temporarily
    from werkzeug.utils import secure_filename
    filename = secure_filename(file.filename)
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S_')
    filename = timestamp + filename
    
    temp_dir = tempfile.mkdtemp()
    filepath = os.path.join(temp_dir, filename)
    file.save(filepath)
    
    # Process the financial data
    result = financial_processor.process_financial_data(filepath, financial_goal, goal_amount, goal_timeframe)
    
    # Clean up
    try:
        os.remove(filepath)
        os.rmdir(temp_dir)
    except:
        pass
    
    if result['success']:
        return jsonify({
            'success': True,
            'data': result['data']
        })
    else:
        return jsonify({
            'success': False,
            'error': result['error']
        }), 500

# Contact form handler
@app.route('/api/contact', methods=['POST'])
def handle_contact():
    data = request.json
    
    if not data.get('name') or not data.get('email') or not data.get('message'):
        return jsonify({'success': False, 'error': 'Missing required fields'}), 400
    
    try:
        app.logger.info(f"Contact form submission from {data.get('name')} ({data.get('email')})")
        return jsonify({'success': True}), 200
    except Exception as e:
        app.logger.error(f"Error processing contact form: {str(e)}")
        return jsonify({'success': False, 'error': 'Server error'}), 500

# Chat functionality
@app.route('/api/chat', methods=['POST'])
def chat():
    data = request.json
    user_message = data['message']
    user_id = session.get('user_id', str(uuid.uuid4()))
    
    conversation = conversation_manager.get_conversation(user_id)
    if not conversation:
        conversation = conversation_manager.create_conversation(
            user_id,
            system_message="You are a friendly chatbot that responds with short sentences and uses emojis frequently. Keep your responses brief and cheerful!"
        )
    
    conversation_manager.add_message(user_id, "user", user_message)
    
    try:
        assistant_message = claude_service.get_response(conversation)
        conversation_manager.add_message(user_id, "assistant", assistant_message)
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
    
    if audio_file.filename == '':
        return jsonify({'error': 'Empty audio file'}), 400

    temp_audio_path = None
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix='.wav') as temp_audio:
            audio_file.save(temp_audio.name)
            temp_audio_path = temp_audio.name
        
        file_size = os.path.getsize(temp_audio_path)
        app.logger.info(f"Audio file saved: {temp_audio_path}, size: {file_size} bytes")
        
        if file_size == 0:
            os.unlink(temp_audio_path)
            return jsonify({'error': 'Empty audio file (zero bytes)'}), 400

        segments, info = model.transcribe(temp_audio_path, beam_size=5)

        transcript = ""
        for segment in segments:
            transcript += segment.text + " "

        os.unlink(temp_audio_path)
        
        if not transcript.strip():
            return jsonify({'transcript': '', 'message': 'No speech detected'}), 200

        return jsonify({'transcript': transcript.strip()})

    except Exception as e:
        app.logger.error(f"Error transcribing audio: {str(e)}")
        if temp_audio_path and os.path.exists(temp_audio_path):
            os.unlink(temp_audio_path)
        return jsonify({'error': f'Transcription error: {str(e)}'}), 500

LANGUAGE_TO_VOICE = {
    'en': 'en-US-AriaNeural',
    'es': 'es-ES-ElviraNeural',
    'fr': 'fr-FR-DeniseNeural',
    'zh': 'zh-CN-XiaoxiaoNeural',
    'ar': 'ar-SA-ZariyahNeural',
    'pt': 'pt-BR-FranciscaNeural',
    'de': 'de-DE-KatjaNeural',
    'it': 'it-IT-ElsaNeural',
    'ja': 'ja-JP-NanamiNeural',
    'ko': 'ko-KR-SunHiNeural',
    'ru': 'ru-RU-SvetlanaNeural',
    'hi': 'hi-IN-SwaraNeural',
    'tr': 'tr-TR-EmelNeural',
    'nl': 'nl-NL-ColetteNeural',
    'pl': 'pl-PL-AgnieszkaNeural',
    'sv': 'sv-SE-SofieNeural',
    'el': 'el-GR-AthinaNeural',
    'he': 'he-IL-HilaNeural',
    'id': 'id-ID-GadisNeural',
    'vi': 'vi-VN-HoaiMyNeural',
    'th': 'th-TH-AcharaNeural',
}

DEFAULT_VOICE = 'en-US-AriaNeural'

@app.route('/detect-language', methods=['POST'])
def detect_language():
    try:
        data = request.json
        text = data.get('text', '')
        
        if not text.strip():
            return jsonify({'language': 'unknown', 'voice': DEFAULT_VOICE})
        
        lang_code = detect(text)
        voice = LANGUAGE_TO_VOICE.get(lang_code, DEFAULT_VOICE)
        
        language_names = {
            'en': 'English', 'es': 'Spanish', 'fr': 'French', 'zh': 'Chinese',
            'ar': 'Arabic', 'pt': 'Portuguese', 'de': 'German', 'it': 'Italian',
            'ja': 'Japanese', 'ko': 'Korean', 'ru': 'Russian', 'hi': 'Hindi',
            'tr': 'Turkish', 'nl': 'Dutch', 'pl': 'Polish', 'sv': 'Swedish',
            'el': 'Greek', 'he': 'Hebrew', 'id': 'Indonesian', 'vi': 'Vietnamese',
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
        
        audio_data = asyncio.run(generate_speech(text, voice))
        
        encoded_audio = base64.b64encode(audio_data).decode('utf-8')
        return jsonify({'audio': encoded_audio})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

async def generate_speech(text, voice):
    communicate = edge_tts.Communicate(text, voice)
    audio_data = io.BytesIO()
    
    async for chunk in communicate.stream():
        if chunk["type"] == "audio":
            audio_data.write(chunk["data"])
    
    audio_data.seek(0)
    return audio_data.read()

if __name__ == '__main__':
    app.run(debug=app.config['DEBUG'], host='0.0.0.0', port=5000)