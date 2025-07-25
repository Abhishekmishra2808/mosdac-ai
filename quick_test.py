from chatbot import MOSDACChatbot

print("Testing MOSDAC Chatbot...")
chatbot = MOSDACChatbot()
print(f"Loaded {len(chatbot.knowledge_base)} pages")

question = "What satellite data does MOSDAC provide?"
print(f"\nQuestion: {question}")
response = chatbot.generate_response(question)
print(f"\nResponse:\n{response}")
