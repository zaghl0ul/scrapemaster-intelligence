"""
Enhanced Data Models with Validation and Business Logic
Implements domain-driven design patterns for robust data handling
"""

from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Union, Any
from enum import Enum
import hashlib
import json
import uuid
from urllib.parse import urlparse

class PlanType(Enum):
    """Subscription plan types with feature sets"""
    STARTER = "starter"
    PROFESSIONAL = "professional"
    ENTERPRISE = "enterprise"
    CUSTOM = "custom"
    
    @property
    def max_targets(self) -> int:
        """Get maximum targets allowed for plan"""
        mapping = {
            self.STARTER: 5,
            self.PROFESSIONAL: 15,
            self.ENTERPRISE: 50,
            self.CUSTOM: 9999
        }
        return mapping.get(self, 5)
    
    @property
    def features(self) -> List[str]:
        """Get feature list for plan"""
        base_features = ["Web Monitoring", "Change Detection", "Email Alerts"]
        
        if self == self.STARTER:
            return base_features
        elif self == self.PROFESSIONAL:
            return base_features + ["API Access", "Slack Integration", "Custom Alerts"]
        elif self == self.ENTERPRISE:
            return base_features + ["API Access", "Slack Integration", "Custom Alerts", 
                                   "White Label", "Dedicated Support", "Custom Integrations"]
        return base_features + ["All Features"]

class TargetStatus(Enum):
    """Scraping target operational status"""
    ACTIVE = "active"
    PAUSED = "paused"
    ERROR = "error"
    MAINTENANCE = "maintenance"
    ARCHIVED = "archived"
@dataclass
class ScrapingTarget:
    """Enhanced scraping target with comprehensive validation and business logic"""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    name: str = ""
    url: str = ""
    selectors: Dict[str, str] = field(default_factory=dict)
    frequency_hours: int = 24
    client_id: str = ""
    price_per_month: float = 0.0
    created_at: datetime = field(default_factory=datetime.now)
    last_scraped: Optional[datetime] = None
    is_active: bool = True
    status: TargetStatus = TargetStatus.ACTIVE
    success_rate: float = 100.0
    error_count: int = 0
    consecutive_errors: int = 0
    metadata: Dict[str, Any] = field(default_factory=dict)
    headers: Dict[str, str] = field(default_factory=dict)
    cookies: Dict[str, str] = field(default_factory=dict)
    
    def __post_init__(self):
        """Validate and normalize target data"""
        # URL validation and normalization
        if not self.url:
            raise ValueError("URL is required")
        
        parsed = urlparse(self.url)
        if not parsed.scheme:
            self.url = f"https://{self.url}"
        elif parsed.scheme not in ['http', 'https']:
            raise ValueError(f"Invalid URL scheme: {parsed.scheme}")
            
        # Validate frequency
        if not 1 <= self.frequency_hours <= 168:
            raise ValueError("Frequency must be between 1 and 168 hours")
            
        # Validate price
        if self.price_per_month < 0:
            raise ValueError("Price cannot be negative")
            
        # Auto-generate ID if not provided
        if not self.id:
            self.id = str(uuid.uuid4())
            
        # Set default selectors if empty
        if not self.selectors:
            self.selectors = {
                "title": "title",
                "content": "body",
                "price": "[class*='price']",
                "availability": "[class*='stock'], [class*='availability']"
            }
    
    @property
    def is_due_for_scraping(self) -> bool:
        """Check if target is due for scraping based on frequency"""
        if not self.last_scraped:
            return True
        
        next_scrape = self.last_scraped + timedelta(hours=self.frequency_hours)
        return datetime.now() >= next_scrape
    
    @property
    def health_score(self) -> float:
        """Calculate target health score (0-100)"""
        if self.consecutive_errors >= 5:
            return 0.0
        
        error_penalty = min(self.consecutive_errors * 20, 80)
        return max(self.success_rate - error_penalty, 0)
    
    def update_stats(self, success: bool, response_time: float = 0):
        """Update target statistics after scraping attempt"""
        if success:
            self.consecutive_errors = 0
            self.success_rate = (self.success_rate * 0.95) + 5.0
            self.status = TargetStatus.ACTIVE
        else:
            self.error_count += 1
            self.consecutive_errors += 1
            self.success_rate = self.success_rate * 0.95
            
            if self.consecutive_errors >= 3:
                self.status = TargetStatus.ERROR
                
        self.last_scraped = datetime.now()
        self.metadata['last_response_time'] = response_time
