#!/usr/bin/env python3
"""
MOSDAC Chatbot Demo - Enhanced with Gemini AI
This script demonstrates the improved chatbot with better responses.
"""

from chatbot import MOSDACChatbot
import time

def demo_chatbot():
    print("🚀 MOSDAC Chatbot Demo - Enhanced with Gemini AI 🚀")
    print("=" * 70)
    
    # Initialize chatbot
    print("Initializing chatbot...")
    chatbot = MOSDACChatbot()
    
    print(f"✅ Successfully loaded {len(chatbot.knowledge_base)} pages from MOSDAC")
    print("✅ Connected to Gemini AI")
    print("✅ Enhanced search and response generation ready")
    
    # Demo questions
    demo_questions = [
        {
            "question": "What is MOSDAC and what services does it provide?",
            "category": "General Information"
        },
        {
            "question": "What satellite missions does MOSDAC support?",
            "category": "Satellite Missions"
        },
        {
            "question": "How can I access weather forecast data from MOSDAC?",
            "category": "Data Access"
        },
        {
            "question": "Tell me about ocean data and oceanographic services available",
            "category": "Ocean Services"
        }
    ]
    
    print("\n🔍 Demo Questions:")
    for i, item in enumerate(demo_questions, 1):
        print(f"{i}. {item['question']} [{item['category']}]")
    
    print("\n" + "="*70)
    
    for i, item in enumerate(demo_questions, 1):
        question = item['question']
        category = item['category']
        
        print(f"\n📋 Demo {i}/{len(demo_questions)} - {category}")
        print(f"❓ Question: {question}")
        print("🤖 Generating response...")
        
        try:
            response = chatbot.generate_response(question)
            print(f"💬 Response:\n{response}")
        except Exception as e:
            print(f"❌ Error: {e}")
        
        print("\n" + "-"*50)
        
        if i < len(demo_questions):
            time.sleep(1)  # Brief pause between questions
    
    print("\n🎉 Demo completed! The chatbot is now ready for interactive use.")
    print("💡 To use interactively, run: python chatbot.py")
    
if __name__ == "__main__":
    demo_chatbot()
