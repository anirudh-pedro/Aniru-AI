from flask import Flask, request, jsonify
from flask_cors import CORS
import os
from dotenv import load_dotenv
import logging
from datetime import datetime

# Import services
from services.fireworks_service import FireworksService
from services.groq_service import GroqService
from services.rule_based_chatbot import RuleBasedChatbot
from routes.chat import chat_bp

# Load environment variables
load_dotenv()

# Initialize Flask app
app = Flask(__name__)
CORS(app)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Circuit breaker for API services
class CircuitBreaker:
    def __init__(self, failure_threshold=3, reset_timeout=60):
        self.failure_threshold = failure_threshold
        self.reset_timeout = reset_timeout
        self.failure_count = 0
        self.last_failure_time = None
        self.state = 'closed'  # closed, open, half-open
    
    def can_execute(self):
        import time
        if self.state == 'closed':
            return True
        elif self.state == 'open':
            if self.last_failure_time and time.time() - self.last_failure_time > self.reset_timeout:
                self.state = 'half-open'
                return True
            return False
        else:  # half-open
            return True
    
    def record_success(self):
        self.failure_count = 0
        self.state = 'closed'
    
    def record_failure(self):
        import time
        self.failure_count += 1
        self.last_failure_time = time.time()
        if self.failure_count >= self.failure_threshold:
            self.state = 'open'

# Initialize services
fireworks_service = FireworksService()
groq_service = GroqService()
rule_based_chatbot = RuleBasedChatbot()

# Circuit breakers for each service
fireworks_circuit_breaker = CircuitBreaker(failure_threshold=2, reset_timeout=30)
groq_circuit_breaker = CircuitBreaker(failure_threshold=3, reset_timeout=60)

# Register blueprints
app.register_blueprint(chat_bp, url_prefix='/api')

@app.route('/', methods=['GET'])
def home():
    """Home endpoint"""
    return jsonify({
        "status": "healthy",
        "message": "Aniru AI Backend is running!",
        "services": {
            "fireworks": fireworks_service.is_available(),
            "groq": groq_service.is_available(),
            "rule_based": True
        }
    })

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    try:
        # Check service availability
        services_status = {
            "fireworks": {
                "available": fireworks_service.is_available(),
                "circuit_breaker": fireworks_circuit_breaker.state,
                "failure_count": fireworks_circuit_breaker.failure_count
            },
            "groq": {
                "available": groq_service.is_available(),
                "circuit_breaker": groq_circuit_breaker.state,
                "failure_count": groq_circuit_breaker.failure_count
            },
            "rule_based": {
                "available": True,  # Rule-based should always be available
                "portfolio_data_loaded": bool(rule_based_chatbot.portfolio_data)
            }
        }
        
        # Determine overall health
        overall_health = "healthy"
        if groq_circuit_breaker.state == 'open' and not rule_based_chatbot.portfolio_data:
            overall_health = "degraded"
        
        return jsonify({
            "status": overall_health,
            "timestamp": datetime.now().isoformat(),
            "services": services_status
        })
        
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        return jsonify({
            "status": "unhealthy",
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }), 500

