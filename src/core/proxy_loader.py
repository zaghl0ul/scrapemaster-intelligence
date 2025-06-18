"""
Proxy Loader Utility
Loads and manages proxy configurations from JSON file
"""

import json
import logging
from pathlib import Path
from typing import List, Optional
from .config import get_config

logger = logging.getLogger(__name__)

class ProxyLoader:
    """Load and manage proxy configurations"""
    
    def __init__(self, config_file: Optional[Path] = None):
        self.config = get_config()
        self.config_file = config_file or self.config.scraping.proxy.config_file
        self.proxies = []
        self._load_proxies()
    
    def _load_proxies(self):
        """Load proxies from configuration file"""
        if not self.config_file.exists():
            logger.warning(f"Proxy config file not found: {self.config_file}")
            return
            
        try:
            with open(self.config_file, 'r') as f:
                data = json.load(f)
                
            proxy_configs = data.get('proxies', [])
            
            for proxy_conf in proxy_configs:
                proxy_url = proxy_conf.get('url')
                if not proxy_url:
                    continue
                    
                # Format proxy URL with credentials if provided
                username = proxy_conf.get('username')
                password = proxy_conf.get('password')
                
                if username and password:
                    # Insert credentials into URL
                    from urllib.parse import urlparse, urlunparse
                    parsed = urlparse(proxy_url)
                    netloc_with_auth = f"{username}:{password}@{parsed.netloc}"
                    proxy_url = urlunparse((
                        parsed.scheme,
                        netloc_with_auth,
                        parsed.path,
                        parsed.params,
                        parsed.query,
                        parsed.fragment
                    ))
                
                self.proxies.append(proxy_url)
                
            logger.info(f"Loaded {len(self.proxies)} proxies from {self.config_file}")
            
        except Exception as e:
            logger.error(f"Failed to load proxies: {e}")
    
    def get_proxy_list(self) -> List[str]:
        """Get list of proxy URLs"""
        return self.proxies.copy()
    
    def add_proxy(self, proxy_url: str):
        """Add a proxy to the list"""
        if proxy_url not in self.proxies:
            self.proxies.append(proxy_url)
    
    def remove_proxy(self, proxy_url: str):
        """Remove a proxy from the list"""
        if proxy_url in self.proxies:
            self.proxies.remove(proxy_url)
    
    def save_proxies(self):
        """Save current proxy list back to config file"""
        try:
            # Load existing config
            with open(self.config_file, 'r') as f:
                data = json.load(f)
            
            # Update proxy list
            proxy_configs = []
            for proxy_url in self.proxies:
                # Parse URL to extract components
                from urllib.parse import urlparse
                parsed = urlparse(proxy_url)
                
                proxy_conf = {
                    'url': f"{parsed.scheme}://{parsed.hostname}:{parsed.port}",
                    'type': parsed.scheme,
                    'username': parsed.username,
                    'password': parsed.password,
                }
                proxy_configs.append(proxy_conf)
            
            data['proxies'] = proxy_configs
            
            # Save back to file
            with open(self.config_file, 'w') as f:
                json.dump(data, f, indent=2)
                
            logger.info(f"Saved {len(self.proxies)} proxies to {self.config_file}")
            
        except Exception as e:
            logger.error(f"Failed to save proxies: {e}")

# Singleton instance
_proxy_loader_instance: Optional[ProxyLoader] = None

def get_proxy_loader() -> ProxyLoader:
    """Get or create singleton proxy loader instance"""
    global _proxy_loader_instance
    if _proxy_loader_instance is None:
        _proxy_loader_instance = ProxyLoader()
    return _proxy_loader_instance 