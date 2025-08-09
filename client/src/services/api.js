import axios from 'axios';

// Production API URL
const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:5000';

// Create an axios instance with default configurations
const api = axios.create({
  baseURL: `${API_BASE_URL}/api`,
  headers: {
    'Content-Type': 'application/json',
  },
  timeout: 60000, // Increased to 60 seconds for AI requests
});

// Add request interceptor for debugging in development
api.interceptors.request.use(
  (config) => {
    if (import.meta.env.DEV) {
      console.log('🚀 API Request:', config.method?.toUpperCase(), config.url);
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Add response interceptor for error handling
api.interceptors.response.use(
  (response) => {
    if (import.meta.env.DEV) {
      console.log('✅ API Response:', response.status, response.config.url);
    }
    return response;
  },
  (error) => {
    // Enhanced error handling for production
    console.error('❌ API Error:', {
      message: error.message,
      status: error.response?.status,
      url: error.config?.url,
      environment: import.meta.env.MODE
    });
    
    // Handle different types of errors
    if (error.code === 'ECONNABORTED' && error.message.includes('timeout')) {
      error.message = 'Request timed out. The AI is taking longer than usual. Please try again.';
    } else if (!error.response) {
      error.message = 'Network error. Please check your connection and try again.';
    } else if (error.response?.status >= 500) {
      error.message = 'Server error. Please try again in a moment.';
    } else if (error.response?.status === 429) {
      error.message = 'Too many requests. Please wait a moment and try again.';
    }
    
    return Promise.reject(error);
  }
);

// Helper function for retrying requests
const retryRequest = async (requestFn, maxRetries = 2, delay = 1000) => {
  for (let attempt = 1; attempt <= maxRetries; attempt++) {
    try {
      return await requestFn();
    } catch (error) {
      console.log(`Attempt ${attempt} failed:`, error.message);
      
      // Don't retry on certain errors
      if (error.response?.status === 400 || error.response?.status === 401) {
        throw error;
      }
      
      // If this is the last attempt, throw the error
      if (attempt === maxRetries) {
        throw error;
      }
      
      // Wait before retrying
      await new Promise(resolve => setTimeout(resolve, delay * attempt));
    }
  }
};

// Chat API services
export const chatService = {
  // Main chat endpoint (matches Flask backend)
  sendMessage: async (message, options = {}) => {
    try {
      const payload = { 
        message
      };
      
      // Use retry mechanism for chat requests
      return await retryRequest(async () => {
        const response = await api.post('/chat', payload);
        return response.data;
      });
    } catch (error) {
      console.error('Error sending message:', error);
      throw error;
    }
  },

  // Fireworks.ai only endpoint
  sendFireworksMessage: async (message) => {
    try {
      const response = await api.post('/chat/fireworks-only', { message });
      return response.data;
    } catch (error) {
      console.error('Error sending Fireworks message:', error);
      throw error;
    }
  },

  // Groq only endpoint
  sendGroqMessage: async (message) => {
    try {
      const response = await api.post('/chat/groq-only', { message });
      return response.data;
    } catch (error) {
      console.error('Error sending Groq message:', error);
      throw error;
    }
  },

  // Rule-based only endpoint
  sendRuleBasedMessage: async (message) => {
    try {
      const response = await api.post('/chat/rule-based', { message });
      return response.data;
    } catch (error) {
      console.error('Error sending rule-based message:', error);
      throw error;
    }
  },

  // Get health status
  getHealth: async () => {
    try {
      const response = await api.get('/health');
      return response.data;
    } catch (error) {
      console.error('Error getting health status:', error);
      throw error;
    }
  },

  // Check API status
  getApiStatus: async () => {
    try {
      const response = await api.get('/status');
      return response.data;
    } catch (error) {
      console.error('Error getting API status:', error);
      throw error;
    }
  },

  // Simple health check (for monitoring)
  ping: async () => {
    try {
      const response = await axios.get(`${API_BASE_URL}/health`);
      return response.data;
    } catch (error) {
      console.error('Error pinging API:', error);
      throw error;
    }
  },

  // Get settings
  getSettings: async () => {
    try {
      const response = await api.get('/settings');
      return response.data;
    } catch (error) {
      console.error('Error getting settings:', error);
      throw error;
    }
  },

  // Update settings
  updateSettings: async (settings) => {
    try {
      const response = await api.post('/settings', settings);
      return response.data;
    } catch (error) {
      console.error('Error updating settings:', error);
      throw error;
    }
  },

  // Get profile data
  getProfile: async () => {
    try {
      const response = await api.get('/profile');
      return response.data;
    } catch (error) {
      console.error('Error getting profile:', error);
      throw error;
    }
  },

  // Get available models
  getModels: async () => {
    try {
      const response = await api.get('/models');
      return response.data;
    } catch (error) {
      console.error('Error getting models:', error);
      throw error;
    }
  },

  // Switch model
  switchModel: async (model) => {
    try {
      const response = await api.post('/switch-model', { model });
      return response.data;
    } catch (error) {
      console.error('Error switching model:', error);
      throw error;
    }
  }
};

export default api;

// Export the main sendMessage function for easy import
export const sendMessage = chatService.sendMessage;