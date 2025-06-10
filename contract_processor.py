import os
import json
import logging
from typing import Dict, Any
import fitz  # PyMuPDF
import docx
import requests
import re
from datetime import datetime
from config import Config

logger = logging.getLogger(__name__)

class ContractProcessor:
    """Handles legal document processing including text extraction and AI analysis."""
    
    def __init__(self, api_key=None):
        self.api_key = api_key or Config.CLAUDE_API_KEY
        self.model = "claude-3-5-haiku-20241022"
        self.allowed_extensions = {'pdf', 'doc', 'docx', 'txt'}
    
    def process_contract(self, file_path: str) -> Dict[str, Any]:
        """Main processing function for legal documents."""
        try:
            # Extract text from file
            text = self._extract_text(file_path)
            if not text.strip():
                return {
                    'success': False,
                    'error': 'No text could be extracted from the file'
                }
            
            logger.info(f"Extracted contract text length: {len(text)} characters")
            
            # Analyze with Claude
            analysis = self._analyze_with_claude(text)
            
            return {
                'success': True,
                'data': analysis
            }
            
        except Exception as e:
            logger.error(f"Error processing contract: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def _extract_text(self, file_path: str) -> str:
        """Extract text from PDF, DOC, DOCX or TXT file."""
        file_extension = os.path.splitext(file_path)[1].lower()
        
        if file_extension == '.pdf':
            return self._extract_text_from_pdf(file_path)
        elif file_extension == '.docx':
            return self._extract_text_from_docx(file_path)
        elif file_extension == '.doc':
            return self._extract_text_from_doc(file_path)
        elif file_extension == '.txt':
            return self._extract_text_from_txt(file_path)
        else:
            raise Exception(f"Unsupported file format: {file_extension}")
    
    def _extract_text_from_pdf(self, file_path: str) -> str:
        """Extract text from PDF using PyMuPDF."""
        try:
            doc = fitz.open(file_path)
            text = ""
            for page in doc:
                text += page.get_text()
            doc.close()
            return text
        except Exception as e:
            logger.error(f"Error extracting text from PDF: {str(e)}")
            raise Exception(f"Failed to extract text from PDF: {str(e)}")
    
    def _extract_text_from_docx(self, file_path: str) -> str:
        """Extract text from DOCX using python-docx."""
        try:
            doc = docx.Document(file_path)
            text = ""
            for paragraph in doc.paragraphs:
                text += paragraph.text + "\n"
            return text
        except Exception as e:
            logger.error(f"Error extracting text from DOCX: {str(e)}")
            raise Exception(f"Failed to extract text from DOCX: {str(e)}")
    
    def _extract_text_from_doc(self, file_path: str) -> str:
        """Extract text from DOC file."""
        try:
            # For .doc files, we'll return a message suggesting conversion
            return "DOC file processing requires additional libraries. Please convert to DOCX or PDF for better results."
        except Exception as e:
            logger.error(f"Error extracting text from DOC: {str(e)}")
            raise Exception(f"Failed to extract text from DOC: {str(e)}")
    
    def _extract_text_from_txt(self, file_path: str) -> str:
        """Extract text from TXT file."""
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                return file.read()
        except Exception as e:
            logger.error(f"Error extracting text from TXT: {str(e)}")
            raise Exception(f"Failed to extract text from TXT: {str(e)}")
    
    def _analyze_with_claude(self, text: str) -> Dict[str, Any]:
        """Analyze legal document with Claude AI."""
        max_retries = 3
        retry_delay = 2
        
        for attempt in range(max_retries):
            try:
                # Legal document analysis prompt
                analysis_prompt = f"""
                As an expert legal analyst, please thoroughly analyze this legal document/contract and provide a comprehensive analysis.

                Document text:
                {text}

                Please provide your response in the following JSON format:
                {{
                    "contract_title": "Title or type of the contract",
                    "duration": "Contract duration/term (e.g., '2 years', 'permanent', 'until terminated')",
                    "parties": {{
                        "party1": "First party name/entity",
                        "party2": "Second party name/entity",
                        "relationship": "Description of the relationship (e.g., 'Employment contract between John Doe and ABC Corp')"
                    }},
                    "contract_details": "Detailed summary of what this contract covers, main obligations, and key terms",
                    "risk_assessment": {{
                        "safety_percentage": 85,
                        "risk_level": "Low/Medium/High",
                        "scam_likelihood": "Very Low/Low/Medium/High/Very High",
                        "explanation": "Detailed explanation of the risk assessment and why this percentage was assigned"
                    }},
                    "contract_explanation": "Clear explanation of the contract in simple terms, breaking down complex legal language",
                    "legal_terms_simplified": [
                        {{
                            "term": "Legal term or phrase",
                            "simple_explanation": "What this means in everyday language"
                        }}
                    ],
                    "risky_parts": [
                        {{
                            "issue": "Description of the risky clause or missing element",
                            "risk_level": "Low/Medium/High/Critical",
                            "explanation": "Why this is risky and potential consequences",
                            "location": "Where in the contract this appears"
                        }}
                    ],
                    "missing_clauses": [
                        {{
                            "clause": "Missing clause or protection",
                            "importance": "Low/Medium/High/Critical",
                            "explanation": "Why this clause is important and what risks it would mitigate"
                        }}
                    ],
                    "recommended_changes": [
                        {{
                            "change": "Specific change or addition recommended",
                            "reason": "Why this change is recommended",
                            "priority": "Low/Medium/High/Critical"
                        }}
                    ],
                    "final_recommendations": "Overall assessment and final advice for the person reviewing this contract"
                }}

                Be thorough in your analysis and focus on protecting the interests of the person asking for the review. Identify any potential red flags, unfair terms, or areas where additional protection might be needed.
                """

                # Headers for API call
                headers = {
                    "Content-Type": "application/json",
                    "x-api-key": self.api_key,
                    "anthropic-version": "2023-06-01"
                }
                
                # Analysis call
                analysis_data = {
                    "model": self.model,
                    "max_tokens": 4000,
                    "messages": [{
                        "role": "user",
                        "content": analysis_prompt
                    }]
                }
                
                response = requests.post(
                    "https://api.anthropic.com/v1/messages",
                    headers=headers,
                    json=analysis_data
                )
                
                # Handle overloaded error with retry
                if response.status_code == 529:
                    if attempt < max_retries - 1:
                        logger.warning(f"API overloaded (attempt {attempt + 1}/{max_retries}). Retrying in {retry_delay} seconds...")
                        import time
                        time.sleep(retry_delay)
                        retry_delay *= 2
                        continue
                    else:
                        raise Exception("API is currently overloaded. Please try again in a few minutes.")
                
                if response.status_code != 200:
                    raise Exception(f"API Error: {response.status_code} - {response.text}")
                
                # Parse the response
                resp_json = response.json()
                content = resp_json.get("content", [])
                analysis_text = ""
                for item in content:
                    if item.get("type") == "text":
                        analysis_text += item.get("text", "")
                
                return self._parse_claude_response(analysis_text)
                
            except Exception as e:
                if "overloaded" in str(e).lower() and attempt < max_retries - 1:
                    logger.warning(f"Retrying due to overload error (attempt {attempt + 1}/{max_retries})...")
                    import time
                    time.sleep(retry_delay)
                    retry_delay *= 2
                    continue
                else:
                    logger.error(f"Error analyzing with Claude: {str(e)}")
                    raise Exception(f"Failed to analyze contract: {str(e)}")
    
    def _parse_claude_response(self, response_text: str) -> Dict[str, Any]:
        """Parse Claude's response and extract JSON data."""
        try:
            # Try to extract JSON from the response
            json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
            if json_match:
                json_str = json_match.group()
                data = json.loads(json_str)
                
                # Validate and clean the data
                return self._validate_and_clean_data(data)
            else:
                # If no JSON found, create a basic structure
                return self._create_fallback_response(response_text)
                
        except json.JSONDecodeError as e:
            logger.error(f"Error parsing JSON response: {str(e)}")
            return self._create_fallback_response(response_text)
    
    def _validate_and_clean_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate and clean the parsed data."""
        cleaned_data = {
            'contract_title': str(data.get('contract_title', 'Unknown Contract')),
            'duration': str(data.get('duration', 'Not specified')),
            'parties': {
                'party1': str(data.get('parties', {}).get('party1', 'Unknown')),
                'party2': str(data.get('parties', {}).get('party2', 'Unknown')),
                'relationship': str(data.get('parties', {}).get('relationship', 'Not specified'))
            },
            'contract_details': str(data.get('contract_details', 'No details available')),
            'risk_assessment': {
                'safety_percentage': min(100, max(0, int(data.get('risk_assessment', {}).get('safety_percentage', 50)))),
                'risk_level': str(data.get('risk_assessment', {}).get('risk_level', 'Medium')),
                'scam_likelihood': str(data.get('risk_assessment', {}).get('scam_likelihood', 'Unknown')),
                'explanation': str(data.get('risk_assessment', {}).get('explanation', 'No risk assessment available'))
            },
            'contract_explanation': str(data.get('contract_explanation', 'No explanation available')),
            'legal_terms_simplified': data.get('legal_terms_simplified', []),
            'risky_parts': data.get('risky_parts', []),
            'missing_clauses': data.get('missing_clauses', []),
            'recommended_changes': data.get('recommended_changes', []),
            'final_recommendations': str(data.get('final_recommendations', 'No recommendations available'))
        }
        
        return cleaned_data
    
    def _create_fallback_response(self, response_text: str) -> Dict[str, Any]:
        """Create a fallback response when JSON parsing fails."""
        return {
            'contract_title': 'Document Analysis',
            'duration': 'Not specified',
            'parties': {
                'party1': 'Unknown',
                'party2': 'Unknown',
                'relationship': 'Not specified'
            },
            'contract_details': 'Could not extract specific contract details.',
            'risk_assessment': {
                'safety_percentage': 50,
                'risk_level': 'Unknown',
                'scam_likelihood': 'Unknown',
                'explanation': 'Automatic analysis could not fully process this document.'
            },
            'contract_explanation': 'The document analysis could not be completed automatically.',
            'legal_terms_simplified': [],
            'risky_parts': [],
            'missing_clauses': [],
            'recommended_changes': [],
            'final_recommendations': 'Please have this document reviewed by a qualified legal professional.',
            'raw_response': response_text
        }