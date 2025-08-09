import React from 'react';
import { MessageCircle, Settings } from 'lucide-react';
import aniruLogo from '../assets/anirulogo.jpeg';

const Navbar = ({ activeSection, setActiveSection }) => {
  const navItems = [
    {
      id: 'chatbot',
      label: 'Chat',
      icon: MessageCircle
    },
    {
      id: 'pipeline',
      label: 'Pipeline',
      icon: Settings
    }
  ];

  return (
    <nav className="bg-black shadow-lg border-b border-gray-800">
      <div className="max-w-7xl mx-auto px-4">
        <div className="flex justify-between items-center h-20">
          <div className="flex items-center space-x-3">
            <div className="w-12 h-12 rounded-lg overflow-hidden flex items-center justify-center">
              <img 
                src={aniruLogo} 
                alt="Aniru AI Logo" 
                className="w-30 h-30 object-contain scale-160"
              />
            </div>
            <span className="text-xl font-bold text-white">Aniru AI</span>
          </div>

          <div className="flex space-x-2">
            {navItems.map((item) => {
              const IconComponent = item.icon;
              return (
                <button
                  key={item.id}
                  onClick={() => setActiveSection(item.id)}
                  className={`px-4 py-2 rounded-lg flex items-center space-x-2 transition-all duration-200 ${
                    activeSection === item.id
                      ? 'bg-blue-900 text-white'
                      : 'text-gray-300 hover:bg-blue-800 hover:text-white'
                  }`}
                >
                  <IconComponent className="w-4 h-4" />
                  <span>{item.label}</span>
                </button>
              );
            })}
          </div>
        </div>
      </div>
    </nav>
  );
};

export default Navbar;
