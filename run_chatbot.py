#!/usr/bin/env python3
"""
MOSDAC Chatbot - Main Application
Run this file to start the interactive chatbot with Gemini AI
"""

from chatbot import MOSDACChatbot

def main():
    """Main function to run the MOSDAC Chatbot"""
    print("🚀 Starting MOSDAC Chatbot...")
    print("📂 Loading data from: data/mosdac_content/")
    print("🤖 Connecting to Gemini AI...")
    print("-" * 50)
    
    try:
        # Initialize and run chatbot
        chatbot = MOSDACChatbot()
        chatbot.chat()
        
    except FileNotFoundError:
        print("❌ Error: No scraped data found!")
        print("📋 Please run scraper.py first to collect MOSDAC data:")
        print("   python scraper.py")
        
    except Exception as e:
        print(f"❌ Error initializing chatbot: {e}")
        print("🔧 Check your .env file and GEMINI_API_KEY")

if __name__ == "__main__":
    main()
