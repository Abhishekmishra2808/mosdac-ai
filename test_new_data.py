#!/usr/bin/env python3

from chatbot import MOSDACChatbot
import json

def test_new_data():
    """Test the chatbot with the new scraped data"""
    print("🚀 Testing MOSDAC Chatbot with New Advanced Scraped Data")
    print("=" * 60)
    
    # Initialize chatbot
    bot = MOSDACChatbot()
    print(f"✅ Loaded {len(bot.knowledge_base)} pages of data")
    
    # Check if new structured data is present
    has_faqs = any(page.get("faqs") for page in bot.knowledge_base)
    has_data_products = any(page.get("data_products") for page in bot.knowledge_base)
    has_tables = any(page.get("tables") for page in bot.knowledge_base)
    has_lists = any(page.get("lists") for page in bot.knowledge_base)
    
    print(f"📋 FAQs found: {'✅' if has_faqs else '❌'}")
    print(f"🛰️ Data products found: {'✅' if has_data_products else '❌'}")
    print(f"📊 Tables found: {'✅' if has_tables else '❌'}")
    print(f"📝 Lists found: {'✅' if has_lists else '❌'}")
    
    # Test search functionality
    print("\n🔍 Testing search functionality...")
    test_queries = [
        "INSAT satellite data",
        "weather forecast",
        "FAQ",
        "data products"
    ]
    
    for query in test_queries:
        results = bot.search_relevant_content(query, top_k=2)
        print(f"Query: '{query}' -> {len(results)} results found")
        if results:
            print(f"  Top result: {results[0]['title'][:50]}...")
    
    print("\n🎯 Data structure sample:")
    if bot.knowledge_base:
        sample_page = bot.knowledge_base[0]
        print(f"  Title: {sample_page.get('title', 'N/A')}")
        print(f"  FAQs: {len(sample_page.get('faqs', []))}")
        print(f"  Data Products: {len(sample_page.get('data_products', []))}")
        print(f"  Tables: {len(sample_page.get('tables', []))}")
        print(f"  Lists: {len(sample_page.get('lists', []))}")
    
    print("\n✅ Chatbot is ready to use with the new advanced scraped data!")
    print("Run 'python chatbot.py' to start the interactive chatbot.")

if __name__ == "__main__":
    test_new_data()
