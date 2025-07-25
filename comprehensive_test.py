from chatbot import MOSDACChatbot

def interactive_test():
    print("=== MOSDAC Chatbot Test ===")
    print("Loading chatbot...")
    
    chatbot = MOSDACChatbot()
    print(f"✓ Loaded {len(chatbot.knowledge_base)} pages from MOSDAC")
    
    # Test questions
    test_questions = [
        "What is MOSDAC?",
        "What satellite missions does MOSDAC support?",
        "How can I access weather forecast data?",
        "What ocean data is available?",
        "Tell me about INSAT-3D satellite",
        "How do I download satellite images?",
    ]
    
    for question in test_questions:
        print(f"\n{'='*60}")
        print(f"Question: {question}")
        print(f"{'='*60}")
        
        try:
            response = chatbot.generate_response(question)
            print(response)
        except Exception as e:
            print(f"Error: {e}")
        
        print("\n" + "-"*60)

if __name__ == "__main__":
    interactive_test()