@dataclass
class ScrapedData:
    """Enhanced scraped data model with comprehensive metrics"""
    id: Optional[int] = None
    target_id: str = ""
    timestamp: datetime = field(default_factory=datetime.now)
    data: Dict[str, Any] = field(default_factory=dict)
    raw_html: Optional[str] = None
    change_detected: bool = False
    changes: Dict[str, Dict[str, Any]] = field(default_factory=dict)
    hash_signature: str = ""
    response_time_ms: int = 0
    status_code: int = 200
    content_length: int = 0
    extraction_success_rate: float = 100.0
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def __post_init__(self):
        """Generate hash signature if not provided"""
        if not self.hash_signature and self.data:
            content = json.dumps(self.data, sort_keys=True)
            self.hash_signature = hashlib.sha256(content.encode()).hexdigest()
    
    def compare_with(self, previous: 'ScrapedData') -> Dict[str, Dict[str, Any]]:
        """Compare with previous scrape to detect changes"""
        changes = {}
        
        for key, current_value in self.data.items():
            if key in previous.data:
                previous_value = previous.data[key]
                if current_value != previous_value:
                    changes[key] = {
                        'previous': previous_value,
                        'current': current_value,
                        'change_type': self._detect_change_type(previous_value, current_value)
                    }
            else:
                changes[key] = {
                    'previous': None,
                    'current': current_value,
                    'change_type': 'added'
                }
        
        # Check for removed fields
        for key in previous.data:
            if key not in self.data:
                changes[key] = {
                    'previous': previous.data[key],
                    'current': None,
                    'change_type': 'removed'
                }
        
        return changes
    
    def _detect_change_type(self, previous: Any, current: Any) -> str:
        """Detect the type of change between values"""
        if isinstance(previous, (int, float)) and isinstance(current, (int, float)):
            if current > previous:
                return 'increased'
            elif current < previous:
                return 'decreased'
        return 'modified'

@dataclass
class Client:
    """Enhanced client model with comprehensive business logic"""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    name: str = ""
    email: str = ""
    company: Optional[str] = None
    phone: Optional[str] = None
    plan_type: PlanType = PlanType.STARTER
    monthly_value: float = 0.0
    created_at: datetime = field(default_factory=datetime.now)
    last_activity: Optional[datetime] = None
    is_active: bool = True
    satisfaction_score: float = 5.0
    targets_count: int = 0
    lifetime_value: float = 0.0
    notes: str = ""
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def __post_init__(self):
        """Validate client data"""
        if not self.email or '@' not in self.email:
            raise ValueError("Valid email is required")
            
        if not self.name:
            raise ValueError("Client name is required")
            
        if self.satisfaction_score < 0 or self.satisfaction_score > 5:
            raise ValueError("Satisfaction score must be between 0 and 5")
    
    @property
    def can_add_targets(self) -> bool:
        """Check if client can add more targets based on plan"""
        return self.targets_count < self.plan_type.max_targets
    
    @property
    def targets_remaining(self) -> int:
        """Get number of targets client can still add"""
        return max(0, self.plan_type.max_targets - self.targets_count)
    
    @property
    def churn_risk_score(self) -> float:
        """Calculate churn risk score (0-100, higher = more risk)"""
        score = 0.0
        
        # Satisfaction component (40%)
        score += (5.0 - self.satisfaction_score) * 8
        
        # Activity component (30%)
        if self.last_activity:
            days_inactive = (datetime.now() - self.last_activity).days
            if days_inactive > 30:
                score += min(30, days_inactive - 30)
        else:
            score += 30
            
        # Usage component (30%)
        if self.plan_type != PlanType.CUSTOM:
            usage_ratio = self.targets_count / self.plan_type.max_targets
            if usage_ratio < 0.2:
                score += 30
            elif usage_ratio < 0.5:
                score += 15
                
        return min(100, score)