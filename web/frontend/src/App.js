import React, { useState, useRef, useEffect } from "react";
import "./App.css";

// Use environment variable or fallback to local development
const API_URL = process.env.REACT_APP_API_URL || "http://localhost:8000/chat";

// Debug log to verify the API URL
console.log("🔗 API_URL:", API_URL);
console.log("🌍 NODE_ENV:", process.env.NODE_ENV);

export default function App() {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const [isInitialState, setIsInitialState] = useState(true);
  const messagesEndRef = useRef(null);
  const textareaRef = useRef(null);

  // Cursor-following background effect
  useEffect(() => {
    const handleMouseMove = (e) => {
      document.documentElement.style.setProperty('--mouse-x', e.clientX + 'px');
      document.documentElement.style.setProperty('--mouse-y', e.clientY + 'px');
    };
    window.addEventListener('mousemove', handleMouseMove);
    return () => window.removeEventListener('mousemove', handleMouseMove);
  }, []);

  // Auto-resize textarea
  useEffect(() => {
    if (textareaRef.current) {
      textareaRef.current.style.height = 'auto';
      textareaRef.current.style.height = `${Math.min(textareaRef.current.scrollHeight, 120)}px`;
    }
  }, [input]);

  // Scroll to bottom on new message
  useEffect(() => {
    if (messagesEndRef.current) {
      messagesEndRef.current.scrollIntoView({ behavior: "smooth" });
    }
  }, [messages, loading]);

  const sendMessage = async (e) => {
    e.preventDefault();
    if (!input.trim()) return;
    
    const messageText = input.trim();
    setInput("");
    
    if (isInitialState) setIsInitialState(false);
    setLoading(true);
    
    const userMsg = { 
      sender: "user", 
      text: messageText, 
      time: new Date().toLocaleTimeString() 
    };
    setMessages((msgs) => [...msgs, userMsg]);
    
    try {
      console.log("🚀 Sending request to:", API_URL);
      console.log("📝 Message:", messageText);
      
      const res = await fetch(API_URL, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ message: messageText })
      });
      
      console.log("📡 Response status:", res.status);
      
      if (!res.ok) {
        throw new Error(`HTTP error! status: ${res.status}`);
      }
      
      const data = await res.json();
      console.log("✅ Response data:", data);
      
      setMessages((msgs) => [
        ...msgs,
        { 
          sender: "bot", 
          text: data.answer, 
          time: new Date().toLocaleTimeString() 
        }
      ]);
    } catch (error) {
      console.error("❌ Error:", error);
      setMessages((msgs) => [
        ...msgs,
        { 
          sender: "bot", 
          text: `Error: Could not connect to AI. ${error.message}`, 
          time: new Date().toLocaleTimeString() 
        }
      ]);
    }
    setLoading(false);
  };

  const handleKeyDown = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      sendMessage(e);
    }
  };

  return (
    <div className="mosdac-root">
      <aside className="sidebar" aria-label="Main navigation">
        <div className="sidebar-top">
          <div className="logo" aria-label="MOSDAC AI Logo">
            <svg width="36" height="36" viewBox="0 0 36 36">
              <circle cx="18" cy="18" r="16" fill="#3b82f6" />
              <text x="18" y="24" textAnchor="middle" fontSize="18" fill="#ffffff" fontWeight="bold">M</text>
            </svg>
          </div>
          <nav>
            <ul>
              <li>
                <button className="sidebar-icon" aria-label="New Chat">
                  <svg width="22" height="22" viewBox="0 0 22 22">
                    <path d="M11 5v12M5 11h12" stroke="currentColor" strokeWidth="2" strokeLinecap="round"/>
                  </svg>
                  <span className="nav-label">New</span>
                </button>
              </li>
              <li>
                <button className="sidebar-icon" aria-label="Home">
                  <svg width="22" height="22" viewBox="0 0 22 22">
                    <path d="M4 10.5L11 4l7 6.5V19a1 1 0 0 1-1 1H5a1 1 0 0 1-1-1V10.5z" 
                          stroke="currentColor" strokeWidth="2" fill="none"/>
                  </svg>
                  <span className="nav-label">Home</span>
                </button>
              </li>
            </ul>
          </nav>
        </div>
        <div className="sidebar-bottom">
          <div className="profile-section">
            <div className="avatar" aria-label="User profile">
              <svg width="24" height="24" viewBox="0 0 24 24" fill="currentColor">
                <path d="M12 12c2.21 0 4-1.79 4-4s-1.79-4-4-4-4 1.79-4 4 1.79 4 4 4zm0 2c-2.67 0-8 1.34-8 4v2h16v-2c0-2.66-5.33-4-8-4z"/>
              </svg>
            </div>
            <span className="notif-dot" aria-label="Notification">3</span>
          </div>
        </div>
      </aside>

      <div className={`chat-container ${isInitialState ? "initial-state" : "conversation-state"}`}>
        <div className="logo-section">
          <h1 className="gradient-text">MOSDAC AI</h1>
          <p className="subtitle">Your intelligent assistant for satellite data and research</p>
        </div>

        <div className="messages-container">
          {messages.map((msg, i) => (
            <div key={i} className={`message ${msg.sender}-message`}>
              <div className="message-content">
                <div className="message-text">{msg.text}</div>
                <div className="message-timestamp">{msg.time}</div>
              </div>
            </div>
          ))}
          
          {loading && (
            <div className="message assistant-message">
              <div className="message-content typing-indicator">
                <div className="typing-dots">
                  <div className="typing-dot"></div>
                  <div className="typing-dot"></div>
                  <div className="typing-dot"></div>
                </div>
                <span className="typing-text">AI is thinking...</span>
              </div>
            </div>
          )}
          <div ref={messagesEndRef} />
        </div>

        <div className="input-section">
          <form className="input-form" onSubmit={sendMessage}>
            <div className="input-wrapper">
              <textarea
                ref={textareaRef}
                className="chat-input"
                placeholder="Ask anything about satellite data, research, or MOSDAC..."
                value={input}
                onChange={e => setInput(e.target.value)}
                onKeyDown={handleKeyDown}
                disabled={loading}
                rows={1}
                autoFocus
              />
              <button 
                type="submit" 
                className="submit-button" 
                disabled={loading || !input.trim()}
                aria-label="Send message"
              >
                {loading ? (
                  <svg className="loading-spinner" width="20" height="20" viewBox="0 0 20 20" fill="currentColor">
                    <path d="M10 2a8 8 0 018 8 1 1 0 01-2 0 6 6 0 00-6-6 1 1 0 010-2z"/>
                  </svg>
                ) : (
                  <svg width="20" height="20" viewBox="0 0 20 20" fill="currentColor">
                    <path d="M2 10l16-8-8 16-1-7-7-1z"/>
                  </svg>
                )}
              </button>
            </div>
          </form>
        </div>
      </div>
    </div>
  );
}
