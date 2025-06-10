import yt_dlp
import whisper
import tempfile
import os
import json
import re
import requests
from config import Config

class VideoAnalyzer:
    def __init__(self, api_key=None):
        self.whisper_model = None
        self.api_key = api_key or Config.CLAUDE_API_KEY
        
    def load_whisper_model(self):
        """Load Whisper model for transcription"""
        if self.whisper_model is None:
            print("Loading Whisper model...")
            self.whisper_model = whisper.load_model("base")
        return self.whisper_model
    
    def download_video_audio(self, url: str) -> str:
        """Download video and extract audio"""
        temp_dir = tempfile.mkdtemp()
        
        ydl_opts = {
            'format': 'bestaudio/best',
            'outtmpl': os.path.join(temp_dir, 'video.%(ext)s'),
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'wav',
                'preferredquality': '192',
            }],
        }
        
        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([url])
            
            # Find the audio file
            for file in os.listdir(temp_dir):
                if file.endswith('.wav'):
                    audio_path = os.path.join(temp_dir, file)
                    return audio_path
                    
        except Exception as e:
            print(f"Error downloading video: {str(e)}")
            return None
    
    def transcribe_audio(self, audio_path: str) -> str:
        """Transcribe audio using Whisper"""
        try:
            model = self.load_whisper_model()
            print("Transcribing video...")
            result = model.transcribe(audio_path)
            return result["text"]
        except Exception as e:
            print(f"Error transcribing audio: {str(e)}")
            return None
        finally:
            # Clean up audio file
            if os.path.exists(audio_path):
                os.remove(audio_path)
    
    def analyze_with_claude(self, transcription: str) -> dict:
        """Analyze transcription with Claude API"""
        prompt = f"""
        As an expert fact-checker and information analyst, please thoroughly analyze this video content for accuracy, reliability, and overall quality.

        IMPORTANT: Identify and analyze ALL significant claims, facts, statistics, statements, and pieces of information presented in this video. Do not limit yourself to just a few - extract and evaluate EVERY important piece of information, including:
        - Factual claims and statements
        - Statistics and numbers mentioned
        - Historical references
        - Scientific claims
        - Personal opinions presented as facts
        - Recommendations or advice given
        - Any controversial or debatable points
        - Background information provided
        - Conclusions drawn by the presenter

        For each significant claim, fact, or piece of information presented, provide:
        1. The specific information or claim
        2. A reliability/accuracy score from 0-100 where:
           - 90-100: Completely accurate, well-sourced, verifiable
           - 70-89: Mostly accurate with minor issues or context needed
           - 50-69: Partially accurate but missing important context or nuance
           - 30-49: Misleading or significantly inaccurate
           - 0-29: False, fabricated, or dangerous misinformation
        3. A comprehensive explanation (3-4 sentences minimum) covering:
           - Why you assigned this specific score
           - What makes this information reliable or unreliable
           - Any missing context or nuance
           - Potential consequences of believing/sharing this information

        Be thorough and comprehensive - if a video contains 20 different claims or pieces of information, analyze all 20. If it contains 50, analyze all 50. Do not skip any important information.

        Also provide your expert opinion on:
        - What this video is really about and its main message
        - The overall credibility and trustworthiness of the content
        - Whether the presenter demonstrates expertise in the subject
        - Any red flags, biases, or concerning patterns you notice
        - Your personal assessment of whether viewers should trust this content
        - Recommendations for viewers (should they share it, be cautious, seek additional sources, etc.)

        Please format your response as JSON with this structure:
        {{
            "claims_analysis": [
                {{
                    "information": "The specific claim or information presented",
                    "reliability_score": 85,
                    "description": "Comprehensive 3-4 sentence analysis explaining the score, reliability factors, missing context, and potential impact of this information"
                }}
            ],
            "summary": "Detailed summary of what this video is about, its main arguments, and overall message",
            "general_assessment": "Your expert opinion on the video's credibility, the presenter's expertise, any biases or red flags, and overall trustworthiness",
            "analysis_description": "Your professional recommendation for viewers - should they trust this content, share it, be cautious, or seek additional sources? Include your reasoning and any warnings."
        }}
        
        Video content to analyze:
        {transcription}
        """
        
        try:
            print("Analyzing content with Claude AI...")
            
            # Headers for API call
            headers = {
                "Content-Type": "application/json",
                "x-api-key": self.api_key,
                "anthropic-version": "2023-06-01"
            }
            
            # Data payload
            data = {
                "model": "claude-3-5-haiku-20241022",
                "max_tokens": 4000,
                "temperature": 0,
                "messages": [{
                    "role": "user",
                    "content": prompt
                }]
            }
            
            # Make the API call
            response = requests.post(
                "https://api.anthropic.com/v1/messages",
                headers=headers,
                json=data
            )
            
            if response.status_code != 200:
                print(f"API Error: {response.status_code} - {response.text}")
                return None
            
            # Parse the response
            resp_json = response.json()
            
            # Extract content from the response
            content = resp_json.get("content", [])
            response_text = ""
            
            for item in content:
                if item.get("type") == "text":
                    response_text += item.get("text", "")
            
            # Extract JSON from response
            json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
            if json_match:
                return json.loads(json_match.group())
            else:
                # If no JSON found, try to parse the entire response
                return json.loads(response_text)
                
        except json.JSONDecodeError as e:
            print(f"Error parsing Claude response: {str(e)}")
            return None
        except Exception as e:
            print(f"Error analyzing with Claude: {str(e)}")
            return None
    
    def analyze_video(self, video_url: str) -> dict:
        """Complete video analysis pipeline"""
        try:
            # Step 1: Download audio
            print("Downloading video audio...")
            audio_path = self.download_video_audio(video_url)
            
            if not audio_path:
                return {'error': 'Failed to download video audio'}
            
            # Step 2: Transcribe
            print("Transcribing video...")
            transcription = self.transcribe_audio(audio_path)
            
            if not transcription:
                return {'error': 'Failed to transcribe video'}
            
            # Step 3: Analyze with Claude
            print("Analyzing content with Claude AI...")
            analysis = self.analyze_with_claude(transcription)
            
            if not analysis:
                return {'error': 'Failed to analyze content'}
            
            # Return results
            return {
                'success': True,
                'transcription': transcription,
                'analysis': analysis
            }
            
        except Exception as e:
            print(f"Error in video analysis: {str(e)}")
            return {'error': str(e)}
