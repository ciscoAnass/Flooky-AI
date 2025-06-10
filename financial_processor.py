import os
import json
import logging
import csv
from typing import Dict, List, Any
import fitz  # PyMuPDF
import requests
import re
from datetime import datetime
from config import Config

logger = logging.getLogger(__name__)

class FinancialProcessor:
    """Handles bank statement processing and financial analysis."""
    
    def __init__(self, api_key=None):
        self.api_key = api_key or Config.CLAUDE_API_KEY
        self.model = "claude-3-5-haiku-20241022"
        self.allowed_extensions = {'pdf', 'csv', 'txt'}
    
    def process_financial_data(self, file_path: str, financial_goal: str, goal_amount: str = "", goal_timeframe: str = "") -> Dict[str, Any]:
        """Main processing function for financial analysis."""
        try:
            # Extract text from file
            text = self._extract_text(file_path)
            if not text.strip():
                return {
                    'success': False,
                    'error': 'No data could be extracted from the file'
                }
            
            logger.info(f"Extracted financial data length: {len(text)} characters")
            
            # Analyze with Claude
            analysis = self._analyze_with_claude(text, financial_goal, goal_amount, goal_timeframe)
            
            return {
                'success': True,
                'data': analysis
            }
            
        except Exception as e:
            logger.error(f"Error processing financial data: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def _extract_text(self, file_path: str) -> str:
        """Extract text from PDF, CSV or TXT file."""
        file_extension = os.path.splitext(file_path)[1].lower()
        
        if file_extension == '.pdf':
            return self._extract_text_from_pdf(file_path)
        elif file_extension == '.csv':
            return self._extract_text_from_csv(file_path)
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
    
    def _extract_text_from_csv(self, file_path: str) -> str:
        """Extract text from CSV file."""
        try:
            text = ""
            with open(file_path, 'r', encoding='utf-8') as csvfile:
                # Try to detect delimiter
                sample = csvfile.read(1024)
                csvfile.seek(0)
                sniffer = csv.Sniffer()
                delimiter = sniffer.sniff(sample).delimiter
                
                reader = csv.reader(csvfile, delimiter=delimiter)
                for row in reader:
                    text += ", ".join(row) + "\n"
            return text
        except Exception as e:
            logger.error(f"Error extracting text from CSV: {str(e)}")
            raise Exception(f"Failed to extract text from CSV: {str(e)}")
    
    def _extract_text_from_txt(self, file_path: str) -> str:
        """Extract text from TXT file."""
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                return file.read()
        except Exception as e:
            logger.error(f"Error extracting text from TXT: {str(e)}")
            raise Exception(f"Failed to extract text from TXT: {str(e)}")
    
    def _analyze_with_claude(self, text: str, financial_goal: str, goal_amount: str, goal_timeframe: str) -> Dict[str, Any]:
        """Analyze financial data with Claude AI."""
        max_retries = 3
        retry_delay = 2
        
        for attempt in range(max_retries):
            try:
                # Financial analysis prompt
                analysis_prompt = f"""
                As an expert financial advisor, please analyze this bank statement data and provide comprehensive financial advice.

                Bank Statement Data:
                {text}

                User's Financial Goal: {financial_goal}
                Goal Amount: {goal_amount}
                Target Timeframe: {goal_timeframe}

                Please provide your response in the following JSON format:
                {{
                    "financial_overview": {{
                        "total_income": 0.00,
                        "total_expenses": 0.00,
                        "net_savings": 0.00,
                        "analysis_period": "Last X months",
                        "average_monthly_income": 0.00,
                        "average_monthly_expenses": 0.00
                    }},
                    "spending_breakdown": [
                        {{
                            "category": "Housing/Rent",
                            "amount": 0.00,
                            "percentage": 0.0,
                            "frequency": "monthly",
                            "status": "normal/high/low"
                        }}
                    ],
                    "income_sources": [
                        {{
                            "source": "Salary",
                            "amount": 0.00,
                            "frequency": "monthly",
                            "stability": "stable/variable"
                        }}
                    ],
                    "financial_habits": {{
                        "good_habits": [
                            "List of positive financial behaviors observed"
                        ],
                        "bad_habits": [
                            "List of concerning spending patterns"
                        ],
                        "subscriptions": [
                            {{
                                "service": "Service name",
                                "cost": 0.00,
                                "frequency": "monthly",
                                "necessity": "essential/useful/unnecessary"
                            }}
                        ]
                    }},
                    "goal_analysis": {{
                        "goal": "{financial_goal}",
                        "target_amount": "{goal_amount}",
                        "timeframe": "{goal_timeframe}",
                        "feasibility": "achievable/challenging/unrealistic",
                        "current_savings_rate": 0.0,
                        "required_savings_rate": 0.0,
                        "monthly_savings_needed": 0.00,
                        "time_to_reach_goal": "X months/years"
                    }},
                    "recommendations": {{
                        "stop_doing": [
                            {{
                                "action": "Specific thing to stop",
                                "potential_savings": 0.00,
                                "impact": "high/medium/low"
                            }}
                        ],
                        "start_doing": [
                            {{
                                "action": "Specific thing to start",
                                "potential_benefit": 0.00,
                                "difficulty": "easy/medium/hard"
                            }}
                        ],
                        "budget_suggestions": [
                            {{
                                "category": "Category name",
                                "current_spending": 0.00,
                                "recommended_spending": 0.00,
                                "reason": "Why this change is recommended"
                            }}
                        ]
                    }},
                    "action_plan": {{
                        "immediate_actions": [
                            "Actions to take in the next 30 days"
                        ],
                        "short_term_goals": [
                            "Goals for next 3-6 months"
                        ],
                        "long_term_strategy": [
                            "Long-term financial strategy"
                        ]
                    }},
                    "income_optimization": [
                        {{
                            "suggestion": "How to increase income",
                            "potential_increase": 0.00,
                            "effort_required": "low/medium/high",
                            "timeframe": "immediate/short-term/long-term"
                        }}
                    ],
                    "risk_assessment": {{
                        "emergency_fund_status": "adequate/insufficient/none",
                        "financial_stability": "stable/at-risk/unstable",
                        "debt_situation": "none/manageable/concerning/critical",
                        "recommendations": "Overall risk mitigation advice"
                    }},
                    "personalized_insights": "Detailed, personalized advice based on the user's specific situation and goals"
                }}

                Analyze spending patterns, identify trends, calculate percentages, and provide actionable advice. Be specific with numbers and realistic with recommendations. Consider the user's goal and provide a clear path to achieve it.
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
                    raise Exception(f"Failed to analyze financial data: {str(e)}")
    
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
        # Ensure all required fields exist with defaults
        cleaned_data = {
            'financial_overview': data.get('financial_overview', {}),
            'spending_breakdown': data.get('spending_breakdown', []),
            'income_sources': data.get('income_sources', []),
            'financial_habits': data.get('financial_habits', {}),
            'goal_analysis': data.get('goal_analysis', {}),
            'recommendations': data.get('recommendations', {}),
            'action_plan': data.get('action_plan', {}),
            'income_optimization': data.get('income_optimization', []),
            'risk_assessment': data.get('risk_assessment', {}),
            'personalized_insights': str(data.get('personalized_insights', 'No specific insights available'))
        }
        
        return cleaned_data
    
    def _create_fallback_response(self, response_text: str) -> Dict[str, Any]:
        """Create a fallback response when JSON parsing fails."""
        return {
            'financial_overview': {
                'total_income': 0.0,
                'total_expenses': 0.0,
                'net_savings': 0.0,
                'analysis_period': 'Unable to determine',
                'average_monthly_income': 0.0,
                'average_monthly_expenses': 0.0
            },
            'spending_breakdown': [],
            'income_sources': [],
            'financial_habits': {
                'good_habits': [],
                'bad_habits': [],
                'subscriptions': []
            },
            'goal_analysis': {
                'feasibility': 'unknown',
                'time_to_reach_goal': 'Unable to calculate'
            },
            'recommendations': {
                'stop_doing': [],
                'start_doing': [],
                'budget_suggestions': []
            },
            'action_plan': {
                'immediate_actions': [],
                'short_term_goals': [],
                'long_term_strategy': []
            },
            'income_optimization': [],
            'risk_assessment': {
                'financial_stability': 'unknown'
            },
            'personalized_insights': 'The financial analysis could not be completed automatically. Please have your financial data reviewed by a qualified financial advisor.',
            'raw_response': response_text
        }