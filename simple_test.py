import os
print("Testing environment...")
print(f"GEMINI_API_KEY exists: {'GEMINI_API_KEY' in os.environ}")

try:
    import google.generativeai as genai
    print("✓ google.generativeai imported successfully")
except ImportError as e:
    print(f"✗ Failed to import google.generativeai: {e}")

try:
    from chatbot import MOSDACChatbot
    print("✓ MOSDACChatbot imported successfully")
    
    chatbot = MOSDACChatbot()
    print(f"✓ Chatbot initialized with {len(chatbot.knowledge_base)} pages")
    
    # Simple test
    response = chatbot.generate_response("What is MOSDAC?")
    print(f"✓ Generated response: {response[:100]}...")
    
except Exception as e:
    print(f"✗ Error: {e}")
    import traceback
    traceback.print_exc()
