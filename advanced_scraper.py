#!/usr/bin/env python3
"""
Advanced MOSDAC Website Scraper
- Respects robots.txt rules
- Uses sitemap for comprehensive coverage
- Extracts structured content (tables, FAQs, lists)
- Implements intelligent content filtering
- Adds crawl delay for respectful scraping
"""

import asyncio
import aiohttp
import aiofiles
from crawl4ai import AsyncWebCrawler
from bs4 import BeautifulSoup
import json
import os
import re
from datetime import datetime
from urllib.parse import urljoin, urlparse
import time
from typing import List, Dict, Set
import logging

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class AdvancedMOSDACScaper:
    def __init__(self):
        self.base_url = "https://www.mosdac.gov.in"
        self.crawl_delay = 10  # Respect robots.txt crawl delay
        self.scraped_data = []
        self.visited_urls = set()
        
        # Define allowed and disallowed patterns from robots.txt
        self.disallowed_patterns = [
            r'/admin/', r'/comment/reply/', r'/filter/tips/', r'/node/add/',
            r'/search/', r'/user/register/', r'/user/password/', r'/user/login/',
            r'/user/logout/', r'/includes/', r'/misc/', r'/modules/', r'/profiles/',
            r'/scripts/', r'/themes/', r'\?q=admin/', r'\?q=comment/reply/',
            r'\?q=filter/tips/', r'\?q=node/add/', r'\?q=search/', r'\?q=user/'
        ]
        
        # Priority URLs from sitemap
        self.sitemap_urls = [
            # Core pages
            f"{self.base_url}/",
            f"{self.base_url}/about-us",
            f"{self.base_url}/help",
            f"{self.base_url}/faq-page",
            
            # Missions
            f"{self.base_url}/insat-3dr",
            f"{self.base_url}/insat-3d",
            f"{self.base_url}/insat-3ds",
            f"{self.base_url}/kalpana-1",
            f"{self.base_url}/insat-3a",
            f"{self.base_url}/megha-tropiques",
            f"{self.base_url}/saral-altika",
            f"{self.base_url}/oceansat-2",
            f"{self.base_url}/oceansat-3",
            f"{self.base_url}/scatsat-1",
            
            # Data Catalogs
            f"{self.base_url}/internal/catalog-satellite",
            f"{self.base_url}/internal/catalog-insitu",
            f"{self.base_url}/internal/catalog-radar",
            
            # Galleries
            f"{self.base_url}/internal/gallery",
            f"{self.base_url}/internal/gallery/weather",
            f"{self.base_url}/internal/gallery/ocean",
            f"{self.base_url}/internal/gallery/dwr",
            f"{self.base_url}/internal/gallery/current",
            
            # Data Access
            f"{self.base_url}/internal/uops",
            f"{self.base_url}/internal/calval-data",
            f"{self.base_url}/internal/forecast-menu",
            
            # Atmosphere Data
            f"{self.base_url}/bayesian-based-mt-saphir-rainfall",
            f"{self.base_url}/gps-derived-integrated-water-vapour",
            f"{self.base_url}/gsmap-isro-rain",
            f"{self.base_url}/meteosat8-cloud-properties",
            
            # Land Data
            f"{self.base_url}/3d-volumetric-terls-dwrproduct",
            f"{self.base_url}/inland-water-height",
            f"{self.base_url}/river-discharge",
            f"{self.base_url}/soil-moisture-0",
            
            # Ocean Data
            f"{self.base_url}/global-ocean-surface-current",
            f"{self.base_url}/high-resolution-sea-surface-salinity",
            f"{self.base_url}/indian-mainland-coastal-product",
            f"{self.base_url}/ocean-subsurface",
            f"{self.base_url}/oceanic-eddies-detection",
            f"{self.base_url}/sea-ice-occurrence-probability",
            f"{self.base_url}/wave-based-renewable-energy",
            
            # Reports
            f"{self.base_url}/insitu",
            f"{self.base_url}/calibration-reports",
            f"{self.base_url}/validation-reports",
            f"{self.base_url}/data-quality",
            f"{self.base_url}/weather-reports",
            
            # Tools and Resources
            f"{self.base_url}/atlases",
            f"{self.base_url}/tools",
            f"{self.base_url}/rss-feed",
            
            # Policies
            f"{self.base_url}/data-access-policy",
            f"{self.base_url}/copyright-policy",
            f"{self.base_url}/privacy-policy",
            f"{self.base_url}/terms-conditions",
        ]
    
    def is_allowed_url(self, url: str) -> bool:
        """Check if URL is allowed based on robots.txt rules"""
        for pattern in self.disallowed_patterns:
            if re.search(pattern, url):
                return False
        return True
    
    def clean_text(self, text: str) -> str:
        """Clean and normalize text content"""
        if not text:
            return ""
        # Remove extra whitespace and normalize
        text = re.sub(r'\\s+', ' ', text)
        # Remove navigation artifacts
        text = re.sub(r'Skip to main content|Back to top|Follow Us|Search', '', text)
        return text.strip()
    
    def extract_structured_content(self, soup: BeautifulSoup, url: str) -> Dict:
        """Extract structured content from HTML"""
        content_data = {
            "url": url,
            "title": "",
            "description": "",
            "main_content": "",
            "headings": [],
            "tables": [],
            "lists": [],
            "faqs": [],
            "links": [],
            "metadata": {},
            "data_products": [],
            "services": []
        }
        
        # Extract title
        if soup.title:
            content_data["title"] = self.clean_text(soup.title.string)
        
        # Extract meta description
        meta_desc = soup.find("meta", attrs={"name": "description"})
        if meta_desc:
            content_data["description"] = self.clean_text(meta_desc.get("content", ""))
        
        # Find main content area
        main_content = (
            soup.find("main") or 
            soup.find("div", {"id": "content"}) or 
            soup.find("div", {"class": "content"}) or
            soup.find("article") or
            soup.body
        )
        
        if main_content:
            # Extract clean main content text
            content_data["main_content"] = self.clean_text(main_content.get_text())
            
            # Extract headings with hierarchy
            for heading in main_content.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6']):
                content_data["headings"].append({
                    "level": heading.name,
                    "text": self.clean_text(heading.get_text())
                })
            
            # Extract tables with structure
            for table in main_content.find_all("table"):
                table_data = {"headers": [], "rows": []}
                
                # Extract headers
                headers = table.find_all("th")
                if headers:
                    table_data["headers"] = [self.clean_text(th.get_text()) for th in headers]
                
                # Extract rows
                for row in table.find_all("tr"):
                    cells = row.find_all(["td", "th"])
                    if cells:
                        row_data = [self.clean_text(cell.get_text()) for cell in cells]
                        if row_data and any(cell.strip() for cell in row_data):
                            table_data["rows"].append(row_data)
                
                if table_data["rows"]:
                    content_data["tables"].append(table_data)
            
            # Extract lists
            for ul in main_content.find_all(["ul", "ol"]):
                list_items = []
                for li in ul.find_all("li"):
                    item_text = self.clean_text(li.get_text())
                    if item_text:
                        list_items.append(item_text)
                
                if list_items:
                    content_data["lists"].append({
                        "type": ul.name,
                        "items": list_items
                    })
            
            # Extract FAQ-like content
            self.extract_faq_content(main_content, content_data)
            
            # Extract data products and services
            self.extract_data_products(main_content, content_data)
            
            # Extract internal links
            for link in main_content.find_all("a", href=True):
                href = link.get("href")
                if href and self.base_url in href:
                    link_text = self.clean_text(link.get_text())
                    if link_text:
                        content_data["links"].append({
                            "url": href,
                            "text": link_text
                        })
        
        return content_data
    
    def extract_faq_content(self, soup: BeautifulSoup, content_data: Dict):
        """Extract FAQ-style Q&A content"""
        # Look for question patterns
        question_patterns = [
            r'^(Q\\d*[\\.\\):]?\\s*|Question[\\s\\d]*:?\\s*|What\\s+|How\\s+|Why\\s+|When\\s+|Where\\s+)',
            r'^\\d+\\.\\s*',
            r'^FAQ\\s*\\d*[\\.\\):]?\\s*'
        ]
        
        for heading in soup.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'p', 'div']):
            heading_text = self.clean_text(heading.get_text())
            
            # Check if this looks like a question
            for pattern in question_patterns:
                if re.search(pattern, heading_text, re.IGNORECASE):
                    # Look for the answer in the next sibling elements
                    answer_elements = []
                    next_elem = heading.find_next_sibling()
                    
                    while next_elem and next_elem.name not in ['h1', 'h2', 'h3', 'h4', 'h5', 'h6']:
                        if next_elem.name in ['p', 'div', 'ul', 'ol']:
                            answer_text = self.clean_text(next_elem.get_text())
                            if answer_text:
                                answer_elements.append(answer_text)
                        next_elem = next_elem.find_next_sibling()
                    
                    if answer_elements:
                        content_data["faqs"].append({
                            "question": heading_text,
                            "answer": " ".join(answer_elements)
                        })
                    break
    
    def extract_data_products(self, soup: BeautifulSoup, content_data: Dict):
        """Extract information about data products and services"""
        # Look for data product information
        product_keywords = [
            "satellite", "data", "product", "service", "forecast", "imagery",
            "temperature", "humidity", "rainfall", "ocean", "wind", "current"
        ]
        
        for div in soup.find_all(['div', 'section', 'article']):
            div_text = self.clean_text(div.get_text()).lower()
            
            # Check if this section contains data product information
            if any(keyword in div_text for keyword in product_keywords):
                # Extract structured information
                title_elem = div.find(['h1', 'h2', 'h3', 'h4', 'h5', 'h6'])
                if title_elem:
                    title = self.clean_text(title_elem.get_text())
                    description = self.clean_text(div.get_text())
                    
                    # Look for download links or access information
                    links = []
                    for link in div.find_all("a", href=True):
                        link_text = self.clean_text(link.get_text())
                        if any(word in link_text.lower() for word in ["download", "access", "view", "more"]):
                            links.append({
                                "url": link.get("href"),
                                "text": link_text
                            })
                    
                    if title and len(description) > 50:  # Meaningful content
                        content_data["data_products"].append({
                            "title": title,
                            "description": description[:500],  # Limit description length
                            "links": links
                        })
    
    async def scrape_url(self, session, crawler, url: str) -> Dict:
        """Scrape a single URL with error handling"""
        if url in self.visited_urls or not self.is_allowed_url(url):
            return None
        
        self.visited_urls.add(url)
        
        try:
            logger.info(f"Scraping: {url}")
            
            # Use Crawl4AI for better content extraction
            result = await crawler.arun(
                url=url,
                word_count_threshold=50,
                extraction_strategy="NoExtractionStrategy",
                bypass_cache=True
            )
            
            if result.success:
                soup = BeautifulSoup(result.html, 'html.parser')
                content_data = self.extract_structured_content(soup, url)
                
                # Add markdown content from Crawl4AI
                if result.markdown:
                    content_data["markdown"] = result.markdown[:10000]  # Limit size
                
                # Add extraction timestamp
                content_data["scraped_at"] = datetime.now().isoformat()
                
                # Respect crawl delay
                await asyncio.sleep(self.crawl_delay)
                
                return content_data
            else:
                logger.warning(f"Failed to scrape {url}: {result.error_message}")
                return None
                
        except Exception as e:
            logger.error(f"Error scraping {url}: {str(e)}")
            return None
    
    async def scrape_all_urls(self):
        """Scrape all URLs from sitemap"""
        logger.info(f"Starting to scrape {len(self.sitemap_urls)} URLs")
        
        async with AsyncWebCrawler(verbose=True) as crawler:
            async with aiohttp.ClientSession() as session:
                # Process URLs in batches to avoid overwhelming the server
                batch_size = 5
                for i in range(0, len(self.sitemap_urls), batch_size):
                    batch = self.sitemap_urls[i:i + batch_size]
                    
                    # Process batch
                    tasks = [self.scrape_url(session, crawler, url) for url in batch]
                    results = await asyncio.gather(*tasks, return_exceptions=True)
                    
                    # Collect successful results
                    for result in results:
                        if result and not isinstance(result, Exception):
                            self.scraped_data.append(result)
                            logger.info(f"Successfully scraped: {result['url']}")
                    
                    # Longer delay between batches
                    if i + batch_size < len(self.sitemap_urls):
                        logger.info(f"Completed batch {i//batch_size + 1}. Waiting before next batch...")
                        await asyncio.sleep(30)  # 30 second delay between batches
    
    async def save_data(self):
        """Save scraped data to JSON file"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Ensure data directory exists
        os.makedirs("data/mosdac_content", exist_ok=True)
        os.makedirs("data/mosdac_structured_data", exist_ok=True)
        
        # Save comprehensive data
        filename = f"data/mosdac_content/pages_{timestamp}.json"
        async with aiofiles.open(filename, 'w', encoding='utf-8') as f:
            await f.write(json.dumps(self.scraped_data, indent=2, ensure_ascii=False))
        
        # Save structured summaries for quick access
        structured_data = []
        for page in self.scraped_data:
            structured_data.append({
                "url": page["url"],
                "title": page["title"],
                "description": page["description"],
                "headings": page["headings"],
                "faqs": page["faqs"],
                "data_products": page["data_products"],
                "tables_count": len(page["tables"]),
                "lists_count": len(page["lists"])
            })
        
        structured_filename = f"data/mosdac_structured_data/summary_{timestamp}.json"
        async with aiofiles.open(structured_filename, 'w', encoding='utf-8') as f:
            await f.write(json.dumps(structured_data, indent=2, ensure_ascii=False))
        
        logger.info(f"Saved {len(self.scraped_data)} pages to {filename}")
        logger.info(f"Saved structured summary to {structured_filename}")
        
        return filename
    
    async def run(self):
        """Main execution method"""
        logger.info("🚀 Starting Advanced MOSDAC Scraper")
        logger.info(f"📋 Respecting robots.txt crawl delay: {self.crawl_delay} seconds")
        logger.info(f"🎯 Target URLs: {len(self.sitemap_urls)}")
        
        start_time = time.time()
        
        try:
            await self.scrape_all_urls()
            filename = await self.save_data()
            
            end_time = time.time()
            duration = end_time - start_time
            
            logger.info("✅ Scraping completed successfully!")
            logger.info(f"📊 Total pages scraped: {len(self.scraped_data)}")
            logger.info(f"⏱️ Total time: {duration:.2f} seconds")
            logger.info(f"💾 Data saved to: {filename}")
            
            return filename
            
        except Exception as e:
            logger.error(f"❌ Scraping failed: {str(e)}")
            raise

async def main():
    """Main function to run the scraper"""
    scraper = AdvancedMOSDACScaper()
    await scraper.run()

if __name__ == "__main__":
    asyncio.run(main())
