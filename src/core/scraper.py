"""
Advanced Web Scraper with Async Support, Caching, and Intelligent Retry Logic
Implements circuit breaker pattern, rate limiting, and content extraction
"""

import asyncio
import aiohttp
from bs4 import BeautifulSoup
import requests
from typing import Dict, Optional, List, Any, Tuple
import time
import hashlib
import json
from datetime import datetime, timedelta
from functools import lru_cache
import logging
from urllib.parse import urljoin, urlparse
import re
from contextlib import asynccontextmanager
import random
from collections import defaultdict
import pickle
from pathlib import Path

from .models import ScrapingTarget, ScrapedData
from .config import get_config

# Import stealth capabilities
try:
    from .stealth_scraper import StealthScraper, ProxyRotator
    STEALTH_AVAILABLE = True
except ImportError:
    STEALTH_AVAILABLE = False
    logging.warning("Stealth scraper not available, using basic scraping")

logger = logging.getLogger(__name__)

class RateLimiter:
    """Token bucket rate limiter for controlling request frequency"""
    
    def __init__(self, rate: float = 1.0, burst: int = 1):
        self.rate = rate  # requests per second
        self.burst = burst  # burst capacity
        self.tokens = burst
        self.last_update = time.time()
        self._lock = asyncio.Lock()
    
    async def acquire(self):
        """Acquire permission to make a request"""
        async with self._lock:
            now = time.time()
            elapsed = now - self.last_update
            self.tokens = min(self.burst, self.tokens + elapsed * self.rate)
            self.last_update = now
            
            if self.tokens < 1:
                sleep_time = (1 - self.tokens) / self.rate
                await asyncio.sleep(sleep_time)
                self.tokens = 1
                
            self.tokens -= 1
class CircuitBreaker:
    """Circuit breaker pattern to prevent cascading failures"""
    
    def __init__(self, failure_threshold: int = 5, recovery_timeout: int = 60):
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.failure_count = 0
        self.last_failure_time = None
        self.state = 'closed'  # closed, open, half-open
        
    def call_succeeded(self):
        """Reset circuit breaker on successful call"""
        self.failure_count = 0
        self.state = 'closed'
        
    def call_failed(self):
        """Record failure and potentially open circuit"""
        self.failure_count += 1
        self.last_failure_time = time.time()
        
        if self.failure_count >= self.failure_threshold:
            self.state = 'open'
            logger.warning(f"Circuit breaker opened after {self.failure_count} failures")
    
    @property
    def is_open(self) -> bool:
        """Check if circuit is open (failing)"""
        if self.state == 'closed':
            return False
            
        if self.state == 'open' and self.last_failure_time:
            if time.time() - self.last_failure_time > self.recovery_timeout:
                self.state = 'half-open'
                return False
                
        return self.state == 'open'

class ResponseCache:
    """LRU cache for HTTP responses with TTL support"""
    
    def __init__(self, max_size: int = 1000, ttl_seconds: int = 3600):
        self.max_size = max_size
        self.ttl_seconds = ttl_seconds
        self.cache = {}
        self.access_times = {}
        self.cache_dir = Path(get_config().project_root) / "temp" / "cache"
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        
    def _get_cache_key(self, url: str, headers: Dict = None) -> str:
        """Generate cache key from URL and headers"""
        key_data = {'url': url, 'headers': headers or {}}
        return hashlib.sha256(json.dumps(key_data, sort_keys=True).encode()).hexdigest()
    
    def get(self, url: str, headers: Dict = None) -> Optional[Tuple[str, int]]:
        """Get cached response if valid"""
        key = self._get_cache_key(url, headers)
        
        if key in self.cache:
            timestamp = self.access_times[key]
            if time.time() - timestamp < self.ttl_seconds:
                logger.debug(f"Cache hit for {url}")
                return self.cache[key]
            else:
                # Expired
                del self.cache[key]
                del self.access_times[key]
                
        # Check disk cache
        cache_file = self.cache_dir / f"{key}.pkl"
        if cache_file.exists():
            try:
                with open(cache_file, 'rb') as f:
                    data = pickle.load(f)
                    if time.time() - data['timestamp'] < self.ttl_seconds:
                        self.cache[key] = data['response']
                        self.access_times[key] = data['timestamp']
                        return data['response']
            except:
                cache_file.unlink()
                
        return None
    
    def set(self, url: str, response: Tuple[str, int], headers: Dict = None):
        """Cache response with TTL"""
        key = self._get_cache_key(url, headers)
        
        # Memory cache
        if len(self.cache) >= self.max_size:
            # Evict oldest
            oldest_key = min(self.access_times, key=self.access_times.get)
            del self.cache[oldest_key]
            del self.access_times[oldest_key]
            
        self.cache[key] = response
        self.access_times[key] = time.time()
        
        # Disk cache for persistence
        cache_file = self.cache_dir / f"{key}.pkl"
        with open(cache_file, 'wb') as f:
            pickle.dump({
                'timestamp': time.time(),
                'response': response,
                'url': url
            }, f)
