import json
import google.generativeai as genai
from typing import List, Dict
import os
from dotenv import load_dotenv
import re
from collections import defaultdict

load_dotenv()

class MOSDACChatbot:
    def __init__(self):
        # Initialize Gemini client using official SDK
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise ValueError("GEMINI_API_KEY environment variable not set")
        
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel('gemini-1.5-flash')
        self.knowledge_base = self.load_scraped_data()
        
    def load_scraped_data(self) -> List[Dict]:
        """Load the latest scraped MOSDAC content from data/mosdac_content/"""
        import glob
        import os
        files = glob.glob("data/mosdac_content/pages_*.json")
        if not files:
            print("❌ No scraped data found in data/mosdac_content/. Please run the scraper first.")
            return []
        latest_file = max(files, key=os.path.getctime)
        print(f"📂 Loading scraped data from: {latest_file}")
        
        with open(latest_file, "r", encoding="utf-8") as f:
            data = json.load(f)
        
        # Display comprehensive data statistics
        print(f"✅ Loaded {len(data)} pages of data")
        
        # Check structured content availability
        has_faqs = sum(1 for page in data if page.get("faqs"))
        has_data_products = sum(1 for page in data if page.get("data_products"))
        has_tables = sum(1 for page in data if page.get("tables"))
        has_lists = sum(1 for page in data if page.get("lists"))
        
        total_faqs = sum(len(page.get("faqs", [])) for page in data)
        total_data_products = sum(len(page.get("data_products", [])) for page in data)
        total_tables = sum(len(page.get("tables", [])) for page in data)
        total_lists = sum(len(page.get("lists", [])) for page in data)
        
        print(f"📋 FAQs: {total_faqs} found across {has_faqs} pages")
        print(f"🛰️ Data products: {total_data_products} found across {has_data_products} pages")
        print(f"📊 Tables: {total_tables} found across {has_tables} pages") 
        print(f"📝 Lists: {total_lists} found across {has_lists} pages")
        print("🤖 Chatbot ready with comprehensive MOSDAC knowledge!")
        
        return data
    
    def search_relevant_content(self, query: str, top_k: int = 5) -> List[dict]:
        """Enhanced search in scraped content with better scoring"""
        relevant_content = []
        query_words = set(re.findall(r'\w+', query.lower()))
        
        for page in self.knowledge_base:
            score = 0
            content_parts = []
            
            # Get all text content from the page
            title = page.get("title", "")
            url = page.get("url", "")
            description = page.get("description", "")
            main_content = page.get("main_content", "")
            markdown = page.get("markdown", "")
            
            # Get structured content
            headings = page.get("headings", [])
            tables = page.get("tables", [])
            lists = page.get("lists", [])
            faqs = page.get("faqs", [])
            data_products = page.get("data_products", [])
            
            # Combine all text content
            headings_text = " ".join([h.get("text", "") for h in headings])
            tables_text = " ".join([
                " ".join(table.get("headers", []) + [" ".join(row) for row in table.get("rows", [])])
                for table in tables
            ])
            lists_text = " ".join([
                " ".join(lst.get("items", []))
                for lst in lists
            ])
            faqs_text = " ".join([
                f"{faq.get('question', '')} {faq.get('answer', '')}"
                for faq in faqs
            ])
            products_text = " ".join([
                f"{prod.get('title', '')} {prod.get('description', '')}"
                for prod in data_products
            ])
            
            # Use structured content if available, otherwise fall back to markdown
            if main_content or headings_text or tables_text:
                full_content = f"{title} {description} {main_content} {headings_text} {tables_text} {lists_text} {faqs_text} {products_text}".lower()
                structured_data = page.get("structured_data", "")
            else:
                # Fallback for older scraped data
                structured_data = page.get("structured_data", "")
                if isinstance(structured_data, dict):
                    structured_text = " ".join([str(v) for v in structured_data.values() if isinstance(v, str)])
                else:
                    structured_text = str(structured_data) if structured_data else ""
                full_content = f"{title} {markdown} {structured_text}".lower()
            
            # Calculate relevance score
            content_words = set(re.findall(r'\w+', full_content))
            common_words = query_words.intersection(content_words)
            
            if common_words:
                # Score based on number of matching words
                score = len(common_words) / len(query_words)
                
                # Boost score for title matches
                title_words = set(re.findall(r'\w+', title.lower()))
                if query_words.intersection(title_words):
                    score += 0.5
                
                # Boost score for FAQ matches
                if faqs and any(
                    any(word in faq.get("question", "").lower() for word in query_words)
                    for faq in faqs
                ):
                    score += 0.3
                
                # Boost score for data product matches
                if data_products and any(
                    any(word in prod.get("title", "").lower() for word in query_words)
                    for prod in data_products
                ):
                    score += 0.3
                
                # Extract relevant content for context
                if main_content:
                    content_preview = main_content[:2000]
                    full_content_for_context = f"{main_content} {headings_text} {tables_text} {lists_text}"[:5000]
                else:
                    # Fallback for older data
                    content_preview = markdown[:2000] if markdown else structured_text[:2000] if isinstance(structured_text, str) else ""
                    full_content_for_context = markdown[:5000] if markdown else structured_text[:5000] if isinstance(structured_text, str) else ""
                
                relevant_content.append({
                    "url": url,
                    "title": title,
                    "description": description,
                    "content": content_preview,
                    "score": score,
                    "full_markdown": full_content_for_context,
                    "headings": headings[:5],  # Include top headings
                    "faqs": [faq for faq in faqs if any(word in faq.get("question", "").lower() for word in query_words)][:3],
                    "data_products": [prod for prod in data_products if any(word in prod.get("title", "").lower() + prod.get("description", "").lower() for word in query_words)][:3],
                    "tables_summary": f"{len(tables)} tables available" if tables else "",
                    "lists_summary": f"{len(lists)} lists available" if lists else ""
                })
        
        # Sort by relevance score and return top results
        relevant_content.sort(key=lambda x: x["score"], reverse=True)
        return relevant_content[:top_k]
    
    def generate_response(self, user_query: str) -> str:
        """Generate chatbot response using Gemini API with enhanced context"""
        relevant_docs = self.search_relevant_content(user_query)
        
        if not relevant_docs:
            return "I couldn't find specific information about that topic in the MOSDAC website data. Please try asking about satellite data, weather forecasting, oceanographic data, or other MOSDAC services."
        
        # Prepare enhanced context from relevant documents
        context_parts = []
        for i, doc in enumerate(relevant_docs, 1):
            # Build comprehensive context
            doc_context = f"""
Document {i}:
Title: {doc['title']}
URL: {doc['url']}
Description: {doc.get('description', 'No description available')}
"""
            
            # Add headings if available
            if doc.get('headings'):
                headings_text = " | ".join([h.get('text', '') for h in doc['headings']])
                doc_context += f"Key Sections: {headings_text}\n"
            
            # Add FAQ content if relevant
            if doc.get('faqs'):
                doc_context += "Relevant FAQs:\n"
                for faq in doc['faqs']:
                    doc_context += f"Q: {faq.get('question', '')}\nA: {faq.get('answer', '')}\n"
            
            # Add data products if relevant
            if doc.get('data_products'):
                doc_context += "Available Data Products:\n"
                for prod in doc['data_products']:
                    doc_context += f"- {prod.get('title', '')}: {prod.get('description', '')}\n"
            
            # Add structured summaries
            if doc.get('tables_summary'):
                doc_context += f"Data Tables: {doc['tables_summary']}\n"
            if doc.get('lists_summary'):
                doc_context += f"Information Lists: {doc['lists_summary']}\n"
            
            # Add main content
            doc_context += f"Content: {doc['full_markdown']}\n"
            doc_context += "---\n"
            
            context_parts.append(doc_context)
        
        context = "\n".join(context_parts)
        
        # Create comprehensive prompt for Gemini
        prompt = f"""
You are MOSDAC Assistant, an expert AI helper for the Meteorological & Oceanographic Satellite Data Archival Centre (MOSDAC). MOSDAC is a data center of the Space Applications Centre (SAC) under the Indian Space Research Organisation (ISRO).

Your role is to provide detailed, accurate, and helpful information about:
- Satellite data and products from missions like INSAT-3D/3DR/3DS, OCEANSAT-2/3, KALPANA-1, SCATSAT-1
- Weather forecasting and monitoring services
- Oceanographic data and marine services
- Data access procedures, catalogs, and download methods
- Scientific applications and research capabilities
- Atmospheric, land, and ocean data products

Based on the following comprehensive website content from MOSDAC, please answer the user's question:

{context}

User Question: {user_query}

Instructions:
1. Provide a detailed, informative response based on the structured context above
2. If FAQs are relevant, incorporate them directly into your answer
3. Mention specific data products, services, or satellite missions when applicable
4. Include relevant URLs for additional information or data access
5. If tables or structured data are mentioned, reference them appropriately
6. Use technical terms accurately but explain them when necessary
7. Structure your response clearly with bullet points or sections when helpful
8. If the context doesn't fully answer the question, provide general MOSDAC knowledge while noting limitations

Please provide a comprehensive and helpful answer:
"""

        try:
            response = self.model.generate_content(prompt)
            return response.text
            
        except Exception as e:
            return f"I apologize, but I encountered an error while generating a response: {str(e)}. Please try rephrasing your question or ask about specific MOSDAC services, satellite data, or weather information."
    
    def chat(self):
        """Interactive chat interface"""
        print("=" * 70)
        print("🛰️  MOSDAC Chatbot with Gemini AI & Advanced Data  🛰️")
        print("=" * 70)
        
        # Display comprehensive data statistics
        total_faqs = sum(len(page.get("faqs", [])) for page in self.knowledge_base)
        total_data_products = sum(len(page.get("data_products", [])) for page in self.knowledge_base)
        total_tables = sum(len(page.get("tables", [])) for page in self.knowledge_base)
        total_lists = sum(len(page.get("lists", [])) for page in self.knowledge_base)
        
        print(f"📊 Data Source: {len(self.knowledge_base)} pages from MOSDAC website")
        print(f"🛰️ Knowledge Base: {total_data_products} data products, {total_tables} tables, {total_lists} lists")
        print(f"🧠 AI Engine: Gemini 1.5 Flash for intelligent responses")
        print(f"🔍 Enhanced Search: FAQs, structured data, and comprehensive content")
        print("\n💡 I can help you with:")
        print("   • Satellite missions (INSAT-3D/3DR/3DS, OCEANSAT, KALPANA-1, SCATSAT-1)")
        print("   • Weather forecasting and ocean data services")
        print("   • Data access procedures and download methods")
        print("   • Scientific applications and technical specifications")
        print("\n🚀 Ask me anything about MOSDAC! Type 'quit' to exit.\n")
        
        while True:
            try:
                user_input = input("🔍 You: ").strip()
                
                if user_input.lower() in ['quit', 'exit', 'bye', 'q']:
                    print("👋 Thank you for using MOSDAC Chatbot! Goodbye!")
                    break
                
                if not user_input:
                    print("Please ask a question about MOSDAC services.")
                    continue
                
                print("🤖 Thinking...")
                response = self.generate_response(user_input)
                print(f"🛰️ MOSDAC Assistant: {response}\n")
                
            except KeyboardInterrupt:
                print("\n👋 Thank you for using MOSDAC Chatbot! Goodbye!")
                break
            except Exception as e:
                print(f"❌ Error: {e}")

if __name__ == "__main__":
    try:
        chatbot = MOSDACChatbot()
        chatbot.chat()
    except Exception as e:
        print(f"❌ Failed to initialize chatbot: {e}")
        print("Please check your GEMINI_API_KEY and ensure you have scraped data available.")
