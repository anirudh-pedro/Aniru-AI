import json
import os
import re
import logging
from typing import Dict, List

logger = logging.getLogger(__name__)

class RuleBasedChatbot:
    def __init__(self):
        self.portfolio_data = self._load_portfolio_data()
        self.responses = self._initialize_responses()
        
    def _load_portfolio_data(self) -> dict:
        """Load portfolio data from data.json"""
        try:
            data_path = os.path.join(os.path.dirname(__file__), '..', 'data', 'data.json')
            with open(data_path, 'r', encoding='utf-8') as file:
                data = json.load(file)
                logger.info("Portfolio data loaded for rule-based chatbot")
                return data
        except FileNotFoundError:
            logger.warning("data.json not found for rule-based chatbot")
            return {}
        except json.JSONDecodeError as e:
            logger.error(f"Error parsing data.json in rule-based chatbot: {str(e)}")
            return {}
        except Exception as e:
            logger.error(f"Error loading portfolio data in rule-based chatbot: {str(e)}")
            return {}
    
    def _initialize_responses(self) -> Dict[str, List[str]]:
        """Initialize response patterns and templates"""
        return {
            'greeting': [
                "Hello! I'm Aniru AI, Anirudh's personal assistant. I'd be happy to help you learn more about his professional journey and expertise. What would you like to know?",
                "Hi there! I'm Aniru AI, and I'm here to share everything about Anirudh's impressive portfolio and achievements. How can I assist you today?",
                "Hey! Welcome to Anirudh's portfolio. I'm Aniru AI, his personal assistant, and I'm excited to showcase his work and accomplishments. What interests you most?"
            ],
            'skills': [
                "I'd be delighted to share information about Anirudh's comprehensive technical skills and areas of expertise.",
                "Anirudh has developed a diverse and impressive skill set. Let me break down his technical capabilities for you."
            ],
            'projects': [
                "Here are Anirudh's key projects:",
                "Anirudh has built some impressive projects. Here they are:"
            ],
            'experience': [
                "I'd be happy to tell you about Anirudh's professional experience and career accomplishments.",
                "Let me share information about Anirudh's work experience and professional development journey."
            ],
            'contact': [
                "I'd be happy to provide you with Anirudh's contact information for professional opportunities and collaborations.",
                "Here's how you can connect with Anirudh for potential projects or professional inquiries."
            ],
            'education': [
                "I'd be delighted to share information about Anirudh's educational background and academic achievements.",
                "Let me tell you about Anirudh's academic journey and qualifications."
            ],
            'about': [
                "I'd love to tell you about Anirudh - his background, passions, and what makes him an exceptional professional.",
                "Let me share more about Anirudh's story, both his professional expertise and personal interests."
            ],
            'default': [
                "That's an interesting question! While I don't have specific information about that topic, I'd be happy to help you learn about:\n\n• Anirudh's technical skills and expertise\n• His impressive portfolio of projects\n• Professional experience and achievements\n• How to connect with him professionally\n\nWhat would you like to explore?",
                "I might not have that exact information, but I can certainly tell you about:\n\n• His comprehensive technical skill set\n• Notable projects and innovations\n• Professional background and experience\n• Contact information for opportunities\n\nWhat interests you most about Anirudh's work?"
            ],
            'api_fallback': [
                "I'm currently running in fallback mode, but I can still provide comprehensive information about:\n\n• Anirudh's technical skills and expertise\n• His impressive project portfolio\n• Professional experience and achievements\n• Contact details for opportunities\n\nWhat would you like to know?",
                "While our advanced AI services are temporarily unavailable, I can still share detailed information about Anirudh's professional portfolio and accomplishments from our knowledge base."
            ]
        }
    
    def _extract_portfolio_info(self, category: str) -> str:
        """Extract specific information from portfolio data with bullet point formatting"""
        try:
            if not self.portfolio_data:
                return "I don't have detailed portfolio information available at the moment."
            
            # Handle different data structures in portfolio_data
            if category == 'skills' and 'skills' in self.portfolio_data:
                skills = self.portfolio_data['skills']
                if isinstance(skills, list):
                    return f"I'd be happy to share Anirudh's technical expertise. Here are his key skills:\n\n• {chr(10).join([f'**{skill}**' for skill in skills])}\n\nThese skills demonstrate Anirudh's comprehensive knowledge across multiple domains. Would you like to know more about his experience with any of these technologies?"
                elif isinstance(skills, dict):
                    skill_text = ["I'd be happy to showcase Anirudh's diverse technical skill set. Here's a breakdown of his expertise:\n"]
                    for skill_category, skill_list in skills.items():
                        if isinstance(skill_list, list):
                            formatted_skills = ', '.join(skill_list)
                            skill_text.append(f"• **{skill_category.title()}**: {formatted_skills}")
                        elif isinstance(skill_list, str):
                            skill_text.append(f"• **{skill_category.title()}**: {skill_list}")
                    skill_text.append("\nThis diverse skill set enables Anirudh to work on various types of projects and adapt to different technological requirements. Feel free to ask about his experience with any specific technology!")
                    return "\n".join(skill_text)
            
            elif category == 'projects' and 'projects' in self.portfolio_data:
                projects = self.portfolio_data['projects']
                if isinstance(projects, list):
                    project_info = ["Here are Anirudh's key projects:\n"]
                    
                    for i, project in enumerate(projects[:4], 1):  # Show top 4 projects
                        if isinstance(project, dict):
                            name = project.get('name', 'Unnamed Project')
                            description = project.get('description', 'A comprehensive project showcasing technical expertise')
                            live_demo = project.get('live_demo', '')
                            tech_stack = project.get('tech_stack', '')
                            
                            # Format the project entry concisely
                            project_text = f"{i}. **{name}**"
                            if live_demo:
                                project_text += f" - {description[:80]}...\n   * Live Demo: {live_demo}"
                            else:
                                project_text += f" - {description[:100]}..."
                            
                            if tech_stack:
                                project_text += f"\n   * Tech: {tech_stack}"
                                
                            project_info.append(project_text)
                        else:
                            project_info.append(f"{i}. **{project}**")
                    
                    return "\n\n".join(project_info)
            
            elif category == 'experience' and 'experience' in self.portfolio_data:
                experience = self.portfolio_data['experience']
                if isinstance(experience, list):
                    exp_info = ["Anirudh's professional experience:\n"]
                    for i, exp in enumerate(experience, 1):
                        if isinstance(exp, dict):
                            title = exp.get('title', exp.get('position', 'Position'))
                            company = exp.get('company', exp.get('organization', 'Company'))
                            duration = exp.get('duration', exp.get('period', ''))
                            description = exp.get('description', '')
                            
                            exp_text = f"{i}. **{title}** at {company}"
                            if duration:
                                exp_text += f" ({duration})"
                            if description:
                                exp_text += f"\n• {description}"
                            exp_info.append(exp_text)
                        else:
                            exp_info.append(f"{i}. {exp}")
                    return "\n\n".join(exp_info)
            
            elif category == 'contact' and 'contact' in self.portfolio_data:
                contact = self.portfolio_data['contact']
                if isinstance(contact, dict):
                    contact_info = ["Here's how to contact Anirudh:\n"]
                    for key, value in contact.items():
                        if value:
                            if key.lower() == 'email':
                                contact_info.append(f"• **Email**: {value}")
                            elif key.lower() == 'linkedin':
                                contact_info.append(f"• **LinkedIn**: {value}")
                            elif key.lower() == 'github':
                                contact_info.append(f"• **GitHub**: {value}")
                            elif key.lower() == 'phone':
                                contact_info.append(f"• **Phone**: {value}")
                            else:
                                contact_info.append(f"• **{key.title()}**: {value}")
                    return "\n".join(contact_info)
            
            return f"I have some information about Anirudh's {category}, but it might need to be formatted better. Please check his portfolio for the most current details."
            
        except Exception as e:
            logger.error(f"Error extracting portfolio info for {category}: {str(e)}")
            return f"I have information about Anirudh's {category}, but I'm having trouble accessing it right now. Please try asking in a different way!"
    
    def _classify_intent(self, message: str) -> str:
        """Classify user intent based on keywords"""
        message_lower = message.lower()
        
        # Greeting patterns
        if any(word in message_lower for word in ['hello', 'hi', 'hey', 'greetings', 'good morning', 'good afternoon']):
            return 'greeting'
        
        # Skills patterns
        if any(word in message_lower for word in ['skill', 'technology', 'programming', 'languages', 'frameworks', 'tools', 'technical', 'expertise']):
            return 'skills'
        
        # Projects patterns
        if any(word in message_lower for word in ['project', 'projects', 'work', 'portfolio', 'built', 'created', 'developed', 'github', 'show me his']):
            return 'projects'
        
        # Experience patterns
        if any(word in message_lower for word in ['experience', 'job', 'career', 'work history', 'employment', 'professional']):
            return 'experience'
        
        # Contact patterns
        if any(word in message_lower for word in ['contact', 'email', 'phone', 'reach', 'connect', 'linkedin', 'social']):
            return 'contact'
        
        # Education patterns
        if any(word in message_lower for word in ['education', 'degree', 'university', 'college', 'study', 'academic']):
            return 'education'
        
        # About patterns
        if any(word in message_lower for word in ['about', 'who is', 'tell me', 'background', 'bio', 'story']):
            return 'about'
        
        return 'default'
    
    def get_response(self, user_message: str) -> str:
        """Generate response based on rule-based logic with enhanced error handling"""
        try:
            # Validate input
            if not user_message or not user_message.strip():
                return "Hello! I'm Aniru AI, Anirudh's personal assistant. How can I help you learn more about his portfolio and expertise?"
            
            user_message = user_message.strip()
            logger.info(f"Rule-based chatbot processing: {user_message}")
            
            # Classify the intent
            intent = self._classify_intent(user_message)
            logger.info(f"Classified intent: {intent}")
            
            # Get base response template with fallback
            response_templates = self.responses.get(intent, self.responses.get('default', [
                "I'm here to help you learn more about Anirudh. What would you like to know?"
            ]))
            
            if not response_templates:
                response_templates = ["I'm here to help you learn about Anirudh's professional background."]
            
            base_response = response_templates[0]  # Use first template
            
            # Add portfolio-specific information if available
            if intent in ['skills', 'projects', 'experience', 'contact'] and self.portfolio_data:
                try:
                    portfolio_info = self._extract_portfolio_info(intent)
                    response = f"{base_response}\n\n{portfolio_info}"
                except Exception as e:
                    logger.warning(f"Failed to extract portfolio info for {intent}: {str(e)}")
                    # Provide basic information as fallback
                    if intent == 'contact':
                        response = f"{base_response}\n\nYou can reach Anirudh at:\n• Email: anirudh200503@gmail.com\n• LinkedIn: https://www.linkedin.com/in/anirudh-t-b5b26a2aa/\n• GitHub: https://github.com/anirudh-pedro"
                    elif intent == 'skills':
                        response = f"{base_response}\n\nAnirudh specializes in:\n• Programming: C++, Python, JavaScript\n• Web Development: React, Node.js, Express\n• Database: MongoDB, MySQL\n• Areas: Data Structures, Algorithms, System Design"
                    elif intent == 'projects':
                        response = f"{base_response}\n\nAnirudh has worked on various projects including web applications, chatbots, and data analysis tools. You can find his work on GitHub: https://github.com/anirudh-pedro"
                    else:
                        response = base_response
            else:
                response = base_response
                
                # Add helpful navigation for default/unknown intents
                if intent == 'default':
                    response += "\n\nI can help you learn about:"
                    response += "\n• His technical skills and expertise"
                    response += "\n• Projects he's worked on"
                    response += "\n• Professional experience"
                    response += "\n• How to contact him"
                    response += "\n\nWhat would you like to know more about?"
            
            logger.info("Rule-based response generated successfully")
            return response
            
        except Exception as e:
            logger.error(f"Critical error in rule-based chatbot: {str(e)}")
            # Emergency fallback with basic information
            return """I'm Aniru AI, Anirudh's personal assistant! I'm experiencing some technical difficulties, but I can still help you.

Anirudh is a passionate computer science student and full-stack developer. Here's how you can learn more:

• **Contact**: anirudh200503@gmail.com
• **LinkedIn**: https://www.linkedin.com/in/anirudh-t-b5b26a2aa/
• **GitHub**: https://github.com/anirudh-pedro

Please try asking your question again, and I'll do my best to provide detailed information about his projects, skills, and achievements!"""
    
    def test_functionality(self) -> dict:
        """Test the rule-based chatbot functionality"""
        try:
            test_messages = [
                "Hello",
                "What are his skills?",
                "Tell me about projects",
                "How can I contact him?"
            ]
            
            results = {}
            for message in test_messages:
                response = self.get_response(message)
                results[message] = response[:100] + "..." if len(response) > 100 else response
            
            return {
                "status": "success",
                "message": "Rule-based chatbot is working",
                "test_results": results,
                "portfolio_data_loaded": bool(self.portfolio_data)
            }
        except Exception as e:
            return {
                "status": "error", 
                "message": f"Rule-based chatbot test failed: {str(e)}"
            }