class WebScraper:
    """Enterprise-grade web scraper with advanced extraction and resilience patterns"""
    
    def __init__(self, config=None, proxy_list=None, use_stealth=True):
        self.config = config or get_config()
        self.rate_limiter = RateLimiter(
            rate=1.0 / self.config.scraping.rate_limit_delay,
            burst=5
        )
        self.circuit_breakers = defaultdict(lambda: CircuitBreaker())
        self.cache = ResponseCache(
            ttl_seconds=self.config.scraping.cache_ttl
        ) if self.config.scraping.cache_responses else None
        
        # Initialize stealth scraper if available and requested
        self.use_stealth = use_stealth and STEALTH_AVAILABLE
        if self.use_stealth:
            self.stealth_scraper = StealthScraper(proxy_list=proxy_list)
            logger.info("Stealth scraping enabled with proxy rotation and anti-detection")
        else:
            self.stealth_scraper = None
            if use_stealth and not STEALTH_AVAILABLE:
                logger.warning("Stealth scraping requested but not available")
        
        # Session configuration with connection pooling
        self.session = None
        self.async_session = None
        self._setup_sessions()
        
    def _setup_sessions(self):
        """Configure requests session with optimal settings"""
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': self.config.scraping.user_agent,
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.9',
            'Accept-Encoding': 'gzip, deflate, br',
            'DNT': '1',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1'
        })
        
        # Configure retry strategy
        from requests.adapters import HTTPAdapter
        from urllib3.util.retry import Retry
        
        retry_strategy = Retry(
            total=self.config.scraping.retry_attempts,
            backoff_factor=self.config.scraping.retry_delay,
            status_forcelist=[429, 500, 502, 503, 504],
            allowed_methods=["HEAD", "GET", "OPTIONS"]
        )
        
        adapter = HTTPAdapter(
            max_retries=retry_strategy,
            pool_connections=10,
            pool_maxsize=20
        )
        
        self.session.mount("http://", adapter)
        self.session.mount("https://", adapter)
    
    @asynccontextmanager
    async def _get_async_session(self):
        """Get or create async session with connection pooling"""
        if not self.async_session:
            connector = aiohttp.TCPConnector(
                limit=100,
                limit_per_host=10,
                ttl_dns_cache=300
            )
            
            timeout = aiohttp.ClientTimeout(
                total=self.config.scraping.default_timeout,
                connect=5,
                sock_connect=5,
                sock_read=self.config.scraping.default_timeout
            )
            
            self.async_session = aiohttp.ClientSession(
                connector=connector,
                timeout=timeout,
                headers={
                    'User-Agent': self.config.scraping.user_agent,
                    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                    'Accept-Language': 'en-US,en;q=0.9',
                    'Accept-Encoding': 'gzip, deflate, br'
                }
            )
            
        yield self.async_session
    
    async def scrape_target_async(self, target: ScrapingTarget) -> Optional[ScrapedData]:
        """Asynchronously scrape a target with circuit breaker and caching"""
        circuit_breaker = self.circuit_breakers[target.id]
        
        if circuit_breaker.is_open:
            logger.warning(f"Circuit breaker open for {target.name}")
            return None
            
        try:
            # Rate limiting
            await self.rate_limiter.acquire()
            
            # Check cache first
            if self.cache:
                cached = self.cache.get(target.url, target.headers)
                if cached:
                    html_content, status_code = cached
                    return self._extract_data(target, html_content, 0, status_code, from_cache=True)
            
            # Use stealth scraping if available and enabled
            if self.use_stealth and self.stealth_scraper:
                logger.info(f"Using stealth scraping for {target.url}")
                try:
                    data, metadata = await self.stealth_scraper.scrape_with_strategy(
                        target.url, target.selectors
                    )
                    
                    if data:
                        circuit_breaker.call_succeeded()
                        
                        # Create ScrapedData from stealth result
                        content_hash = hashlib.sha256(
                            json.dumps(data, sort_keys=True).encode()
                        ).hexdigest()
                        
                        change_detected = self._detect_changes(target.id, content_hash)
                        
                        return ScrapedData(
                            target_id=target.id,
                            data=data,
                            change_detected=change_detected,
                            hash_signature=content_hash,
                            response_time_ms=0,  # Stealth scraper doesn't track this yet
                            status_code=200,
                            extraction_success_rate=100.0,
                            metadata={
                                'stealth_metadata': metadata,
                                'scraping_method': 'stealth'
                            }
                        )
                    else:
                        logger.warning(f"Stealth scraping failed for {target.url}, falling back to basic")
                        # Fall through to basic scraping
                        
                except Exception as e:
                    logger.error(f"Stealth scraping error: {e}, falling back to basic")
                    # Fall through to basic scraping
            
            # Basic scraping (fallback or when stealth not available)
            start_time = time.time()
            
            async with self._get_async_session() as session:
                headers = {**session.headers, **target.headers}
                
                async with session.get(
                    target.url,
                    headers=headers,
                    cookies=target.cookies,
                    allow_redirects=True,
                    ssl=False  # For development; use True in production
                ) as response:
                    response_time = int((time.time() - start_time) * 1000)
                    html_content = await response.text()
                    status_code = response.status
                    
                    if status_code == 200:
                        circuit_breaker.call_succeeded()
                        
                        # Cache successful response
                        if self.cache:
                            self.cache.set(target.url, (html_content, status_code), target.headers)
                            
                        return self._extract_data(
                            target, html_content, response_time, status_code
                        )
                    else:
                        circuit_breaker.call_failed()
                        logger.error(f"Failed to scrape {target.url}: HTTP {status_code}")
                        
                        return ScrapedData(
                            target_id=target.id,
                            status_code=status_code,
                            response_time_ms=response_time,
                            errors=[f"HTTP {status_code}"],
                            extraction_success_rate=0.0
                        )
                        
        except asyncio.TimeoutError:
            circuit_breaker.call_failed()
            logger.error(f"Timeout scraping {target.url}")
            return ScrapedData(
                target_id=target.id,
                status_code=0,
                errors=["Request timeout"],
                extraction_success_rate=0.0
            )
            
        except Exception as e:
            circuit_breaker.call_failed()
            logger.error(f"Error scraping {target.url}: {str(e)}")
            return ScrapedData(
                target_id=target.id,
                status_code=0,
                errors=[str(e)],
                extraction_success_rate=0.0
            )
    
    def scrape_target(self, target: ScrapingTarget) -> Optional[ScrapedData]:
        """Synchronous wrapper for scraping (for backward compatibility)"""
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            return loop.run_until_complete(self.scrape_target_async(target))
        finally:
            loop.close()
    def _extract_data(self, target: ScrapingTarget, html_content: str, 
                     response_time: int, status_code: int, 
                     from_cache: bool = False) -> ScrapedData:
        """Extract structured data using BeautifulSoup with intelligent parsing"""
        try:
            soup = BeautifulSoup(html_content, 'html.parser')
            extracted_data = {}
            extraction_errors = []
            warnings = []
            
            # Track extraction success for each selector
            successful_extractions = 0
            total_selectors = len(target.selectors)
            
            for field_name, selector in target.selectors.items():
                try:
                    # Enhanced selector parsing with multiple strategies
                    value = self._extract_with_strategy(soup, selector, field_name)
                    
                    if value is not None:
                        extracted_data[field_name] = value
                        successful_extractions += 1
                    else:
                        warnings.append(f"No data found for {field_name}")
                        
                except Exception as e:
                    extraction_errors.append(f"Error extracting {field_name}: {str(e)}")
                    logger.error(f"Extraction error for {field_name} with selector '{selector}': {e}")
            
            # Calculate extraction success rate
            extraction_rate = (successful_extractions / total_selectors * 100) if total_selectors > 0 else 0
            
            # Generate content hash
            content_hash = hashlib.sha256(json.dumps(extracted_data, sort_keys=True).encode()).hexdigest()
            
            # Detect changes if we have previous data
            change_detected = self._detect_changes(target.id, content_hash)
            
            return ScrapedData(
                target_id=target.id,
                data=extracted_data,
                raw_html=html_content if not from_cache else None,
                change_detected=change_detected,
                hash_signature=content_hash,
                response_time_ms=response_time,
                status_code=status_code,
                content_length=len(html_content),
                extraction_success_rate=extraction_rate,
                errors=extraction_errors,
                warnings=warnings,
                metadata={
                    'from_cache': from_cache,
                    'selector_count': total_selectors,
                    'successful_extractions': successful_extractions
                }
            )
            
        except Exception as e:
            logger.error(f"Critical extraction error: {e}")
            return ScrapedData(
                target_id=target.id,
                status_code=status_code,
                response_time_ms=response_time,
                errors=[f"Critical extraction error: {str(e)}"],
                extraction_success_rate=0.0
            )
    
    def _extract_with_strategy(self, soup: BeautifulSoup, selector: str, 
                              field_name: str) -> Optional[Any]:
        """Extract data using multiple strategies for robustness"""
        
        # Strategy 1: CSS Selector
        try:
            if selector.startswith(('.', '#', '[')) or ' ' in selector:
                elements = soup.select(selector)
                if elements:
                    # For price fields, try to extract numeric value
                    if 'price' in field_name.lower():
                        return self._extract_price(elements[0])
                    # For availability/stock, extract boolean or text
                    elif any(keyword in field_name.lower() for keyword in ['availability', 'stock', 'available']):
                        return self._extract_availability(elements[0])
                    # Default: get text content
                    else:
                        return elements[0].get_text(strip=True)
        except Exception as e:
            logger.debug(f"CSS selector failed for {selector}: {e}")
        
        # Strategy 2: Direct tag search
        try:
            element = soup.find(selector)
            if element:
                return element.get_text(strip=True)
        except:
            pass
        
        # Strategy 3: Attribute search
        try:
            if '=' in selector:
                attr_name, attr_value = selector.split('=', 1)
                attr_value = attr_value.strip('"\'')
                element = soup.find(attrs={attr_name: attr_value})
                if element:
                    return element.get_text(strip=True)
        except:
            pass
        
        # Strategy 4: Text content search
        try:
            if selector.startswith('text:'):
                search_text = selector[5:].strip()
                element = soup.find(text=re.compile(search_text, re.I))
                if element:
                    return element.parent.get_text(strip=True)
        except:
            pass
        
        # Strategy 5: XPath-like navigation
        try:
            if '>' in selector:
                parts = [p.strip() for p in selector.split('>')]
                current = soup
                for part in parts:
                    current = current.find(part)
                    if not current:
                        break
                if current:
                    return current.get_text(strip=True)
        except:
            pass
        
        return None
    
    def _extract_price(self, element) -> Optional[float]:
        """Extract numeric price from element with currency handling"""
        try:
            text = element.get_text(strip=True)
            # Remove currency symbols and normalize
            price_text = re.sub(r'[^\d.,\-]', '', text)
            price_text = price_text.replace(',', '')
            
            # Handle different decimal separators
            if '.' in price_text and price_text.count('.') == 1:
                return float(price_text)
            elif ',' in price_text and price_text.count(',') == 1:
                return float(price_text.replace(',', '.'))
            else:
                # Try to extract any number
                numbers = re.findall(r'\d+\.?\d*', price_text)
                if numbers:
                    return float(numbers[0])
        except:
            pass
        
        return None
    
    def _extract_availability(self, element) -> str:
        """Extract availability/stock status with normalization"""
        try:
            text = element.get_text(strip=True).lower()
            
            # Positive indicators
            if any(word in text for word in ['in stock', 'available', 'in-stock', 'ready']):
                return 'in_stock'
            # Negative indicators  
            elif any(word in text for word in ['out of stock', 'unavailable', 'sold out', 'out-of-stock']):
                return 'out_of_stock'
            # Limited availability
            elif any(word in text for word in ['limited', 'low stock', 'few left']):
                return 'limited'
            else:
                return text[:50]  # Return first 50 chars of original text
        except:
            return 'unknown'
    
    def _detect_changes(self, target_id: str, new_hash: str) -> bool:
        """Detect if content has changed since last scrape"""
        # This would typically check against the database
        # For now, we'll use a simple file-based approach
        hash_file = Path(self.config.project_root) / "temp" / f"{target_id}_last_hash.txt"
        
        try:
            if hash_file.exists():
                last_hash = hash_file.read_text().strip()
                if last_hash != new_hash:
                    hash_file.write_text(new_hash)
                    return True
                return False
            else:
                hash_file.parent.mkdir(parents=True, exist_ok=True)
                hash_file.write_text(new_hash)
                return False
        except:
            return False
    
    async def scrape_multiple_async(self, targets: List[ScrapingTarget], 
                                   max_concurrent: Optional[int] = None) -> List[ScrapedData]:
        """Scrape multiple targets concurrently with semaphore control"""
        max_concurrent = max_concurrent or self.config.scraping.max_concurrent_scrapers
        semaphore = asyncio.Semaphore(max_concurrent)
        
        async def scrape_with_semaphore(target):
            async with semaphore:
                return await self.scrape_target_async(target)
        
        tasks = [scrape_with_semaphore(target) for target in targets]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Filter out exceptions and None results
        valid_results = []
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                logger.error(f"Error scraping {targets[i].name}: {result}")
            elif result is not None:
                valid_results.append(result)
                
        return valid_results
    
    def cleanup(self):
        """Cleanup resources"""
        if self.session:
            self.session.close()
            
        if self.async_session:
            asyncio.create_task(self.async_session.close())