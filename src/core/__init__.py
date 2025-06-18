"""
ScrapeMaster Intelligence Core Package
Enterprise-grade web scraping and monitoring platform
"""

from .config import get_config, ApplicationConfig
from .models import (
    ScrapingTarget, ScrapedData, Client, 
    PlanType, TargetStatus
)
from .database import DatabaseManager
from .scraper import WebScraper

__version__ = "2.0.0"
__author__ = "ScrapeMaster Intelligence Team"

__all__ = [
    "get_config",
    "ApplicationConfig", 
    "ScrapingTarget",
    "ScrapedData",
    "Client",
    "PlanType",
    "TargetStatus",
    "DatabaseManager",
    "WebScraper"
]

# Initialize core components on import
import logging

# Configure logging format
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(funcName)s:%(lineno)d - %(message)s'
)