import requests
import os
import json
import logging
from typing import Optional

logger = logging.getLogger(__name__)

class GroqService:
    def __init__(self):
        self.api_key = os.getenv('GROQ_API_KEY')
        self.base_url = "https://api.groq.com/openai/v1/chat/completions"
        self.model = "llama3-70b-8192"  # Fast and efficient model
        
        # Load portfolio data
        self.portfolio_data = self._load_portfolio_data()
        
    def is_available(self) -> bool:
        """Check if Groq API is available"""
        return bool(self.api_key)
    
    def _load_portfolio_data(self) -> dict:
        """Load portfolio data from data.json"""
        try:
            data_path = os.path.join(os.path.dirname(__file__), '..', 'data', 'data.json')
            with open(data_path, 'r', encoding='utf-8') as file:
                data = json.load(file)
                logger.info("Portfolio data loaded successfully")
                return data
        except FileNotFoundError:
            logger.warning("data.json not found, using empty portfolio data")
            return {}
        except json.JSONDecodeError as e:
            logger.error(f"Error parsing data.json: {str(e)}")
            return {}
        except Exception as e:
            logger.error(f"Error loading portfolio data: {str(e)}")
            return {}
    
    def _extract_relevant_data(self, question_lower: str) -> str:
        """Extract relevant portfolio data based on the question type"""
        if not self.portfolio_data:
            return "No portfolio data available."
        
        relevant_sections = []
        
        # Projects-related questions
        if any(word in question_lower for word in ['project', 'work', 'portfolio', 'built', 'created', 'developed', 'github', 'repo']) and not any(word in question_lower for word in ['bye', 'goodbye', 'see you', 'thanks', 'thank you']):
            if 'projects' in self.portfolio_data:
                projects_data = self.portfolio_data['projects'][:4]  # Limit to 4 projects to avoid large payload
                
                # Dynamic GitHub URLs - map based on actual project names in data.json
                def get_github_url(project_name):
                    """Get GitHub URL for a project based on its name"""
                    name_lower = project_name.lower()
                    if 'flashchat' in name_lower:
                        return 'https://github.com/anirudh-pedro/FlashChat'
                    elif 'typomaster' in name_lower:
                        return 'https://github.com/anirudh-pedro/TypoMaster'
                    elif 'sentiment' in name_lower:
                        return 'https://github.com/anirudh-pedro/Sentiment-Analysis-App'
                    elif 'blogsphere' in name_lower or 'blog' in name_lower:
                        return 'https://github.com/anirudh-pedro/blogsphere'
                    return None
                
                # Enhance projects with GitHub URLs dynamically
                enhanced_projects = []
                for project in projects_data:
                    enhanced_project = project.copy()
                    project_name = project.get('name', '')
                    
                    # Add GitHub URL dynamically based on project name
                    github_url = get_github_url(project_name)
                    if github_url:
                        enhanced_project['github_url'] = github_url
                    
                    enhanced_projects.append(enhanced_project)
                
                relevant_sections.append(f"PROJECTS: {json.dumps(enhanced_projects, indent=2)}")
            else:
                # Only provide basic message if no project data exists
                relevant_sections.append("PROJECTS: No detailed project data available.")
        
        # Skills-related questions
        if any(word in question_lower for word in ['skill', 'technology', 'programming', 'languages', 'frameworks', 'tools', 'tech']):
            if 'skills' in self.portfolio_data:
                relevant_sections.append(f"SKILLS: {json.dumps(self.portfolio_data['skills'], indent=2)}")
        
        # Contact-related questions
        if any(word in question_lower for word in ['contact', 'email', 'phone', 'reach', 'connect', 'linkedin']):
            contact_info = {
                'email': 'anirudh200503@gmail.com',
                'phone': '+91 9894969187',
                'linkedin': 'https://www.linkedin.com/in/anirudh-t-b5b26a2aa/',
                'github': 'https://github.com/anirudh-pedro'
            }
            relevant_sections.append(f"CONTACT: {json.dumps(contact_info, indent=2)}")
        
        # Experience/Education questions
        if any(word in question_lower for word in ['experience', 'education', 'degree', 'university', 'background']):
            if 'profile' in self.portfolio_data:
                profile_info = {
                    'education': self.portfolio_data['profile'].get('education', {}),
                    'bio': self.portfolio_data['profile'].get('bio', ''),
                    'title': self.portfolio_data['profile'].get('title', '')
                }
                relevant_sections.append(f"BACKGROUND: {json.dumps(profile_info, indent=2)}")
        
        # Achievements questions
        if any(word in question_lower for word in ['achievement', 'leetcode', 'hackathon', 'contest', 'accomplishment']):
            if 'achievements' in self.portfolio_data:
                achievements = self.portfolio_data['achievements']
                # Limit achievements data to avoid large payload
                limited_achievements = {}
                if 'leetcode' in achievements:
                    limited_achievements['leetcode'] = {
                        'problems_solved': achievements['leetcode'].get('problems_solved'),
                        'contest_rating': achievements['leetcode'].get('contest_rating'),
                        'profile_url': achievements['leetcode'].get('profile_url')
                    }
                if 'hackathons' in achievements:
                    limited_achievements['hackathons'] = achievements['hackathons'][:2]  # Limit to 2
                relevant_sections.append(f"ACHIEVEMENTS: {json.dumps(limited_achievements, indent=2)}")
        
        # Farewell/goodbye questions
        if any(word in question_lower for word in ['bye', 'goodbye', 'see you', 'farewell', 'take care', 'later']):
            farewell_info = {
                'message_type': 'farewell',
                'response_style': 'brief and friendly'
            }
            relevant_sections.append(f"FAREWELL: {json.dumps(farewell_info, indent=2)}")
        
        # Default: provide basic profile info
        if not relevant_sections:
            if 'profile' in self.portfolio_data:
                basic_info = {
                    'name': self.portfolio_data['profile'].get('name'),
                    'title': self.portfolio_data['profile'].get('title'),
                    'bio': self.portfolio_data['profile'].get('bio', '')[:200] + '...'  # Truncate long bio
                }
                relevant_sections.append(f"PROFILE: {json.dumps(basic_info, indent=2)}")
        
        return '\n\n'.join(relevant_sections) if relevant_sections else "Basic portfolio information available."
    
    def get_response(self, enhanced_question: str, original_question: str) -> str:
        """
        Get response from Groq API using portfolio data and enhanced question
        """
        if not self.api_key:
            logger.warning("Groq API key not found")
            raise Exception("Groq API key not configured")
        
        # Validate input
        if not enhanced_question.strip():
            raise Exception("Empty question provided")
            
        try:
            # Extract relevant data based on question type
            relevant_data = self._extract_relevant_data(enhanced_question.lower())
            
            # Create system prompt with relevant portfolio data
            system_prompt = f"""You are Aniru AI, Anirudh's personal assistant. You're here to help users learn about Anirudh and answer their questions in a natural, conversational way.

RELEVANT DATA FOR THIS QUESTION:
{relevant_data}

PERSONALITY & BEHAVIOR:
- You are helpful, friendly, and conversational - like a real AI assistant
- Answer questions directly and specifically based on what the user asks
- ALWAYS give the exact information requested - don't give generic responses
- Use natural language and adapt to the user's tone and question type
- Be enthusiastic about Anirudh's work when relevant
- Keep responses focused on the user's specific question
- Handle different types of interactions naturally based on the RELEVANT DATA context
- Stay upbeat and engaging, never defensive or overly formal
- NEVER give generic "I'm here to help" responses when asked for specific information

FORMATTING RULES (use when listing multiple items):
1. Use numbered lists (1. 2. 3.) for multiple projects/items
2. Use bullet points (•) for details under each item  
3. Only include links if they exist in the portfolio data - never mention "no live demo available"
4. **CRITICAL URL FORMATTING**: Format links EXACTLY like this for clickability:
   - "Live Demo: https://example.com" (on same line, no bullets or line breaks)
   - "GitHub: https://github.com/user/repo" (on same line, no bullets or line breaks)
   - Never use bullet points (•) before URLs
   - Never put URLs on separate lines
5. Bold important names using **text**
6. Add line breaks between sections for readability
7. **CRITICAL**: NEVER add periods or punctuation after URLs - keep URLs clean for proper linking
8. When providing URLs, ensure they end without any trailing punctuation

RESPONSE GUIDELINES:
- Use the RELEVANT DATA provided above to answer questions accurately
- Answer naturally and conversationally based on the context and data provided
- For project questions: List projects from the PROJECTS data with descriptions and links
- For skill questions: Use the SKILLS data to mention specific technologies
- For contact questions: Use the CONTACT data to provide connection information
- For achievement questions: Use the ACHIEVEMENTS data to highlight accomplishments
- For background questions: Use the BACKGROUND data for education and bio info
- For farewell questions: Respond naturally and briefly based on the FAREWELL data context
- **CRITICAL**: NEVER add periods or punctuation after URLs - keep URLs clean for proper linking
- **URL FORMAT**: Always format URLs as "Live Demo: https://example.com" (same line, no bullets)
- Always answer directly based on the provided data - don't give generic responses
- Be conversational and adapt your response style to match the user's question type

**EXAMPLE PROJECT FORMAT:**
1. **ProjectName** - Brief description
   Tech Stack: Technology1, Technology2, Technology3
   Live Demo: https://example.com
   GitHub: https://github.com/user/repo

Remember: Use the actual data provided in RELEVANT DATA section above to give accurate, specific answers."""

            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            
            messages = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": enhanced_question}
            ]
            
            # Add context about question enhancement if applicable
            if enhanced_question != original_question:
                context_msg = f"Note: The user originally asked '{original_question}' which was enhanced to '{enhanced_question}' for better context."
                messages.append({"role": "system", "content": context_msg})
            
            payload = {
                "model": self.model,
                "messages": messages,
                "max_tokens": 1500,  # Increased for detailed project descriptions
                "temperature": 0.7,
                "top_p": 0.9,
                "stream": False
            }
            
            logger.info(f"Sending request to Groq API")
            response = requests.post(self.base_url, headers=headers, json=payload, timeout=15)
            response.raise_for_status()
            
            result = response.json()
            ai_response = result['choices'][0]['message']['content'].strip()
            
            logger.info("Successfully got response from Groq API")
            return ai_response
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Groq API request failed: {str(e)}")
            raise Exception(f"Groq API error: {str(e)}")
        except KeyError as e:
            logger.error(f"Unexpected Groq API response format: {str(e)}")
            raise Exception("Invalid response format from Groq API")
        except Exception as e:
            logger.error(f"Groq service error: {str(e)}")
            raise Exception(f"Groq service error: {str(e)}")
    
    def test_connection(self) -> dict:
        """Test the Groq API connection"""
        if not self.api_key:
            return {"status": "error", "message": "API key not configured"}
        
        try:
            test_response = self.get_response("Hello, who are you?", "Hello")
            return {
                "status": "success", 
                "message": "Groq API connection successful",
                "test_response": test_response[:100] + "..." if len(test_response) > 100 else test_response
            }
        except Exception as e:
            return {"status": "error", "message": f"Connection failed: {str(e)}"}
