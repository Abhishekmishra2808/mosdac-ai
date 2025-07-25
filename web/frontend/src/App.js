import React, { useState, useEffect, useRef } from 'react';
import './App.css';

// Use environment variable or fallback to local development
const API_URL = process.env.REACT_APP_API_URL || "http://localhost:8000/chat";

// Debug log to verify the API URL
console.log("🔗 API_URL:", API_URL);
console.log("🌍 NODE_ENV:", process.env.NODE_ENV);


// --- SVG Icons as Components for cleaner JSX ---

const SatelliteLogo = ({ className, style }) => (
  <div className={className} style={style}>
    <svg viewBox="0 0 100 100" xmlns="http://www.w3.org/2000/svg">
      <defs>
        <linearGradient id="planetGradient" x1="0%" y1="0%" x2="100%" y2="100%">
          <stop offset="0%" style={{ stopColor: '#3b82f6' }} />
          <stop offset="100%" style={{ stopColor: '#58a6ff' }} />
        </linearGradient>
      </defs>
      <circle cx="50" cy="50" r="30" fill="url(#planetGradient)" />
      <path d="M 20 50 A 40 15 0 1 0 80 50 A 40 15 0 1 0 20 50" fill="none" stroke="#94a3b8" strokeWidth="5" />
      <circle cx="12" cy="42" r="6" fill="#c9d1d9" />
    </svg>
  </div>
);

const UserAvatar = () => (
    <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor" viewBox="0 0 16 16"><path d="M8 8a3 3 0 1 0 0-6 3 3 0 0 0 0 6Zm2-3a2 2 0 1 1-4 0 2 2 0 0 1 4 0Zm4 8c0 1-1 1-1 1H3s-1 0-1-1 1-4 6-4 6 3 6 4Zm-1-.004c-.001-.246-.154-.986-.832-1.664C11.516 10.68 10.289 10 8 10c-2.29 0-3.516.68-4.168 1.332-.678.678-.83 1.418-.832 1.664h10Z"/></svg>
);

const BotAvatar = () => (
    <div className="logo-svg" style={{ width: '18px', height: '18px', animation: 'none' }}><svg viewBox="0 0 100 100" xmlns="http://www.w3.org/2000/svg"><circle cx="50" cy="50" r="30" fill="#58a6ff"/><path d="M 20 50 A 40 15 0 1 0 80 50 A 40 15 0 1 0 20 50" fill="none" stroke="#0d1117" strokeWidth="5"/><circle cx="12" cy="42" r="6" fill="#0d1117"/></svg></div>
);


export default function App() {
  const [isChatActive, setIsChatActive] = useState(false);
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const messagesEndRef = useRef(null);
  const textareaRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages, loading]);
  
  useEffect(() => {
    if (textareaRef.current) {
        textareaRef.current.style.height = 'auto';
        textareaRef.current.style.height = `${textareaRef.current.scrollHeight}px`;
    }
  }, [input]);

  const transitionToChat = () => {
    setIsChatActive(true);
  };

  const resetChat = () => {
    setMessages([]);
  };

  const sendMessage = async (e) => {
    e.preventDefault();
    if (!input.trim() || loading) return;

    const messageText = input.trim();
    const userMsg = { sender: "user", text: messageText };

    setMessages(prev => [...prev, userMsg]);
    setInput("");
    setLoading(true);
    
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
        
        const botMsg = { sender: "bot", text: data.answer };
        setMessages((msgs) => [...msgs, botMsg]);

    } catch (error) {
        console.error("❌ Error:", error);
        const errorMsg = { 
          sender: "bot", 
          text: `Error: Could not connect to AI. ${error.message}`
        };
        setMessages((msgs) => [...msgs, errorMsg]);
    } finally {
        setLoading(false);
    }
  };

  return (
    <div id="app-wrapper" className={isChatActive ? 'chat-active' : ''}>
      <LandingPage onTryChatbot={transitionToChat} />
      <ChatInterface 
        messages={messages}
        input={input}
        setInput={setInput}
        loading={loading}
        onSendMessage={sendMessage}
        onResetChat={resetChat}
        messagesEndRef={messagesEndRef}
        textareaRef={textareaRef}
      />
    </div>
  );
}

