import React from 'react';
import image1 from '../assets/bc97f699-a633-4ce3-b996-7f7cf8e2e58e.jpeg'

const PipelineSetup = () => {
  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-900 via-gray-800 to-gray-900 text-white flex items-center justify-center px-4 py-8">
      <div className="text-center w-full max-w-6xl">
        <img 
          src={image1} 
          alt="AI Pipeline Architecture" 
          className="mx-auto w-full max-w-4xl h-auto max-h-[85vh] object-contain rounded-lg shadow-2xl mb-18"
        />
      </div>
    </div>
  );
};

export default PipelineSetup;
