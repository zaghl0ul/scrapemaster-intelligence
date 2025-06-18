"""
Stealth Scraper Module - Advanced Anti-Detection & Proxy Rotation
Implements multiple layers of protection against bot detection
"""

import random
import asyncio
import time
import json
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime, timedelta
import aiohttp
from aiohttp import ClientSession, TCPConnector
from aiohttp_proxy import ProxyConnector
import ssl
from fake_useragent import UserAgent
from playwright.async_api import async_playwright, Browser
import cloudscraper
from bs4 import BeautifulSoup
import httpx
from urllib.parse import urlparse
import logging

logger = logging.getLogger(__name__)

@dataclass
class ProxyConfig:
    """Proxy configuration with health tracking"""
    url: str
    type: str  # 'http', 'socks5', 'residential'
    username: Optional[str] = None
    password: Optional[str] = None
    last_used: Optional[datetime] = None
    success_count: int = 0
    fail_count: int = 0
    response_times: List[float] = None
    blocked: bool = False
    
    def __post_init__(self):
        if self.response_times is None:
            self.response_times = []
    
    @property
    def success_rate(self) -> float:
        total = self.success_count + self.fail_count
        return (self.success_count / total * 100) if total > 0 else 0
    
    @property
    def avg_response_time(self) -> float:
        return sum(self.response_times) / len(self.response_times) if self.response_times else 0
    
    def get_proxy_url(self) -> str:
        """Get formatted proxy URL with credentials"""
        if self.username and self.password:
            parsed = urlparse(self.url)
            return f"{parsed.scheme}://{self.username}:{self.password}@{parsed.netloc}"
        return self.url


class BrowserProfileManager:
    """Manages browser fingerprints to avoid detection"""
    
    def __init__(self):
        self.profiles = self._generate_profiles()
        
    def _generate_profiles(self) -> List[Dict]:
        """Generate diverse browser profiles"""
        profiles = []
        
        # Common screen resolutions
        resolutions = [
            (1920, 1080), (1366, 768), (1440, 900), (1536, 864),
            (1680, 1050), (1280, 720), (1280, 800), (2560, 1440)
        ]
        
        # Common browser languages
        languages = [
            ['en-US', 'en'], ['en-GB', 'en'], ['fr-FR', 'fr'],
            ['de-DE', 'de'], ['es-ES', 'es'], ['it-IT', 'it'],
            ['pt-BR', 'pt'], ['ja-JP', 'ja'], ['ko-KR', 'ko']
        ]
        
        # Common timezones
        timezones = [
            'America/New_York', 'America/Chicago', 'America/Los_Angeles',
            'Europe/London', 'Europe/Paris', 'Europe/Berlin',
            'Asia/Tokyo', 'Asia/Shanghai', 'Australia/Sydney'
        ]
        
        # Generate 50 diverse profiles
        for i in range(50):
            profile = {
                'viewport': random.choice(resolutions),
                'language': random.choice(languages),
                'timezone': random.choice(timezones),
                'webgl_vendor': random.choice(['Intel Inc.', 'NVIDIA Corporation', 'AMD']),
                'webgl_renderer': self._get_random_gpu(),
                'hardware_concurrency': random.choice([2, 4, 6, 8, 12, 16]),
                'device_memory': random.choice([2, 4, 8, 16, 32]),
                'color_depth': random.choice([24, 32]),
                'platform': self._get_random_platform(),
                'plugins': self._get_random_plugins(),
                'canvas_noise': random.random()  # Add noise to canvas fingerprint
            }
            profiles.append(profile)
            
        return profiles
    
    def _get_random_gpu(self) -> str:
        gpus = [
            'ANGLE (Intel HD Graphics 620 Direct3D11 vs_5_0 ps_5_0)',
            'ANGLE (NVIDIA GeForce GTX 1050 Ti Direct3D11 vs_5_0 ps_5_0)',
            'ANGLE (AMD Radeon RX 580 Series Direct3D11 vs_5_0 ps_5_0)',
            'Intel Iris OpenGL Engine',
            'AMD Radeon Pro 5500M OpenGL Engine',
            'NVIDIA GeForce RTX 2060 OpenGL Engine'
        ]
        return random.choice(gpus)
    
    def _get_random_platform(self) -> str:
        platforms = ['Win32', 'MacIntel', 'Linux x86_64', 'Linux armv81']
        return random.choice(platforms)
    
    def _get_random_plugins(self) -> List[str]:
        all_plugins = [
            'Chrome PDF Plugin', 'Chrome PDF Viewer', 'Native Client',
            'Shockwave Flash', 'Widevine Content Decryption Module'
        ]
        num_plugins = random.randint(0, len(all_plugins))
        return random.sample(all_plugins, num_plugins)
    
    def get_random_profile(self) -> Dict:
        """Get a random browser profile"""
        return random.choice(self.profiles)