// --- Sub-components for better organization ---

const LandingPage = ({ onTryChatbot }) => (
  <main id="landing-page">
    <div className="landing-content">
      <div className="landing-logo">
        <SatelliteLogo className="logo-svg" />
        <h1 className="landing-title animated-gradient-text">MOSDAC AI</h1>
      </div>
      <p className="landing-subtitle">Your intelligent assistant for satellite data, geospatial research, and mission analysis. Ask questions in natural language and get insights instantly.</p>
      <button id="try-chatbot-btn" onClick={onTryChatbot}>
        <span>Try MOSDAC AI</span>
        <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" fill="currentColor" viewBox="0 0 16 16"><path fillRule="evenodd" d="M4 8a.5.5 0 0 1 .5-.5h5.793L8.146 5.354a.5.5 0 1 1 .708-.708l3 3a.5.5 0 0 1 0 .708l-3 3a.5.5 0 0 1-.708-.708L10.293 8.5H4.5A.5.5 0 0 1 4 8z"/></svg>
      </button>
      <div className="section-divider"></div>
      <section className="how-it-works-section">
        <h2>How It's Made</h2>
        <div className="how-it-works-steps">
          <div className="how-it-works-step">
            <div className="step-number">1</div>
            <div className="step-details">
              <h3>Data Ingestion & Processing</h3>
              <p>Crawling and scraping dynamic and static data from the MOSDAC website. This raw data is then converted into a structured format, ready for the language model.</p>
            </div>
          </div>
          <div className="how-it-works-step">
            <div className="step-number">2</div>
            <div className="step-details">
              <h3>LLM Integration</h3>
              <p>The structured data is integrated with a powerful Large Language Model (Google's Gemini) to understand natural language and provide intelligent, context-aware responses.</p>
            </div>
          </div>
        </div>
      </section>
      <div className="section-divider"></div>
      <section className="features-section">
        <h2>Features</h2>
        <div className="features-grid">
          <div className="feature-card"><h3>Natural Language Queries</h3><p>Ask complex questions about satellite imagery and datasets just like you're talking to a person.</p></div>
          <div className="feature-card"><h3>Data Analysis</h3><p>Request summaries, trend analysis, and anomaly detection across vast archives of geospatial data.</p></div>
          <div className="feature-card"><h3>Mission Support</h3><p>Get quick access to documentation, mission parameters, and operational status.</p></div>
        </div>
      </section>
      <footer className="landing-footer">
        <p>Made by Abhishek Mishra</p>
        <div className="social-links">
          <a href="https://github.com/Abhishekmishra2808" target="_blank" rel="noopener noreferrer" aria-label="GitHub"><svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" fill="currentColor" viewBox="0 0 16 16"><path d="M8 0C3.58 0 0 3.58 0 8c0 3.54 2.29 6.53 5.47 7.59.4.07.55-.17.55-.38 0-.19-.01-.82-.01-1.49-2.01.37-2.53-.49-2.69-.94-.09-.23-.48-.94-.82-1.13-.28-.15-.68-.52-.01-.53.63-.01 1.08.58 1.23.82.72 1.21 1.87.87 2.33.66.07-.52.28-.87.51-1.07-1.78-.2-3.64-.89-3.64-3.95 0-.87.31-1.59.82-2.15-.08-.2-.36-1.02.08-2.12 0 0 .67-.21 2.2.82.64-.18 1.32-.27 2-.27.68 0 1.36.09 2 .27 1.53-1.04 2.2-.82 2.2-.82.44 1.1.16 1.92.08 2.12.51.56.82 1.27.82 2.15 0 3.07-1.87 3.75-3.65 3.95.29.25.54.73.54 1.48 0 1.07-.01 1.93-.01 2.2 0 .21.15.46.55.38A8.012 8.012 0 0 0 16 8c0-4.42-3.58-8-8-8z"/></svg></a>
          <a href="https://www.linkedin.com/in/abhishek-mishra-b76993317/" target="_blank" rel="noopener noreferrer" aria-label="LinkedIn"><svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" fill="currentColor" viewBox="0 0 16 16"><path d="M0 1.146C0 .513.526 0 1.175 0h13.65C15.474 0 16 .513 16 1.146v13.708c0 .633-.526 1.146-1.175 1.146H1.175C.526 16 0 15.487 0 14.854V1.146zm4.943 12.248V6.169H2.542v7.225h2.401zm-1.2-8.212c.837 0 1.358-.554 1.358-1.248-.015-.709-.52-1.248-1.342-1.248-.822 0-1.359.54-1.359 1.248 0 .694.521 1.248 1.327 1.248h.016zm4.908 8.212V9.359c0-.216.016-.432.08-.586.173-.431.568-.878 1.232-.878.869 0 1.216.662 1.216 1.634v3.865h2.401V9.25c0-2.22-1.184-3.252-2.764-3.252-1.274 0-1.845.7-2.165 1.193v.025h-.016a5.54 5.54 0 0 1 .016-.025V6.169h-2.4c.03.678 0 7.225 0 7.225h2.4z"/></svg></a>
        </div>
      </footer>
    </div>
  </main>
);

const ChatInterface = ({ messages, input, setInput, loading, onSendMessage, onResetChat, messagesEndRef, textareaRef }) => (
  <section id="chat-interface">
    <header className="chat-header">
      <div className="chat-header-title">
        <SatelliteLogo className="logo-svg" style={{ width: '28px', height: '28px', animation: 'none' }} />
        <span>MOSDAC AI</span>
      </div>
      <button id="new-chat-btn" onClick={onResetChat}>New Chat</button>
    </header>
    <div id="messages-container">
      {messages.length === 0 && !loading && <WelcomeView />}
      {messages.map((msg, index) => (
        <div key={index} className={`message ${msg.sender}-message`}>
          <div className="message-avatar">{msg.sender === 'user' ? <UserAvatar /> : <BotAvatar />}</div>
          <div className="message-content"><div className="message-text">{msg.text}</div></div>
        </div>
      ))}
      {loading && <TypingIndicator />}
      <div ref={messagesEndRef} />
    </div>
    <div className="chat-input-area">
      <form className="chat-input-wrapper" onSubmit={onSendMessage}>
        <textarea 
          id="chat-input" 
          ref={textareaRef}
          placeholder="Ask about satellite data..." 
          rows="1"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={(e) => {
            if (e.key === 'Enter' && !e.shiftKey) {
              e.preventDefault();
              onSendMessage(e);
            }
          }}
        />
        <button id="send-btn" type="submit" disabled={!input.trim() || loading}>
          <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" fill="currentColor" viewBox="0 0 16 16"><path d="M15.854.146a.5.5 0 0 1 .11.54l-5.819 14.547a.75.75 0 0 1-1.329.124l-3.178-4.995L.643 7.184a.75.75 0 0 1 .124-1.33L15.314.037a.5.5 0 0 1 .54.11ZM6.636 10.07l2.761 4.338L14.13 2.576 6.636 10.07Zm6.787-8.201L1.591 6.602l4.339 2.76 7.494-7.493Z"/></svg>
        </button>
      </form>
    </div>
  </section>
);

const WelcomeView = () => (
    <div className="chat-welcome-view">
        <SatelliteLogo className="logo-icon" style={{width: '56px', height: '56px', animation: 'none'}} />
        <h2>How can I help you today?</h2>
        <p>Ask me anything about MOSDAC services and data.</p>
    </div>
);

const TypingIndicator = () => (
    <div className="message bot-message">
        <div className="message-avatar"><BotAvatar /></div>
        <div className="message-content">
            <div className="typing-indicator">
                <div className="typing-dot"></div>
                <div className="typing-dot"></div>
                <div className="typing-dot"></div>
            </div>
        </div>
    </div>
);