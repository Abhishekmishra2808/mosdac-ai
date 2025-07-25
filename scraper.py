# scraper.py

import asyncio
import json
import os
import time
import requests
from datetime import datetime
from urllib.parse import urljoin, urlparse
from pathlib import Path
from typing import List, Dict

from dotenv import load_dotenv
load_dotenv()  # loads GEMINI_API_KEY from .env

from crawl4ai import AsyncWebCrawler, BrowserConfig, CrawlerRunConfig, CacheMode, LLMExtractionStrategy, LLMConfig
from bs4 import BeautifulSoup

class MOSDACAdvancedScraper:
    def __init__(self):
        print("Initializing MOSDAC scraper...")
        self.base_url = "https://www.mosdac.gov.in"
        self.session = requests.Session()
        self.scraped_urls = set()
        self.scraped_data: List[Dict] = []
        self.images_data: List[Dict] = []

        # Create storage directories
        print("Creating storage directories...")
        for d in (
            "data/mosdac_content",
            "data/mosdac_images",
            "data/mosdac_structured_data",
        ):
            Path(d).mkdir(parents=True, exist_ok=True)

        # Browser configuration for dynamic content
        self.browser_config = BrowserConfig(
            headless=True,
            user_agent=(
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/120.0.0.0 Safari/537.36"
            ),
            extra_args=[
                "--disable-blink-features=AutomationControlled",
                "--no-sandbox",
                "--disable-dev-shm-usage",
                "--disable-gpu",
            ]
        )

        # LLM‐based extraction strategy (requires GEMINI_API_KEY)
        print("Setting up LLM extraction strategy...")
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            print("WARNING: GEMINI_API_KEY not found in environment variables")
        else:
            print(f"GEMINI_API_KEY found: {api_key[:10]}...")
        
        self.structured_strategy = LLMExtractionStrategy(
            llm_config=LLMConfig(
                provider="gemini/gemini-2.0-flash-exp", 
                api_token=api_key
            ),
            instruction="""
            From this MOSDAC page HTML extract:
            1. Satellite info: names, launch dates, payload specs
            2. Weather data: temperature, precipitation, forecasts
            3. Data products: types, formats, download links
            4. Instrument specs: sensors, resolutions
            Return JSON with clearly labeled fields.
            """,
            extraction_type="block",
            input_format="markdown"
        )
        print("Initialization complete!")

    def get_urls(self) -> List[str]:
        return [
            self.base_url + path for path in (
                "/", "/about-us", "/contact-us",
                "/data", "/services", "/tools", "/products",
                "/insat-3d-payloads", "/insat-3dr-payloads",
                "/oceansat-2-payloads", "/scatsat-1-payloads",
                "/searchTab", "/data-dissemination",
                "/documentation", "/user-manual", "/faq"
            )
        ]

    async def extract_page(self, crawler: AsyncWebCrawler, url: str) -> Dict:
        # configure run for dynamic content
        run_cfg = CrawlerRunConfig(
            cache_mode=CacheMode.BYPASS,
            wait_for_images=True,
            process_iframes=True,
            delay_before_return_html=2,
            js_code=[
                # allow lazy loading
                "window.scrollTo(0, document.body.scrollHeight);"
            ]
        )
        try:
            # Fetch raw content + metadata
            result = await crawler.arun(url=url, config=run_cfg)

            # LLM‐driven structured extraction
            structured_run_cfg = CrawlerRunConfig(
                cache_mode=CacheMode.BYPASS,
                extraction_strategy=self.structured_strategy,
                wait_for_images=True,
                process_iframes=True,
                delay_before_return_html=2,
                js_code=[
                    "window.scrollTo(0, document.body.scrollHeight);"
                ]
            )
            structured = await crawler.arun(url=url, config=structured_run_cfg)

            return {
                "url": url,
                "title": result.metadata.get("title", ""),
                "markdown": result.markdown,
                "html": result.html,
                "links": result.links,
                "images": result.media,
                "structured_data": structured.extracted_content,
                "timestamp": datetime.utcnow().isoformat()
            }

        except Exception as e:
            print(f"Error fetching {url}: {e}")
            return {}

    def download_images(self, images: List, page_url: str) -> List[Dict]:
        downloaded = []
        if not images:
            return downloaded
            
        for i, img in enumerate(images):
            # Handle both dict and string formats
            if isinstance(img, dict):
                src = img.get("src") or img.get("url") or img.get("link")
            elif isinstance(img, str):
                src = img
            else:
                continue
                
            if not src:
                continue
                
            # normalize URL
            if src.startswith("/"):
                img_url = urljoin(self.base_url, src)
            elif src.startswith("http"):
                img_url = src
            else:
                img_url = urljoin(page_url, src)
                
            try:
                resp = self.session.get(img_url, timeout=20)
                resp.raise_for_status()
                ext = (
                    ".jpg" if "jpeg" in resp.headers.get("content-type", "")
                    else ".png" if "png" in resp.headers.get("content-type", "")
                    else ".svg" if "svg" in resp.headers.get("content-type", "")
                    else ""
                )
                domain = urlparse(page_url).netloc.replace(".", "_")
                fn = f"{domain}_{i}_{int(time.time())}{ext}"
                path = f"data/mosdac_images/{fn}"
                with open(path, "wb") as f:
                    f.write(resp.content)
                downloaded.append({
                    "original_url": img_url,
                    "local_path": path,
                    "content_type": resp.headers.get("content-type", ""),
                })
            except Exception as e:
                print(f"Failed to download image {img_url}: {e}")
        return downloaded

    def save(self):
        ts = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        # save pages
        with open(f"data/mosdac_content/pages_{ts}.json", "w", encoding="utf-8") as f:
            json.dump(self.scraped_data, f, indent=2, ensure_ascii=False)
        # save images metadata
        with open(f"data/mosdac_images/images_{ts}.json", "w", encoding="utf-8") as f:
            json.dump(self.images_data, f, indent=2, ensure_ascii=False)

    async def run(self):
        print("Starting scraping process...")
        urls = self.get_urls()
        print(f"Found {len(urls)} URLs to scrape")
        
        async with AsyncWebCrawler(config=self.browser_config) as crawler:
            print("AsyncWebCrawler initialized")
            for url in urls:
                if url in self.scraped_urls:
                    continue
                print(f"Scraping {url}")
                page = await self.extract_page(crawler, url)
                if not page:
                    continue
                self.scraped_urls.add(url)
                # download images
                imgs = page.get("images", [])
                print(f"Found {len(imgs)} images on {url}")
                if isinstance(imgs, list) and imgs:
                    print(f"First image sample: {imgs[0]}")
                elif isinstance(imgs, dict):
                    print(f"Images dict keys: {list(imgs.keys())}")
                else:
                    print(f"Images type: {type(imgs)}, value: {imgs}")
                downloaded = self.download_images(imgs, url)
                page["downloaded_images"] = downloaded
                self.images_data.extend(downloaded)
                self.scraped_data.append(page)
                # polite delay
                await asyncio.sleep(1)
        self.save()
        print("Done. Data and images saved under data/")

if __name__ == "__main__":
    print("Starting MOSDAC Advanced Scraper...")
    try:
        scraper = MOSDACAdvancedScraper()
        print("Scraper initialized successfully")
        asyncio.run(scraper.run())
    except Exception as e:
        print(f"Error occurred: {e}")
        import traceback
        traceback.print_exc()
