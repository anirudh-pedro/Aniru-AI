import React, { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import Navbar from './components/Navbar';
import Chatbot from './components/Chatbot';
import PipelineSetup from './components/PipelineSetup';

const App = () => {
  const [activeSection, setActiveSection] = useState('chatbot');

  const renderActiveSection = () => {
    switch (activeSection) {
      case 'chatbot':
        return <Chatbot />;
      case 'pipeline':
        return <PipelineSetup />;
      default:
        return <Chatbot />;
    }
  };

  return (
    <div className="h-screen flex flex-col bg-black">
      <Navbar activeSection={activeSection} setActiveSection={setActiveSection} />
      
      <div className="flex-1 overflow-hidden">
        <AnimatePresence mode="wait">
          <motion.div
            key={activeSection}
            initial={{ opacity: 0, x: 20 }}
            animate={{ opacity: 1, x: 0 }}
            exit={{ opacity: 0, x: -20 }}
            transition={{ duration: 0.3 }}
            className="h-full"
          >
            {renderActiveSection()}
          </motion.div>
        </AnimatePresence>
      </div>
    </div>
  );
};

export default App;