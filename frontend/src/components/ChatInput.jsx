import React from 'react';
import { CornerDownLeft } from 'lucide-react';

const ChatInput = ({ input, setInput, handleSubmit, isLoading }) => {
  return (
    <footer className="p-4 bg-slate-800 border-t border-slate-700">
      <form onSubmit={handleSubmit} className="max-w-4xl mx-auto flex items-center bg-slate-700 rounded-lg p-2 shadow-inner">
        <input
          type="text"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          placeholder="e.g., Plot the temperature profile for float 53548 on cycle 97"
          className="w-full bg-transparent focus:outline-none p-2"
          disabled={isLoading}
        />
        <button type="submit" className="bg-blue-600 p-2 rounded-lg hover:bg-blue-500 disabled:bg-slate-500 transition-colors" disabled={isLoading}>
          <CornerDownLeft size={24} />
        </button>
      </form>
    </footer>
  );
};

export default ChatInput;