@app.route('/api/chat', methods=['POST'])
def chat():
    """Main chat endpoint with the specified pipeline"""
    try:
        data = request.get_json()
        user_message = data.get('message', '').strip()
        
        if not user_message:
            return jsonify({"error": "Message is required"}), 400
        
        logger.info(f"Received message: {user_message}")
        
        # Step 1: Try to enhance the question using Fireworks API (with circuit breaker)
        enhanced_message = user_message
        if fireworks_circuit_breaker.can_execute() and fireworks_service.is_available():
            try:
                logger.info("Step 1: Enhancing message with Fireworks API")
                enhanced_message = fireworks_service.enhance_question(user_message)
                fireworks_circuit_breaker.record_success()
                logger.info(f"Enhanced message: {enhanced_message}")
            except Exception as e:
                fireworks_circuit_breaker.record_failure()
                logger.warning(f"Fireworks API failed for enhancement: {str(e)}")
                logger.info("Proceeding with original message")
        else:
            logger.info("Fireworks API circuit breaker open or service unavailable, skipping enhancement")

        # Step 2: Try to get response from Groq API using enhanced message (with circuit breaker)
        if groq_circuit_breaker.can_execute() and groq_service.is_available():
            try:
                logger.info("Step 2: Getting response from Groq API")
                response = groq_service.get_response(enhanced_message, user_message)
                groq_circuit_breaker.record_success()
                logger.info("Successfully got response from Groq API")
                
                return jsonify({
                    "response": response,
                    "source": "groq_api",
                    "enhanced_query": enhanced_message != user_message,
                    "original_message": user_message,
                    "enhanced_message": enhanced_message if enhanced_message != user_message else None
                })
                
            except Exception as e:
                groq_circuit_breaker.record_failure()
                logger.warning(f"Groq API failed: {str(e)}")
                logger.info("Step 3: Falling back to rule-based chatbot")
        else:
            logger.info("Groq API circuit breaker open or service unavailable, using fallback")
            
        # Step 3: Fallback to rule-based chatbot with enhanced error handling
        try:
            response = rule_based_chatbot.get_response(enhanced_message)
            logger.info("Successfully got response from rule-based chatbot")
            
            return jsonify({
                "response": response,
                "source": "rule_based",
                "enhanced_query": enhanced_message != user_message,
                "original_message": user_message,
                "enhanced_message": enhanced_message if enhanced_message != user_message else None,
                "fallback_reason": "API services unavailable or circuit breaker open"
            })
        except Exception as fallback_error:
            logger.error(f"Rule-based chatbot also failed: {str(fallback_error)}")
            # Try with original message as last resort
            try:
                response = rule_based_chatbot.get_response(user_message)
                logger.info("Fallback successful with original message")
                
                return jsonify({
                    "response": response,
                    "source": "rule_based_fallback",
                    "enhanced_query": False,
                    "original_message": user_message,
                    "fallback_reason": f"Enhanced message failed, used original"
                })
            except Exception as final_error:
                logger.error(f"All fallbacks failed: {str(final_error)}")
                # Emergency response
                emergency_response = f"""Hello! I'm Aniru AI, Anirudh's personal assistant. I'm currently experiencing some technical difficulties, but I'm here to help you learn about Anirudh.

Anirudh is a passionate computer science student and full-stack developer with expertise in:
• Programming Languages: C++, Python, JavaScript
• Technologies: React, Node.js, Express, MongoDB
• Specialties: Data Structures, Algorithms, System Design

You can reach out to Anirudh at:
• Email: anirudh200503@gmail.com
• LinkedIn: https://www.linkedin.com/in/anirudh-t-b5b26a2aa/
• GitHub: https://github.com/anirudh-pedro

Please try asking your question again, and I'll do my best to provide you with detailed information about Anirudh's projects and achievements!"""
                
                return jsonify({
                    "response": emergency_response,
                    "source": "emergency_fallback",
                    "enhanced_query": False,
                    "original_message": user_message,
                    "fallback_reason": "All systems temporarily unavailable"
                })
                
    except Exception as e:
        logger.error(f"Unexpected error in chat endpoint: {str(e)}")
        
        # Final fallback
        try:
            response = rule_based_chatbot.get_response(data.get('message', ''))
            return jsonify({
                "response": response,
                "source": "rule_based",
                "enhanced_query": False,
                "fallback_reason": "Unexpected error occurred"
            })
        except:
            return jsonify({
                "response": "I'm sorry, I'm experiencing technical difficulties. Please try again later.",
                "source": "error_fallback",
                "enhanced_query": False
            })

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    debug = os.environ.get('FLASK_ENV') == 'development'
    
    logger.info(f"Starting Aniru AI Backend on port {port}")
    app.run(host='0.0.0.0', port=port, debug=debug)