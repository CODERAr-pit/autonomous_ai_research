'use client'
import { useState, useRef, useEffect } from "react";
import ReactMarkdown from 'react-markdown';

// 1. Define a message structure to hold the chat history
interface Message {
  role: 'user' | 'ai';
  content: string;
  time?: string | null;
}

export default function Home() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState<string>("");
  const [isLoading, setIsLoading] = useState<boolean>(false);
  
  // Reference to auto-scroll to the bottom of the chat
  const messagesEndRef = useRef<HTMLDivElement>(null);

  // Auto-scroll whenever messages update
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, isLoading]);

  async function handleSend() {
    if (!input.trim() || isLoading) return;

    const userQuery = input;
    setInput(""); // Clear input box immediately for good UX
    
    // 2. Add the user's message to the chat history
    setMessages(prev => [...prev, { role: 'user', content: userQuery }]);
    setIsLoading(true);

    try {
      const res = await fetch(`http://127.0.0.1:8000/run-agent/?query=${encodeURIComponent(userQuery)}`, {
        method: 'GET',
        headers: { 'content-type': 'application/json' }
      });

      if (!res.ok) throw new Error(`Server returned status: ${res.status}`);

      const time = res.headers.get("Total_access_time");
      const data = await res.json();
      
      // 3. Add the AI's response to the chat history
      setMessages(prev => [...prev, { 
        role: 'ai', 
        content: data.message || "No response received.",
        time: time
      }]);

    } catch (err: any) {
      setMessages(prev => [...prev, { 
        role: 'ai', 
        content: `**Error:** I couldn't connect to the server. (${err.message})` 
      }]);
    } finally {
      setIsLoading(false);
    }
  }

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  return (
    <div className="flex flex-col h-screen bg-balack text-gray-800 font-geist-sans">
      
      {/* Header */}
      <header className="p-4 flex items-center justify-between border-b border-gray-100">
        <h1 className="text-3xl font-bold font-geist-sans text-white">Xenum</h1>
      </header>

      {/* Chat History Area */}
      <div className="mb-16 flex-1 overflow-y-auto p-4 sm:p-6 w-full max-w-4xl mx-auto pb-32">
        
        {messages.length === 0 ? (
          <div className="h-full flex flex-col items-center justify-center text-center text-white space-y-4">
            <div className="w-16 h-16 bg-blue-100 text-blue-500 rounded-full flex items-center justify-center text-2xl">✨</div>
            <h2 className="text-2xl font-medium text-gray-600">How can I help you today?</h2>
          </div>
        ) : (
          <div className="space-y-6 ">
            {messages.map((msg, index) => (
              <div key={index} className={`flex flex-col ${msg.role === 'user' ? 'items-end' : 'items-start'}`}>
                
                {/* Message Bubble */}
                <div 
                  className={`px-5 py-3 rounded-2xl max-w-[85%] sm:max-w-[75%] ${
                    msg.role === 'user' 
                      ? 'bg-white text-black rounded-tr-sm' 
                      : 'bg-transparent text-gray-800'
                  }`}
                >
                  {msg.role === 'user' ? (
                    <p className="whitespace-pre-wrap">{msg.content}</p>
                  ) : (
                    // Tailwind 'prose' makes markdown look beautiful
                    <div className="bg-white rounded-3xl p-3 prose prose-sm sm:prose-base max-w-none text-black leading-relaxed">
                      <ReactMarkdown>{msg.content}</ReactMarkdown>
                    </div>
                  )}
                </div>

                {/* Optional: Access Time Badge for AI */}
                {msg.role === 'ai' && msg.time && (
                  <span className="text-xs text-gray-400 mt-1 ml-2">
                    {msg.time}s
                  </span>
                )}
              </div>
            ))}
            
            {/* Loading Indicator */}
            {isLoading && (
              <div className="flex items-start">
                <div className="px-5 py-4 bg-transparent text-gray-500 flex space-x-2 items-center">
                  <div className="w-2 h-2 bg-gray-300 rounded-full animate-bounce"></div>
                  <div className="w-2 h-2 bg-gray-300 rounded-full animate-bounce" style={{ animationDelay: '0.2s' }}></div>
                  <div className="w-2 h-2 bg-gray-300 rounded-full animate-bounce" style={{ animationDelay: '0.4s' }}></div>
                </div>
              </div>
            )}
            
            {/* Invisible div to scroll to */}
            <div ref={messagesEndRef} />
          </div>
        )}
      </div>

      {/* Input Area (Pinned to Bottom) */}
      <div className="fixed bottom-0 w-full bg-gradient-to-t from-white via-white to-transparent pt-6 pb-6 px-4">
        <div className="max-w-3xl mx-auto relative flex items-end bg-gray-100 rounded-3xl p-2 focus-within:ring-2 focus-within:ring-gray-200 transition-all shadow-sm">
          
          <textarea
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={handleKeyDown}
            placeholder="Ask anything..."
            className="flex-1 max-h-32 min-h-[44px] bg-transparent outline-none resize-none px-4 py-3 text-gray-800 placeholder-gray-500"
            rows={1}
          />
          
          <button 
            onClick={handleSend}
            disabled={!input.trim() || isLoading}
            className={`p-3 rounded-full mb-1 mr-1 transition-colors ${
              input.trim() && !isLoading
                ? 'bg-black text-white hover:bg-gray-800' 
                : 'bg-gray-200 text-gray-400 cursor-not-allowed'
            }`}
          >
            {/* Send Icon (SVG) */}
            <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="currentColor" className="w-5 h-5">
              <path d="M3.478 2.404a.75.75 0 0 0-.926.941l2.432 7.905H13.5a.75.75 0 0 1 0 1.5H4.984l-2.432 7.905a.75.75 0 0 0 .926.94 60.519 60.519 0 0 0 18.445-8.986.75.75 0 0 0 0-1.218A60.517 60.517 0 0 0 3.478 2.404Z" />
            </svg>
          </button>
        </div>
        <p className="text-center text-xs text-gray-400 mt-3">
          AI can make mistakes. Verify important info.
        </p>
      </div>

    </div>
  );
}