import requests
import os
import json
import logging
from typing import Optional

logger = logging.getLogger(__name__)

class FireworksService:
    def __init__(self):
        self.api_key = os.getenv('FIREWORKS_API_KEY')
        self.base_url = "https://api.fireworks.ai/inference/v1/chat/completions"
        self.model = "accounts/fireworks/models/llama-v3p1-405b-instruct"
        
    def is_available(self) -> bool:
        """Check if Fireworks API is available"""
        return bool(self.api_key)
    
    def enhance_question(self, user_question: str) -> str:
        """
        Enhance and format the user's question using Fireworks API
        """
        if not self.api_key:
            logger.warning("Fireworks API key not found")
            return user_question
            
        try:
            # System prompt for question enhancement
            system_prompt = """You are a question enhancement AI for Anirudh's portfolio chatbot. 
Your job is to take user questions and enhance them to be more specific and contextually relevant for a portfolio assistant that should provide structured, bullet-point formatted responses.

Rules:
1. Keep the original intent of the question
2. Make it more specific to portfolio/professional context if vague
3. Fix any grammar or spelling issues
4. Make it conversational and natural
5. If it's already well-formed, return it unchanged
6. Don't add unnecessary complexity
7. Encourage responses that can be formatted with bullet points and structure

Examples:
"tell me about skills" → "What are Anirudh's technical skills and areas of expertise?"
"projects" → "Can you provide details about Anirudh's notable projects with descriptions and links?"
"contact" → "How can I contact Anirudh for professional opportunities?"
"experience" → "What is Anirudh's professional work experience and background?"
"detail description of the projects" → "Can you provide detailed descriptions of Anirudh's featured projects including technologies used and links?"

Return only the enhanced question, nothing else."""

            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            
            payload = {
                "model": self.model,
                "messages": [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": f"Enhance this question: {user_question}"}
                ],
                "max_tokens": 150,
                "temperature": 0.3
            }
            
            logger.info(f"Sending request to Fireworks API for question enhancement")
            response = requests.post(self.base_url, headers=headers, json=payload, timeout=10)
            response.raise_for_status()
            
            result = response.json()
            enhanced_question = result['choices'][0]['message']['content'].strip()
            
            # Remove quotes if present
            if enhanced_question.startswith('"') and enhanced_question.endswith('"'):
                enhanced_question = enhanced_question[1:-1]
                
            logger.info(f"Question enhanced successfully: {user_question} → {enhanced_question}")
            return enhanced_question
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Fireworks API request failed: {str(e)}")
            raise Exception(f"Fireworks API error: {str(e)}")
        except KeyError as e:
            logger.error(f"Unexpected Fireworks API response format: {str(e)}")
            raise Exception("Invalid response format from Fireworks API")
        except Exception as e:
            logger.error(f"Fireworks service error: {str(e)}")
            raise Exception(f"Fireworks service error: {str(e)}")
    
    def test_connection(self) -> dict:
        """Test the Fireworks API connection"""
        if not self.api_key:
            return {"status": "error", "message": "API key not configured"}
        
        try:
            test_question = "Hello"
            enhanced = self.enhance_question(test_question)
            return {
                "status": "success", 
                "message": "Fireworks API connection successful",
                "test_result": f"'{test_question}' → '{enhanced}'"
            }
        except Exception as e:
            return {"status": "error", "message": f"Connection failed: {str(e)}"}