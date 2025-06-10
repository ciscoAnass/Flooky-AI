import os
from werkzeug.utils import secure_filename
import PyPDF2
import docx
import requests
from io import BytesIO
from config import Config

class HRHelper:
    """Service for processing CVs and finding the best candidates."""
    
    def __init__(self, api_key=None):
        self.api_key = api_key or Config.CLAUDE_API_KEY
        self.model = "claude-3-5-haiku-20241022"
        self.allowed_extensions = {'pdf', 'doc', 'docx'}
    
    def allowed_file(self, filename):
        """Check if file extension is allowed."""
        return '.' in filename and \
               filename.rsplit('.', 1)[1].lower() in self.allowed_extensions
    
    def extract_text_from_pdf(self, file_stream):
        """Extract text from PDF file."""
        try:
            pdf_reader = PyPDF2.PdfReader(file_stream)
            text = ""
            for page in pdf_reader.pages:
                text += page.extract_text() + "\n"
            return text
        except Exception as e:
            return f"Error reading PDF: {str(e)}"
    
    def extract_text_from_docx(self, file_stream):
        """Extract text from DOCX file."""
        try:
            doc = docx.Document(file_stream)
            text = ""
            for paragraph in doc.paragraphs:
                text += paragraph.text + "\n"
            return text
        except Exception as e:
            return f"Error reading DOCX: {str(e)}"
    
    def extract_text_from_doc(self, file_path):
        """Extract text from DOC file (basic implementation)."""
        try:
            # For .doc files, you might need python-docx2txt or other libraries
            # This is a simplified version
            return "DOC file processing requires additional libraries. Please convert to DOCX or PDF."
        except Exception as e:
            return f"Error reading DOC: {str(e)}"
    
    def process_cv_files(self, files):
        """Process uploaded CV files and extract text."""
        all_cv_texts = []
        
        for file in files:
            if file and self.allowed_file(file.filename):
                filename = secure_filename(file.filename)
                file_extension = filename.rsplit('.', 1)[1].lower()
                
                # Read file content
                file_content = file.read()
                file_stream = BytesIO(file_content)
                
                # Extract text based on file type
                if file_extension == 'pdf':
                    text = self.extract_text_from_pdf(file_stream)
                elif file_extension == 'docx':
                    text = self.extract_text_from_docx(file_stream)
                elif file_extension == 'doc':
                    # For DOC files, we'll return a message
                    text = self.extract_text_from_doc(None)
                else:
                    text = "Unsupported file format"
                
                all_cv_texts.append(f"CV: {filename}\n{text}")
        
        # Join all CV texts with separator
        combined_text = "\n---------------------------------\n".join(all_cv_texts)
        return combined_text
    
    def analyze_cvs_with_claude(self, job_role, cv_texts, top_count):
        """Send CV texts to Claude API for analysis."""
        try:
            prompt = f"""
            I am looking for candidates for the position: {job_role}

            Below are {len(cv_texts.split('---------------------------------'))} CVs separated by dashes:

            {cv_texts}

            Please analyze these CVs and select the TOP {top_count} best candidates for the {job_role} position based on:
            - Work experience relevance
            - Education background
            - Skills match
            - Overall qualifications

            For each selected candidate, please provide the following information in this exact format:

            Candidate X:
            Full Name: [Extract full name]
            Email: [Extract email or N/A if not provided]
            Phone Number: [Extract phone number or N/A if not provided]
            Years of Experience: [Calculate or estimate years of experience]
            Education: [Highest education level and field]
            LinkedIn: [Extract LinkedIn profile or N/A if not provided]
            Website: [Extract personal website or N/A if not provided]

            Please only return the top {top_count} candidates in the format above, ranking them from best to least suitable.
            """

            # Headers for API call
            headers = {
                "Content-Type": "application/json",
                "x-api-key": self.api_key,
                "anthropic-version": "2023-06-01"
            }
            
            # Data payload
            data = {
                "model": self.model,
                "max_tokens": 4000,
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
                return f"API Error: {response.status_code} - {response.text}"
            
            # Parse the response
            resp_json = response.json()
            
            # Extract content from the response
            content = resp_json.get("content", [])
            response_text = ""
            
            for item in content:
                if item.get("type") == "text":
                    response_text += item.get("text", "")
            
            return response_text
        
        except Exception as e:
            return f"Error analyzing CVs: {str(e)}"
    
    def analyze_cvs(self, job_role, files, top_count):
        """Complete CV analysis pipeline."""
        try:
            if not job_role:
                return {'error': 'Job role is required'}
            
            if not files or all(file.filename == '' for file in files):
                return {'error': 'Please upload at least one CV file'}
            
            # Process CV files
            cv_texts = self.process_cv_files(files)
            
            if not cv_texts:
                return {'error': 'No valid CV files found'}
            
            # Analyze with Claude
            analysis_result = self.analyze_cvs_with_claude(job_role, cv_texts, top_count)
            
            return {
                'success': True,
                'job_role': job_role,
                'top_count': top_count,
                'files_processed': len([f for f in files if f.filename != '']),
                'analysis': analysis_result
            }
        
        except Exception as e:
            return {'error': f'An error occurred: {str(e)}'}