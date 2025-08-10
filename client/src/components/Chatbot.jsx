import React, { useState, useRef, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Send, Bot, User, Loader2, Sparkles } from 'lucide-react';
import Message from './Message';

const Chatbot = () => {
  const [messages, setMessages] = useState([
    {
      id: 1,
      text: "Hey there, I'm Aniru AI — A Personal AI Assistant who knows everything about Anirudh's professional career. Ask me anything about him, okay? ✨",
      sender: 'bot',
      timestamp: new Date()
    }
  ]);
  const [inputMessage, setInputMessage] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const messagesEndRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    const handleResize = () => {
      if (window.innerWidth <= 768) {
        const vh = window.innerHeight * 0.01;
        document.documentElement.style.setProperty('--vh', `${vh}px`);
        
        setTimeout(() => {
          scrollToBottom();
        }, 100);
      }
    };

    handleResize();
    
    window.addEventListener('resize', handleResize);
    return () => window.removeEventListener('resize', handleResize);
  }, []);

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const handleSendMessage = async (e) => {
    e.preventDefault();
    if (!inputMessage.trim() || isLoading) return;

    const userMessage = {
      id: Date.now(),
      text: inputMessage,
      sender: 'user',
      timestamp: new Date()
    };

    setMessages(prev => [...prev, userMessage]);
    setInputMessage('');
    setIsLoading(true);

    try {
      const { sendMessage } = await import('../services/api');
      const response = await sendMessage(inputMessage);
      
      const botResponse = {
        id: Date.now() + 1,
        text: response.response,
        sender: 'bot',
        timestamp: new Date(),
        source: response.source,
        enhanced: response.enhanced_query
      };
      
      setMessages(prev => [...prev, botResponse]);
      setIsLoading(false);
    } catch (error) {
      console.error('Error sending message:', error);
      
      const errorResponse = {
        id: Date.now() + 1,
        text: "I'm sorry, I'm having trouble connecting right now. Please try again in a moment, or feel free to ask me about Anirudh's skills, projects, or experience!",
        sender: 'bot',
        timestamp: new Date(),
        source: 'error_fallback'
      };
      
      setMessages(prev => [...prev, errorResponse]);
      setIsLoading(false);
    }
  };

  const quickActions = [
    "Tell me about Anirudh's skills",
    "Show me his projects",
    "What's his experience?",
    "How can I contact him?"
  ];

  const handleQuickAction = (action) => {
    setInputMessage(action);
  };

  return (
    <div className="flex justify-center items-start min-h-full bg-gradient-to-br from-gray-900 to-black p-4">
      <div className="w-full max-w-4xl bg-gray-800 rounded-2xl shadow-2xl border border-gray-700 overflow-hidden flex flex-col h-[calc(100vh-120px)] sm:h-[calc(100vh-120px)]" style={{ height: 'calc(100vh - 120px)', minHeight: 'calc(100vh - 120px)' }}>
        <div className="bg-gray-800 shadow-lg border-b border-gray-700 p-4">
          <div className="flex items-center space-x-3">
            <div className="relative">
              <div className="w-10 h-10 bg-blue-900 rounded-full flex items-center justify-center shadow-lg">
                <Bot className="w-6 h-6 text-white" />
              </div>
              <div className="absolute -bottom-1 -right-1 w-4 h-4 bg-green-400 border-2 border-gray-800 rounded-full"></div>
            </div>
            <div>
              <h2 className="text-lg font-semibold text-white">Aniru AI</h2>
              <p className="text-sm text-gray-400">Personal Assistant • Online</p>
            </div>
          </div>
        </div>

        <div className="flex-1 overflow-y-auto p-6 space-y-4 bg-gray-900">
          <AnimatePresence>
            {messages.map((message) => (
              <Message key={message.id} message={message} />
            ))}
          </AnimatePresence>

          {isLoading && (
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              className="flex items-center space-x-2 text-gray-400"
            >
              <div className="w-8 h-8 bg-gray-800 rounded-full flex items-center justify-center">
                <Bot className="w-4 h-4 text-cyan-400" />
              </div>
              <div className="flex items-center space-x-1">
                <Loader2 className="w-4 h-4 animate-spin text-cyan-400" />
                <span className="text-sm">Aniru AI is typing...</span>
              </div>
            </motion.div>
          )}
          <div ref={messagesEndRef} />
        </div>

        {messages.length <= 2 && (
          <div className="px-6 pb-4 bg-gray-900">
            <div className="flex flex-wrap gap-2">
              {quickActions.map((action, index) => (
                <motion.button
                  key={index}
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: index * 0.1 }}
                  onClick={() => handleQuickAction(action)}
                  className="px-3 py-1.5 bg-blue-900 border border-blue-700 rounded-full text-sm text-gray-300 hover:bg-blue-800 hover:text-white hover:border-blue-600 transition-all duration-200"
                >
                  <Sparkles className="w-3 h-3 inline mr-1" />
                  {action}
                </motion.button>
              ))}
            </div>
          </div>
        )}

        <div className="p-6 bg-gray-800 border-t border-gray-700" style={{ position: 'relative' }}>
          <form onSubmit={handleSendMessage} className="flex space-x-3">
            <div className="flex-1 relative">
              <input
                type="text"
                value={inputMessage}
                onChange={(e) => setInputMessage(e.target.value)}
                placeholder="Ask me anything about Anirudh's portfolio..."
                className="w-full px-4 py-3 border border-gray-600 bg-gray-700 text-white rounded-xl focus:outline-none focus:ring-2 focus:ring-cyan-500 focus:border-transparent resize-none placeholder-gray-400"
                disabled={isLoading}
                style={{ fontSize: '16px' }}
              />
            </div>
            <motion.button
              type="submit"
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.95 }}
              disabled={!inputMessage.trim() || isLoading}
              className="px-6 py-3 bg-blue-900 text-white rounded-xl hover:bg-blue-800 disabled:opacity-50 disabled:cursor-not-allowed transition-all duration-200 flex items-center space-x-2 shadow-lg shadow-blue-500/25"
            >
              <Send className="w-4 h-4" />
            </motion.button>
          </form>
        </div>
      </div>
    </div>
  );
};

export default Chatbot;