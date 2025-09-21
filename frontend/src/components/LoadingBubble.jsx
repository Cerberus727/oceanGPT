import React from 'react';
import { Bot, LoaderCircle } from 'lucide-react';

const LoadingBubble = () => {
  return (
    <div className="flex items-start gap-4">
      <Bot className="text-cyan-400 flex-shrink-0" size={28} />
      <div className="p-4 rounded-lg bg-slate-700 flex items-center shadow-md">
        <LoaderCircle className="animate-spin mr-2" />
        Thinking...
      </div>
    </div>
  );
};

export default LoadingBubble;