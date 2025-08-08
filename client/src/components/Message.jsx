import React from 'react';
import { motion } from 'framer-motion';
import { Bot, User, Clock, ExternalLink } from 'lucide-react';

const Message = ({ message }) => {
  const isBot = message.sender === 'bot';
  
  const formatTime = (timestamp) => {
    return new Date(timestamp).toLocaleTimeString([], { 
      hour: '2-digit', 
      minute: '2-digit' 
    });
  };

  // Function to format bot messages with proper line breaks and styling
  const formatBotMessage = (text) => {
    if (!isBot) return text;

    // Split text into lines
    const lines = text.split('\n');
    
    return lines.map((line, index) => {
      // Skip empty lines but add spacing
      if (!line.trim()) {
        return <br key={index} />;
      }

      // Handle numbered lists (1. 2. 3. etc.)
      if (/^\d+\.\s/.test(line)) {
        const match = line.match(/^(\d+)\.\s(.+)/);
        if (match) {
          const [, number, content] = match;
          // Handle bold project names
          const formattedContent = content.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');
          return (
            <div key={index} className="mb-3">
              <div className="flex items-start space-x-2">
                <span className="font-bold text-cyan-400 mt-0.5">{number}.</span>
                <div 
                  className="flex-1"
                  dangerouslySetInnerHTML={{ __html: formattedContent }}
                />
              </div>
            </div>
          );
        }
      }

      // Handle bullet points
      if (line.startsWith('• ') || line.startsWith('* ')) {
        const content = line.substring(2);
        // Handle links in bullet points - support both "Link:" and "Live Demo:" formats
        if (content.startsWith('Link: ') || content.startsWith('Live Demo: ')) {
          const linkType = content.startsWith('Link: ') ? 'Link' : 'Live Demo';
          const url = content.startsWith('Link: ') ? content.substring(6) : content.substring(11);
          return (
            <div key={index} className="ml-4 mb-1 flex items-center space-x-1">
              <span className="text-cyan-400">•</span>
              <span className="text-sm text-gray-300">{linkType}:</span>
              <a 
                href={url.trim()} 
                target="_blank" 
                rel="noopener noreferrer"
                className="text-blue-400 hover:text-blue-300 underline text-sm flex items-center space-x-1"
              >
                <span>{url.trim()}</span>
                <ExternalLink className="w-3 h-3" />
              </a>
            </div>
          );
        } else {
          // Handle bold text in bullet points
          const formattedContent = content.replace(/\*\*(.*?)\*\*/g, '<strong class="text-white">$1</strong>');
          return (
            <div key={index} className="ml-4 mb-1 flex items-start space-x-2">
              <span className="text-cyan-400 mt-0.5">•</span>
              <div 
                className="flex-1 text-sm"
                dangerouslySetInnerHTML={{ __html: formattedContent }}
              />
            </div>
          );
        }
      }

      // Handle regular text with bold formatting and URL detection
      let processedLine = line;
      
      // Handle markdown-style links [text](url)
      const markdownLinkRegex = /\[([^\]]+)\]\(([^)]+)\)/g;
      const markdownLinks = [...line.matchAll(markdownLinkRegex)];
      
      if (markdownLinks.length > 0) {
        const parts = [];
        let lastIndex = 0;
        
        markdownLinks.forEach((match) => {
          const [fullMatch, linkText, url] = match;
          const matchStart = match.index;
          
          // Add text before the link
          if (matchStart > lastIndex) {
            parts.push({
              type: 'text',
              content: line.substring(lastIndex, matchStart)
            });
          }
          
          // Add the link
          parts.push({
            type: 'link',
            content: linkText,
            url: url
          });
          
          lastIndex = matchStart + fullMatch.length;
        });
        
        // Add remaining text after last link
        if (lastIndex < line.length) {
          parts.push({
            type: 'text',
            content: line.substring(lastIndex)
          });
        }
        
        return (
          <div key={index} className="mb-2 leading-relaxed flex flex-wrap items-center">
            {parts.map((part, partIndex) => {
              if (part.type === 'link') {
                return (
                  <a
                    key={partIndex}
                    href={part.url}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="text-blue-400 hover:text-blue-300 underline mx-1 flex items-center space-x-1"
                  >
                    <span>{part.content}</span>
                    <ExternalLink className="w-3 h-3" />
                  </a>
                );
              } else {
                // Apply bold formatting to text parts
                const boldFormatted = part.content.replace(/\*\*(.*?)\*\*/g, '<strong class="text-white">$1</strong>');
                return (
                  <span 
                    key={partIndex} 
                    dangerouslySetInnerHTML={{ __html: boldFormatted }}
                  />
                );
              }
            })}
          </div>
        );
      }
      
      // Handle regular URLs in text (including those wrapped in bold formatting)
      const urlRegex = /(https?:\/\/[^\s\*]+)/g;
      const hasUrl = line.match(urlRegex);
      
      if (hasUrl) {
        // First, extract URLs from bold formatting if they exist
        let processedLine = line.replace(/\*\*(https?:\/\/[^\s\*]+)\*\*/g, '$1');
        const parts = processedLine.split(urlRegex);
        
        return (
          <div key={index} className="mb-2 leading-relaxed flex flex-wrap items-center">
            {parts.map((part, partIndex) => {
              if (part.match(/^https?:\/\//)) {
                return (
                  <a
                    key={partIndex}
                    href={part}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="text-blue-400 hover:text-blue-300 underline mx-1 flex items-center space-x-1"
                  >
                    <span>{part}</span>
                    <ExternalLink className="w-3 h-3" />
                  </a>
                );
              } else {
                // Apply bold formatting to non-URL parts (but not to URLs)
                const boldFormatted = part.replace(/\*\*((?!https?:\/\/)[^*]+)\*\*/g, '<strong class="text-white">$1</strong>');
                return (
                  <span 
                    key={partIndex} 
                    dangerouslySetInnerHTML={{ __html: boldFormatted }}
                  />
                );
              }
            })}
          </div>
        );
      }
      
      // Handle regular text with bold formatting only
      // Remove bold formatting from URLs first, then apply bold to other text
      const cleanedLine = line.replace(/\*\*(https?:\/\/[^\s\*]+)\*\*/g, '$1');
      const formattedLine = cleanedLine.replace(/\*\*((?!https?:\/\/)[^*]+)\*\*/g, '<strong class="text-white">$1</strong>');
      
      return (
        <div 
          key={index} 
          className="mb-2 leading-relaxed"
          dangerouslySetInnerHTML={{ __html: formattedLine }}
        />
      );
    });
  };

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      className={`flex items-start space-x-3 ${isBot ? '' : 'flex-row-reverse space-x-reverse'}`}
    >
      {/* Avatar */}
      <div className={`flex-shrink-0 w-8 h-8 rounded-full flex items-center justify-center shadow-lg ${
        isBot 
          ? 'bg-gradient-to-br from-cyan-400 to-blue-500' 
          : 'bg-gradient-to-br from-emerald-400 to-green-500'
      }`}>
        {isBot ? (
          <Bot className="w-4 h-4 text-white" />
        ) : (
          <User className="w-4 h-4 text-white" />
        )}
      </div>

      {/* Message Content */}
      <div className={`flex-1 max-w-xs sm:max-w-md lg:max-w-lg xl:max-w-xl ${isBot ? '' : 'flex justify-end'}`}>
        <div className={`relative px-4 py-3 rounded-2xl shadow-lg ${
          isBot
            ? 'bg-gray-800 border border-gray-700 text-gray-100'
            : 'bg-gradient-to-r from-cyan-500 to-blue-500 text-white'
        }`}>
          {/* Message Text */}
          <div className="text-sm leading-relaxed">
            {isBot ? formatBotMessage(message.text) : message.text}
          </div>
          
          {/* Timestamp */}
          <div className={`flex items-center mt-2 pt-2 border-t border-opacity-20 text-xs ${
            isBot ? 'text-gray-400 border-gray-600' : 'text-cyan-100 border-cyan-300'
          }`}>
            <Clock className="w-3 h-3 mr-1" />
            {formatTime(message.timestamp)}
            {message.source && (
              <span className="ml-2 opacity-70">
                • {message.source === 'groq_api' ? 'AI' : message.source === 'rule_based' ? 'KB' : 'System'}
              </span>
            )}
          </div>

          {/* Speech bubble tail */}
          <div className={`absolute top-3 w-0 h-0 ${
            isBot
              ? '-left-2 border-r-8 border-r-gray-800 border-t-8 border-t-transparent border-b-8 border-b-transparent'
              : '-right-2 border-l-8 border-l-cyan-500 border-t-8 border-t-transparent border-b-8 border-b-transparent'
          }`}></div>
        </div>
      </div>
    </motion.div>
  );
};

export default Message;