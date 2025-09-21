import React, { useState, useEffect, useRef } from 'react';
import { Bot } from 'lucide-react';
import MessageBubble from './components/MessageBubble';
import LoadingBubble from './components/LoadingBubble';
import ChatInput from './components/ChatInput';
import ErrorBoundary from './components/ErrorBoundary'; // <-- IMPORT THE ERROR BOUNDARY

function App() {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const messagesEndRef = useRef(null);

  useEffect(() => {
    setMessages([{ 
        id: crypto.randomUUID(), // <-- ADD UNIQUE ID
        role: 'assistant', 
        content: "Hello! How can I help you explore the ARGO data today?" 
    }]);
  }, []);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!input.trim() || isLoading) return;

    const userMessage = { 
        id: crypto.randomUUID(), // <-- ADD UNIQUE ID
        role: 'user', 
        content: input 
    };
    setMessages((prev) => [...prev, userMessage]);
    setIsLoading(true);
    setInput('');

    try {
      const response = await fetch('http://127.0.0.1:8000/ask', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ question: input }),
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || `API error: ${response.statusText}`);
      }

      const data = await response.json();
      
      const assistantMessage = {
        id: crypto.randomUUID(), // <-- ADD UNIQUE ID
        role: 'assistant',
        content: data.summary,
        data: data.data,
        sql: data.sql_query,
      };
      setMessages((prev) => [...prev, assistantMessage]);

    } catch (error) {
      const errorMessage = { 
        id: crypto.randomUUID(), // <-- ADD UNIQUE ID
        role: 'assistant', 
        content: `Sorry, I encountered an error: ${error.message}`, 
        isError: true 
      };
      setMessages((prev) => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="flex flex-col h-screen bg-slate-900 text-slate-100 font-sans">
      <header className="bg-slate-800 p-4 border-b border-slate-700 shadow-lg">
        <h1 className="text-xl md:text-2xl font-bold flex items-center text-cyan-400">
          <Bot className="mr-3" size={32} />
          <span>OceanGPT: Your ARGO Data Assistant</span>
        </h1>
      </header>

      <main className="flex-1 overflow-y-auto p-4 md:p-6 space-y-8">
        {messages.map((msg) => (
          // --- WRAP THE BUBBLE IN THE ERROR BOUNDARY ---
          <ErrorBoundary key={msg.id}> 
            <MessageBubble msg={msg} />
          </ErrorBoundary>
          // --- END OF WRAPPER ---
        ))}
        {isLoading && <LoadingBubble />}
        <div ref={messagesEndRef} />
      </main>

      <ChatInput 
        input={input}
        setInput={setInput}
        handleSubmit={handleSubmit}
        isLoading={isLoading}
      />
    </div>
  );
}

export default App;