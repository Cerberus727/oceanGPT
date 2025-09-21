import React from 'react';
import { Bot, User } from 'lucide-react';
import DataTable from './DataTable';
import DataMap from './DataMap';
import ProfileChart from './ProfileChart';

const MessageBubble = ({ msg }) => {
  // --- INTELLIGENT DISPLAY LOGIC ---
  const hasData = msg.data && msg.data.length > 0;
  
  // Condition 1: Check for location data to display the map
  const hasLocationData = hasData && 'latitude' in msg.data[0] && 'longitude' in msg.data[0];

  // Condition 2: Check for profile data to display the chart
  // This is the logic you asked for, translated into JavaScript.
  const isProfileData = hasData && 
                        msg.data.length > 1 && // Must have more than one point to draw a line
                        'pressure' in msg.data[0] && // Must have pressure for the Y-axis
                        ('temperature' in msg.data[0] || 'salinity' in msg.data[0]) && // Must have at least one variable to plot
                        new Set(msg.data.map(d => d.platform_number)).size === 1; // Must be for a single float
  // --- END OF LOGIC ---

  return (
    <div className={`flex items-start gap-4 ${msg.role === 'user' ? 'justify-end' : ''}`}>
      {msg.role === 'assistant' && <Bot className="text-cyan-400 flex-shrink-0 mt-1" size={28} />}
      <div className={`p-4 rounded-lg max-w-4xl w-full shadow-md ${msg.role === 'user' ? 'bg-blue-600' : 'bg-slate-700'} ${msg.isError ? 'bg-red-800/50 border border-red-500' : ''}`}>
        <p className="whitespace-pre-wrap">{msg.content}</p>
        
        {msg.sql && (
          <div className="mt-4 border-t border-slate-600 pt-2">
            <p className="text-xs text-slate-400 mb-1 font-semibold">Generated SQL Query:</p>
            <pre className="bg-slate-800 p-2 rounded text-xs text-green-300 overflow-x-auto"><code>{msg.sql}</code></pre>
          </div>
        )}

        {/* --- CONDITIONAL RENDERING --- */}
        {/* If it's profile data, show the chart. Otherwise, show the table. */}
        {hasData && !isProfileData && <DataTable data={msg.data} />}
        {isProfileData && <ProfileChart data={msg.data} />}

        {/* Always render the Map if location data is present */}
        {hasLocationData && <DataMap data={msg.data} />}
        {/* --- END OF RENDERING --- */}

      </div>
      {msg.role === 'user' && <User className="text-blue-400 flex-shrink-0 mt-1" size={28} />}
    </div>
  );
};

export default MessageBubble;