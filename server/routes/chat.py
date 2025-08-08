from flask import Blueprint, request, jsonify
import logging

# This file is kept for modular structure
# The main chat logic is implemented in app.py
# Additional routes can be added here if needed

logger = logging.getLogger(__name__)

chat_bp = Blueprint('chat', __name__)

@chat_bp.route('/health', methods=['GET'])
def health():
    """Health check for chat service"""
    return jsonify({
        "status": "healthy",
        "service": "chat_routes",
        "message": "Chat service is running"
    })

@chat_bp.route('/test', methods=['POST'])
def test_services():
    """Test all services"""
    try:
        from services.fireworks_service import FireworksService
        from services.groq_service import GroqService
        from services.rule_based_chatbot import RuleBasedChatbot
        
        fireworks_service = FireworksService()
        groq_service = GroqService()
        rule_based_chatbot = RuleBasedChatbot()
        
        results = {
            "fireworks": fireworks_service.test_connection(),
            "groq": groq_service.test_connection(),
            "rule_based": rule_based_chatbot.test_functionality()
        }
        
        return jsonify({
            "status": "completed",
            "tests": results
        })
        
    except Exception as e:
        logger.error(f"Service test error: {str(e)}")
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500