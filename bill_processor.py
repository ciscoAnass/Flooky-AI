import os
import json
import logging
from typing import Dict, List, Any
import fitz  # PyMuPDF
import pytesseract
from PIL import Image
import requests
import re
from datetime import datetime
from config import Config

logger = logging.getLogger(__name__)

class BillProcessor:
    """Handles bill processing including text extraction and AI analysis."""
    
    def __init__(self, api_key=None):
        self.api_key = api_key or Config.CLAUDE_API_KEY
        self.model = "claude-3-5-haiku-20241022"
    
    def process_bill(self, file_path: str) -> Dict[str, Any]:
        """Main processing function for bills."""
        try:
            # Extract text from file
            text = self._extract_text(file_path)
            if not text.strip():
                return {
                    'success': False,
                    'error': 'No text could be extracted from the file'
                }
            
            logger.info(f"Extracted text length: {len(text)} characters")
            
            # Analyze with Claude
            analysis = self._analyze_with_claude(text)
            
            return {
                'success': True,
                'data': analysis
            }
            
        except Exception as e:
            logger.error(f"Error processing bill: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def _extract_text(self, file_path: str) -> str:
        """Extract text from PDF or image file."""
        file_extension = os.path.splitext(file_path)[1].lower()
        
        if file_extension == '.pdf':
            return self._extract_text_from_pdf(file_path)
        else:
            return self._extract_text_from_image(file_path)
    
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
    
    def _extract_text_from_image(self, file_path: str) -> str:
        """Extract text from image using Tesseract OCR."""
        try:
            image = Image.open(file_path)
            text = pytesseract.image_to_string(image)
            return text
        except Exception as e:
            logger.error(f"Error extracting text from image: {str(e)}")
            raise Exception(f"Failed to extract text from image: {str(e)}")
    
    def _analyze_with_claude(self, text: str) -> Dict[str, Any]:
        """Analyze extracted text with Claude AI."""
        try:
            # Detect language first
            language_prompt = f"""
            Detect the language of this bill text and respond with just the language name in English:
            
            {text[:500]}
            """
            
            # Headers for API call
            headers = {
                "Content-Type": "application/json",
                "x-api-key": self.api_key,
                "anthropic-version": "2023-06-01"
            }
            
            # Language detection call
            language_data = {
                "model": self.model,
                "max_tokens": 50,
                "messages": [{
                    "role": "user",
                    "content": language_prompt
                }]
            }
            
            language_response = requests.post(
                "https://api.anthropic.com/v1/messages",
                headers=headers,
                json=language_data
            )
            
            if language_response.status_code == 200:
                lang_resp_json = language_response.json()
                lang_content = lang_resp_json.get("content", [])
                detected_language = ""
                for item in lang_content:
                    if item.get("type") == "text":
                        detected_language += item.get("text", "")
                detected_language = detected_language.strip()
            else:
                detected_language = "English"
            
            logger.info(f"Detected language: {detected_language}")
            
            # Main analysis prompt
            analysis_prompt = self._get_analysis_prompt(text, detected_language)
            
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
            
            if response.status_code != 200:
                raise Exception(f"API Error: {response.status_code} - {response.text}")
            
            # Parse the response
            resp_json = response.json()
            content = resp_json.get("content", [])
            analysis_text = ""
            for item in content:
                if item.get("type") == "text":
                    analysis_text += item.get("text", "")
            
            return self._parse_claude_response(analysis_text, detected_language)
            
        except Exception as e:
            logger.error(f"Error analyzing with Claude: {str(e)}")
            raise Exception(f"Failed to analyze bill: {str(e)}")
    
    def _get_analysis_prompt(self, text: str, language: str) -> str:
        """Generate the analysis prompt for Claude."""
        if language.lower() in ['spanish', 'español']:
            return f"""
            Analiza esta factura/recibo y proporciona un análisis estructurado. Responde en español.
            
            Texto de la factura:
            {text}
            
            Por favor, proporciona tu respuesta en el siguiente formato JSON:
            {{
                "items": [
                    {{
                        "name": "Nombre del artículo",
                        "amount": 0.00,
                        "category": "Categoría",
                        "notes": "Notas sobre este artículo"
                    }}
                ],
                "total": 0.00,
                "currency": "Moneda detectada",
                "summary": "Resumen del análisis",
                "observations": "Observaciones importantes",
                "suggestions": "Sugerencias para el usuario"
            }}
            
            Categorías sugeridas: Servicios Públicos, Alimentación, Suscripciones, Transporte, Entretenimiento, Salud, Educación, Hogar, Desconocido
            
            Para las notas, incluye comentarios como "tarifa estándar", "más alto de lo usual", "cargo sospechoso", etc.
            """
        else:
            return f"""
            Analyze this bill/receipt and provide a structured analysis. Respond in English.
            
            Bill text:
            {text}
            
            Please provide your response in the following JSON format:
            {{
                "items": [
                    {{
                        "name": "Item name",
                        "amount": 0.00,
                        "category": "Category",
                        "notes": "Notes about this item"
                    }}
                ],
                "total": 0.00,
                "currency": "Detected currency",
                "summary": "Summary of the analysis",
                "observations": "Important observations",
                "suggestions": "Suggestions for the user"
            }}
            
            Suggested categories: Utilities, Grocery, Subscription, Transportation, Entertainment, Healthcare, Education, Home, Unknown
            
            For notes, include comments like "standard rate", "higher than usual", "suspicious charge", etc.
            """
    
    def _parse_claude_response(self, response_text: str, language: str) -> Dict[str, Any]:
        """Parse Claude's response and extract JSON data."""
        try:
            # Try to extract JSON from the response
            json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
            if json_match:
                json_str = json_match.group()
                data = json.loads(json_str)
                
                # Validate and clean the data
                return self._validate_and_clean_data(data, language)
            else:
                # If no JSON found, create a basic structure
                return self._create_fallback_response(response_text, language)
                
        except json.JSONDecodeError as e:
            logger.error(f"Error parsing JSON response: {str(e)}")
            return self._create_fallback_response(response_text, language)
    
    def _validate_and_clean_data(self, data: Dict[str, Any], language: str) -> Dict[str, Any]:
        """Validate and clean the parsed data."""
        cleaned_data = {
            'items': [],
            'total': 0.0,
            'currency': data.get('currency', 'USD'),
            'summary': data.get('summary', ''),
            'observations': data.get('observations', ''),
            'suggestions': data.get('suggestions', ''),
            'language': language
        }
        
        # Clean items
        for item in data.get('items', []):
            try:
                cleaned_item = {
                    'name': str(item.get('name', 'Unknown')),
                    'amount': float(item.get('amount', 0.0)),
                    'category': str(item.get('category', 'Unknown')),
                    'notes': str(item.get('notes', ''))
                }
                cleaned_data['items'].append(cleaned_item)
            except (ValueError, TypeError) as e:
                logger.warning(f"Skipping invalid item: {item}, error: {str(e)}")
        
        # Calculate total
        try:
            cleaned_data['total'] = float(data.get('total', 0.0))
        except (ValueError, TypeError):
            cleaned_data['total'] = sum(item['amount'] for item in cleaned_data['items'])
        
        return cleaned_data
    
    def _create_fallback_response(self, response_text: str, language: str) -> Dict[str, Any]:
        """Create a fallback response when JSON parsing fails."""
        if language.lower() in ['spanish', 'español']:
            return {
                'items': [],
                'total': 0.0,
                'currency': 'EUR',
                'summary': 'No se pudieron extraer elementos específicos de la factura.',
                'observations': 'El análisis automático no pudo procesar completamente este documento.',
                'suggestions': 'Considere verificar manualmente los elementos de la factura.',
                'language': language,
                'raw_response': response_text
            }
        else:
            return {
                'items': [],
                'total': 0.0,
                'currency': 'USD',
                'summary': 'Could not extract specific items from the bill.',
                'observations': 'Automatic analysis could not fully process this document.',
                'suggestions': 'Consider manually reviewing the bill items.',
                'language': language,
                'raw_response': response_text
            }