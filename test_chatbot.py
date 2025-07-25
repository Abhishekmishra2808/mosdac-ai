#!/usr/bin/env python3

from chatbot import MOSDACChatbot
import sys

def test_chatbot():
    print('Initializing MOSDAC Chatbot...')
    try:
        chatbot = MOSDACChatbot()
        print(f'Loaded {len(chatbot.knowledge_base)} pages from MOSDAC')
        
        # Test with a question about satellite data
        test_query = 'What satellite data does MOSDAC provide?'
        print(f'\nTesting with query: {test_query}')
        response = chatbot.generate_response(test_query)
        print(f'\nResponse:\n{response}')
        
        print("\n" + "="*50)
        
        # Test with another question
        test_query2 = 'How can I access weather forecast data?'
        print(f'\nTesting with query: {test_query2}')
        response2 = chatbot.generate_response(test_query2)
        print(f'\nResponse:\n{response2}')
        
    except Exception as e:
        print(f'Error: {e}')
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_chatbot()