class ProxyRotator:
    """Advanced proxy rotation with health monitoring"""
    
    def __init__(self, proxy_list: List[str] = None):
        self.proxies: List[ProxyConfig] = []
        self._load_proxies(proxy_list)
        self.current_index = 0
        self.retry_after = timedelta(minutes=30)  # Retry blocked proxies after 30 min
        
    def _load_proxies(self, proxy_list: List[str]):
        """Load and validate proxy list"""
        if not proxy_list:
            # Default free proxies (for testing - replace with premium proxies)
            proxy_list = [
                "http://proxy1.example.com:8080",
                "socks5://proxy2.example.com:1080",
            ]
            
        for proxy_url in proxy_list:
            # Parse proxy URL to extract credentials if present
            parsed = urlparse(proxy_url)
            username = parsed.username
            password = parsed.password
            
            # Reconstruct URL without credentials
            if username:
                clean_url = f"{parsed.scheme}://{parsed.hostname}:{parsed.port}"
            else:
                clean_url = proxy_url
                
            proxy = ProxyConfig(
                url=clean_url,
                type=parsed.scheme,
                username=username,
                password=password
            )
            self.proxies.append(proxy)
    
    def get_proxy(self) -> Optional[ProxyConfig]:
        """Get next available proxy using round-robin with health check"""
        if not self.proxies:
            return None
            
        attempts = 0
        while attempts < len(self.proxies):
            proxy = self.proxies[self.current_index]
            self.current_index = (self.current_index + 1) % len(self.proxies)
            
            # Skip blocked proxies unless retry time has passed
            if proxy.blocked:
                if proxy.last_used and datetime.now() - proxy.last_used > self.retry_after:
                    proxy.blocked = False  # Give it another chance
                else:
                    attempts += 1
                    continue
                    
            proxy.last_used = datetime.now()
            return proxy
            
        logger.warning("All proxies are blocked!")
        return None
    
    def mark_success(self, proxy: ProxyConfig, response_time: float):
        """Mark proxy request as successful"""
        proxy.success_count += 1
        proxy.response_times.append(response_time)
        if len(proxy.response_times) > 100:  # Keep last 100 response times
            proxy.response_times.pop(0)
    
    def mark_failure(self, proxy: ProxyConfig, block: bool = False):
        """Mark proxy request as failed"""
        proxy.fail_count += 1
        if block or proxy.fail_count > 5:
            proxy.blocked = True
            logger.warning(f"Proxy {proxy.url} blocked due to failures")
    
    def get_best_proxy(self) -> Optional[ProxyConfig]:
        """Get proxy with best performance"""
        available_proxies = [p for p in self.proxies if not p.blocked]
        if not available_proxies:
            return None
            
        # Sort by success rate and response time
        return sorted(
            available_proxies,
            key=lambda p: (p.success_rate, -p.avg_response_time),
            reverse=True
        )[0]


