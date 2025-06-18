"""
Advanced Configuration Management with Environment Variable Support
Implements singleton pattern with lazy loading and type validation
"""

import os
from pathlib import Path
from typing import Dict, Any, Optional
from dataclasses import dataclass, field
import json
import logging
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

@dataclass
class DatabaseConfig:
    """Database configuration with connection pooling parameters"""
    path: Path
    max_connections: int = 10
    timeout: float = 30.0
    enable_wal: bool = True
    cache_size: int = 10000
    
@dataclass
class ProxyConfiguration:
    """Proxy configuration settings"""
    enabled: bool = True
    config_file: Optional[Path] = None
    rotation_strategy: str = "round_robin"  # round_robin, random, best_performance
    health_check_interval: int = 300  # seconds
    retry_failed_after: int = 1800  # seconds
    max_failures_before_removal: int = 5
    concurrent_connections_per_proxy: int = 5
    
    def __post_init__(self):
        if self.config_file is None:
            self.config_file = Path(__file__).parent.parent.parent / "config" / "proxies.json"

@dataclass
class ScrapingConfig:
    """Web scraping configuration with performance tuning"""
    max_concurrent_scrapers: int = 10
    default_timeout: int = 30
    retry_attempts: int = 3
    retry_delay: float = 1.0
    user_agent: str = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    rate_limit_delay: float = 1.0
    cache_responses: bool = True
    cache_ttl: int = 3600
    use_stealth: bool = True  # Enable stealth scraping by default
    proxy: ProxyConfiguration = field(default_factory=ProxyConfiguration)

@dataclass
class NotificationConfig:
    """Notification settings for alerts and monitoring"""
    email_enabled: bool = False
    email_server: Optional[str] = None
    email_port: int = 587
    email_username: Optional[str] = None
    email_password: Optional[str] = None
    slack_enabled: bool = False
    slack_webhook: Optional[str] = None
    desktop_notifications: bool = False
    alert_on_changes: bool = True
    alert_on_errors: bool = True
    alert_on_downtime: bool = True

@dataclass
class PricingConfig:
    """Dynamic pricing configuration"""
    starter_price: float = 99.0
    starter_targets: int = 5
    professional_price: float = 199.0
    professional_targets: int = 15
    enterprise_price: float = 499.0
    enterprise_targets: int = 50
    custom_price_per_target: float = 10.0
@dataclass 
class ApplicationConfig:
    """Master configuration class with all subsystem configs"""
    project_root: Path = field(default_factory=lambda: Path(__file__).parent.parent.parent)
    database: DatabaseConfig = field(default_factory=lambda: DatabaseConfig(
        path=Path(__file__).parent.parent.parent / "scrapemaster.db"
    ))
    scraping: ScrapingConfig = field(default_factory=ScrapingConfig)
    notifications: NotificationConfig = field(default_factory=NotificationConfig) 
    pricing: PricingConfig = field(default_factory=PricingConfig)
    
    # Runtime settings
    debug_mode: bool = field(default_factory=lambda: os.getenv("DEBUG", "False").lower() == "true")
    log_level: str = field(default_factory=lambda: os.getenv("LOG_LEVEL", "INFO"))
    secret_key: str = field(default_factory=lambda: os.getenv("SECRET_KEY", "dev-secret-key"))
    
    # Feature flags
    enable_async_scraping: bool = True
    enable_cache: bool = True
    enable_metrics: bool = True
    enable_auto_retry: bool = True
    
    def __post_init__(self):
        """Validate configuration on initialization"""
        # Ensure directories exist
        self.project_root.mkdir(exist_ok=True)
        (self.project_root / "data").mkdir(exist_ok=True)
        (self.project_root / "logs").mkdir(exist_ok=True)
        (self.project_root / "temp").mkdir(exist_ok=True)
        
        # Load custom settings from JSON if exists
        config_file = self.project_root / "config" / "settings.json"
        if config_file.exists():
            self._load_custom_settings(config_file)
    
    def _load_custom_settings(self, config_file: Path):
        """Load and merge custom settings from JSON file"""
        try:
            with open(config_file, 'r') as f:
                custom_settings = json.load(f)
                
            # Update scraping config
            if 'scraping' in custom_settings:
                for key, value in custom_settings['scraping'].items():
                    if hasattr(self.scraping, key):
                        setattr(self.scraping, key, value)
                        
            # Update notification config
            if 'notifications' in custom_settings:
                for key, value in custom_settings['notifications'].items():
                    if hasattr(self.notifications, key):
                        setattr(self.notifications, key, value)
                        
            # Update pricing config
            if 'pricing' in custom_settings:
                for key, value in custom_settings['pricing'].items():
                    if hasattr(self.pricing, key):
                        setattr(self.pricing, key, value)
                        
            logging.info(f"Loaded custom settings from {config_file}")
            
        except Exception as e:
            logging.warning(f"Failed to load custom settings: {e}")
    
    def save_custom_settings(self):
        """Save current settings to JSON file"""
        config_file = self.project_root / "config" / "settings.json"
        config_file.parent.mkdir(exist_ok=True)
        
        settings = {
            'scraping': {
                'max_concurrent_scrapers': self.scraping.max_concurrent_scrapers,
                'default_timeout': self.scraping.default_timeout,
                'retry_attempts': self.scraping.retry_attempts,
                'rate_limit_delay': self.scraping.rate_limit_delay,
            },
            'notifications': {
                'email_enabled': self.notifications.email_enabled,
                'slack_enabled': self.notifications.slack_enabled,
                'desktop_notifications': self.notifications.desktop_notifications,
                'alert_on_changes': self.notifications.alert_on_changes,
                'alert_on_errors': self.notifications.alert_on_errors,
                'alert_on_downtime': self.notifications.alert_on_downtime,
            },
            'pricing': {
                'starter_price': self.pricing.starter_price,
                'professional_price': self.pricing.professional_price,
                'enterprise_price': self.pricing.enterprise_price,
            }
        }
        
        with open(config_file, 'w') as f:
            json.dump(settings, f, indent=2)
            
        logging.info(f"Saved settings to {config_file}")

# Singleton instance
_config_instance: Optional[ApplicationConfig] = None

def get_config() -> ApplicationConfig:
    """Get or create singleton configuration instance"""
    global _config_instance
    if _config_instance is None:
        _config_instance = ApplicationConfig()
    return _config_instance