class StealthScraper:
    """Main stealth scraper with multiple anti-detection techniques"""
    
    def __init__(self, proxy_list: List[str] = None):
        self.ua = UserAgent()
        self.proxy_rotator = ProxyRotator(proxy_list)
        self.profile_manager = BrowserProfileManager()
        self.cloudscraper_session = cloudscraper.create_scraper()
        self.browser: Optional[Browser] = None
        self.request_delays = self._generate_human_delays()
        
    def _generate_human_delays(self) -> List[float]:
        """Generate human-like delays between requests"""
        delays = []
        for _ in range(100):
            # Normal distribution around 2 seconds with variance
            base_delay = random.gauss(2.0, 0.5)
            # Ensure minimum delay
            delay = max(0.5, base_delay)
            # Add occasional longer pauses (human behavior)
            if random.random() < 0.1:  # 10% chance of longer pause
                delay += random.uniform(3, 10)
            delays.append(delay)
        return delays
    
    def _get_random_delay(self) -> float:
        """Get random human-like delay"""
        return random.choice(self.request_delays)
    
    def _get_stealth_headers(self, url: str) -> Dict[str, str]:
        """Generate stealth headers that mimic real browser"""
        domain = urlparse(url).netloc
        
        headers = {
            'User-Agent': self.ua.random,
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.9',
            'Accept-Encoding': 'gzip, deflate, br',
            'DNT': '1',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'none',
            'Sec-Fetch-User': '?1',
            'Cache-Control': 'max-age=0',
            'Referer': f'https://www.google.com/search?q={domain}',
            'Origin': f'https://{domain}',
        }
        
        # Randomize header order (real browsers don't always send in same order)
        headers_list = list(headers.items())
        random.shuffle(headers_list)
        
        return dict(headers_list)
    
    async def scrape_with_strategy(self, url: str, selectors: Dict[str, str]) -> Tuple[Optional[Dict], Dict]:
        """
        Try multiple scraping strategies in order of sophistication
        Returns: (extracted_data, metadata)
        """
        strategies = [
            self._scrape_basic_request,
            self._scrape_with_cloudscraper,
            self._scrape_with_httpx,
            self._scrape_with_playwright,
            self._scrape_with_selenium_grid,
        ]
        
        metadata = {
            'attempts': 0,
            'successful_strategy': None,
            'proxy_used': None,
            'errors': []
        }
        
        for strategy in strategies:
            metadata['attempts'] += 1
            try:
                # Add human-like delay between attempts
                if metadata['attempts'] > 1:
                    await asyncio.sleep(self._get_random_delay())
                
                logger.info(f"Attempting {strategy.__name__} for {url}")
                result = await strategy(url, selectors)
                
                if result:
                    metadata['successful_strategy'] = strategy.__name__
                    return result, metadata
                    
            except Exception as e:
                logger.error(f"{strategy.__name__} failed: {str(e)}")
                metadata['errors'].append({
                    'strategy': strategy.__name__,
                    'error': str(e)
                })
                continue
        
        return None, metadata
    
    async def _scrape_basic_request(self, url: str, selectors: Dict[str, str]) -> Optional[Dict]:
        """Basic request with proxy and stealth headers"""
        proxy = self.proxy_rotator.get_proxy()
        
        if not proxy:
            # Fallback to no proxy
            proxy_url = None
        else:
            proxy_url = proxy.get_proxy_url()
        
        start_time = time.time()
        
        try:
            # Create custom SSL context that accepts more certificates
            ssl_context = ssl.create_default_context()
            ssl_context.check_hostname = False
            ssl_context.verify_mode = ssl.CERT_NONE
            
            # Create connector with proxy
            if proxy_url:
                connector = ProxyConnector.from_url(proxy_url, ssl=ssl_context)
            else:
                connector = TCPConnector(ssl=ssl_context)
            
            timeout = aiohttp.ClientTimeout(total=30)
            
            async with ClientSession(
                connector=connector,
                timeout=timeout,
                headers=self._get_stealth_headers(url)
            ) as session:
                async with session.get(url) as response:
                    if response.status == 200:
                        html = await response.text()
                        data = self._extract_data(html, selectors)
                        
                        # Mark proxy success
                        if proxy:
                            response_time = time.time() - start_time
                            self.proxy_rotator.mark_success(proxy, response_time)
                            
                        return data
                    else:
                        if proxy:
                            self.proxy_rotator.mark_failure(proxy, response.status == 403)
                        return None
                        
        except Exception as e:
            if proxy:
                self.proxy_rotator.mark_failure(proxy)
            raise e
    
    async def _scrape_with_cloudscraper(self, url: str, selectors: Dict[str, str]) -> Optional[Dict]:
        """Use cloudscraper for Cloudflare bypass"""
        try:
            # Cloudscraper is synchronous, so run in executor
            loop = asyncio.get_event_loop()
            response = await loop.run_in_executor(
                None,
                self.cloudscraper_session.get,
                url
            )
            
            if response.status_code == 200:
                return self._extract_data(response.text, selectors)
                
        except Exception as e:
            logger.error(f"Cloudscraper failed: {e}")
            
        return None
    
    async def _scrape_with_httpx(self, url: str, selectors: Dict[str, str]) -> Optional[Dict]:
        """Use httpx with HTTP/2 support"""
        proxy = self.proxy_rotator.get_proxy()
        
        proxies = None
        if proxy:
            proxies = {
                "http://": proxy.get_proxy_url(),
                "https://": proxy.get_proxy_url()
            }
        
        # HTTPX proxy support is different - use mounts
        transport = None
        if proxy:
            transport = httpx.AsyncHTTPTransport(proxy=proxy.get_proxy_url())
        
        async with httpx.AsyncClient(
            transport=transport,
            headers=self._get_stealth_headers(url),
            http2=True,
            follow_redirects=True,
            timeout=30.0
        ) as client:
            try:
                response = await client.get(url)
                if response.status_code == 200:
                    return self._extract_data(response.text, selectors)
            except Exception as e:
                logger.error(f"HTTPX failed: {e}")
                
        return None
    
    async def _scrape_with_playwright(self, url: str, selectors: Dict[str, str]) -> Optional[Dict]:
        """Use Playwright for JavaScript-heavy sites"""
        proxy = self.proxy_rotator.get_proxy()
        profile = self.profile_manager.get_random_profile()
        
        async with async_playwright() as p:
            # Launch browser with stealth settings
            browser_args = [
                '--disable-blink-features=AutomationControlled',
                '--disable-dev-shm-usage',
                '--no-sandbox',
                '--disable-web-security',
                f'--window-size={profile["viewport"][0]},{profile["viewport"][1]}'
            ]
            
            # Configure proxy
            proxy_config = None
            if proxy:
                proxy_config = {
                    "server": proxy.url,
                }
                if proxy.username:
                    proxy_config["username"] = proxy.username
                    proxy_config["password"] = proxy.password
            
            browser = await p.chromium.launch(
                headless=True,
                args=browser_args,
                proxy=proxy_config
            )
            
            context = await browser.new_context(
                viewport={'width': profile["viewport"][0], 'height': profile["viewport"][1]},
                user_agent=self.ua.random,
                locale=profile["language"][0],
                timezone_id=profile["timezone"],
                color_scheme='light',
                device_scale_factor=1,
                is_mobile=False,
                has_touch=False,
                java_script_enabled=True,
            )
            
            # Add stealth scripts
            await context.add_init_script("""
                // Override navigator properties
                Object.defineProperty(navigator, 'webdriver', {
                    get: () => undefined
                });
                
                // Override chrome property
                window.chrome = {
                    runtime: {},
                };
                
                // Override permissions
                const originalQuery = window.navigator.permissions.query;
                window.navigator.permissions.query = (parameters) => (
                    parameters.name === 'notifications' ?
                        Promise.resolve({ state: Notification.permission }) :
                        originalQuery(parameters)
                );
                
                // Add plugins
                Object.defineProperty(navigator, 'plugins', {
                    get: () => {
                        return """ + json.dumps(profile["plugins"]) + """;
                    },
                });
                
                // Override hardware concurrency
                Object.defineProperty(navigator, 'hardwareConcurrency', {
                    get: () => """ + str(profile["hardware_concurrency"]) + """
                });
                
                // Override device memory
                Object.defineProperty(navigator, 'deviceMemory', {
                    get: () => """ + str(profile["device_memory"]) + """
                });
                
                // Add WebGL noise
                const getParameter = WebGLRenderingContext.prototype.getParameter;
                WebGLRenderingContext.prototype.getParameter = function(parameter) {
                    if (parameter === 37445) {
                        return '""" + profile["webgl_vendor"] + """';
                    }
                    if (parameter === 37446) {
                        return '""" + profile["webgl_renderer"] + """';
                    }
                    return getParameter.apply(this, arguments);
                };
            """)
            
            page = await context.new_page()
            
            # Random mouse movements to appear human
            async def random_mouse_movement():
                for _ in range(random.randint(2, 5)):
                    x = random.randint(100, 800)
                    y = random.randint(100, 600)
                    await page.mouse.move(x, y)
                    await asyncio.sleep(random.uniform(0.1, 0.3))
            
            try:
                # Navigate with random mouse movements
                await page.goto(url, wait_until='networkidle')
                await random_mouse_movement()
                
                # Random scroll to appear human
                await page.evaluate("""
                    window.scrollTo({
                        top: Math.random() * document.body.scrollHeight,
                        behavior: 'smooth'
                    });
                """)
                
                await asyncio.sleep(random.uniform(1, 3))
                
                # Extract data
                html = await page.content()
                data = self._extract_data(html, selectors)
                
                return data
                
            finally:
                await browser.close()
    
    async def _scrape_with_selenium_grid(self, url: str, selectors: Dict[str, str]) -> Optional[Dict]:
        """Fallback to Selenium Grid for distributed scraping"""
        # This would connect to a Selenium Grid instance
        # Implementation depends on your infrastructure
        logger.info("Selenium Grid strategy not implemented in this version")
        return None
    
    def _extract_data(self, html: str, selectors: Dict[str, str]) -> Dict[str, any]:
        """Extract data using CSS selectors"""
        soup = BeautifulSoup(html, 'html.parser')
        data = {}
        
        for key, selector in selectors.items():
            try:
                # Try multiple selector strategies
                if selector.startswith('//'):  # XPath
                    # Convert to CSS selector or use lxml
                    logger.warning(f"XPath selectors not fully supported: {selector}")
                    continue
                    
                elements = soup.select(selector)
                if elements:
                    # Get text from all matching elements
                    if len(elements) == 1:
                        data[key] = elements[0].get_text(strip=True)
                    else:
                        data[key] = [el.get_text(strip=True) for el in elements]
                else:
                    # Try attribute extraction
                    if '::' in selector:
                        sel, attr = selector.split('::', 1)
                        elements = soup.select(sel)
                        if elements:
                            if len(elements) == 1:
                                data[key] = elements[0].get(attr, '')
                            else:
                                data[key] = [el.get(attr, '') for el in elements]
                                
            except Exception as e:
                logger.error(f"Failed to extract {key} with selector {selector}: {e}")
                
        return data


# Circuit breaker for resilience
class CircuitBreaker:
    """Circuit breaker pattern to prevent hammering failed endpoints"""
    
    def __init__(self, failure_threshold: int = 5, recovery_timeout: int = 60):
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.failure_count = 0
        self.last_failure_time = None
        self.state = 'closed'  # closed, open, half-open
        
    def call(self, func, *args, **kwargs):
        """Execute function with circuit breaker protection"""
        if self.state == 'open':
            if time.time() - self.last_failure_time > self.recovery_timeout:
                self.state = 'half-open'
            else:
                raise Exception("Circuit breaker is open")
                
        try:
            result = func(*args, **kwargs)
            if self.state == 'half-open':
                self.state = 'closed'
                self.failure_count = 0
            return result
            
        except Exception as e:
            self.failure_count += 1
            self.last_failure_time = time.time()
            
            if self.failure_count >= self.failure_threshold:
                self.state = 'open'
                
            raise e


# Export main class
__all__ = ['StealthScraper', 'ProxyRotator', 'CircuitBreaker'] 