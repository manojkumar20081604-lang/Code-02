"""
============================================================
SHORT-TERM MEMORY - Active Context Storage
============================================================
Stores current conversation context and working memory
"""

from typing import Any, Dict, List, Optional
from dataclasses import dataclass, field
from datetime import datetime, timedelta
import json


@dataclass
class MemoryItem:
    key: str
    value: Any
    timestamp: datetime
    ttl: Optional[timedelta] = None
    access_count: int = 0
    last_accessed: datetime = None
    
    def is_expired(self) -> bool:
        if self.ttl is None:
            return False
        return datetime.now() > self.timestamp + self.ttl


class ShortTermMemory:
    """
    Short-term memory for active context
    - Stores current session data
    - Limited capacity (FIFO eviction)
    - Time-based expiration
    """
    
    def __init__(self, max_items: int = 50, default_ttl: int = 3600):
        self.max_items = max_items
        self.default_ttl = timedelta(seconds=default_ttl)
        self._storage: Dict[str, MemoryItem] = {}
        self._access_order: List[str] = []
    
    def add(self, key: str, value: Any, ttl: Optional[int] = None) -> None:
        """Add an item to short-term memory"""
        
        # Evict if at capacity
        if len(self._storage) >= self.max_items and key not in self._storage:
            self._evict_oldest()
        
        ttl_delta = timedelta(seconds=ttl) if ttl else self.default_ttl
        
        item = MemoryItem(
            key=key,
            value=value,
            timestamp=datetime.now(),
            ttl=ttl_delta,
            last_accessed=datetime.now()
        )
        
        self._storage[key] = item
        
        # Update access order
        if key in self._access_order:
            self._access_order.remove(key)
        self._access_order.append(key)
    
    def get(self, key: str, default: Any = None) -> Any:
        """Retrieve an item from memory"""
        
        if key not in self._storage:
            return default
        
        item = self._storage[key]
        
        # Check expiration
        if item.is_expired():
            self.remove(key)
            return default
        
        # Update access tracking
        item.access_count += 1
        item.last_accessed = datetime.now()
        
        # Move to end of access order (most recently used)
        self._access_order.remove(key)
        self._access_order.append(key)
        
        return item.value
    
    def remove(self, key: str) -> bool:
        """Remove an item from memory"""
        if key in self._storage:
            del self._storage[key]
            if key in self._access_order:
                self._access_order.remove(key)
            return True
        return False
    
    def clear(self) -> None:
        """Clear all short-term memory"""
        self._storage.clear()
        self._access_order.clear()
    
    def get_all(self) -> Dict[str, Any]:
        """Get all non-expired items"""
        result = {}
        expired_keys = []
        
        for key, item in self._storage.items():
            if item.is_expired():
                expired_keys.append(key)
            else:
                result[key] = item.value
        
        # Clean up expired items
        for key in expired_keys:
            self.remove(key)
        
        return result
    
    def size(self) -> int:
        """Get current size of memory"""
        return len(self._storage)
    
    def _evict_oldest(self) -> None:
        """Evict the oldest item (FIFO)"""
        if self._access_order:
            oldest_key = self._access_order[0]
            self.remove(oldest_key)
    
    def search(self, pattern: str) -> Dict[str, Any]:
        """Search memory for items matching pattern"""
        results = {}
        pattern_lower = pattern.lower()
        
        for key, item in self._storage.items():
            if item.is_expired():
                continue
            
            # Search in key
            if pattern_lower in key.lower():
                results[key] = item.value
                continue
            
            # Search in value
            value_str = str(item.value).lower()
            if pattern_lower in value_str:
                results[key] = item.value
        
        return results
    
    def get_context_window(self, n: int = 5) -> List[Any]:
        """Get the last n items (conversation window)"""
        items = []
        for key in self._access_order[-n:]:
            if key in self._storage and not self._storage[key].is_expired():
                items.append(self._storage[key].value)
        return items
    
    def to_dict(self) -> Dict:
        """Export memory as dictionary"""
        return {
            "size": self.size(),
            "max_items": self.max_items,
            "items": {
                key: {
                    "value": str(item.value)[:100],  # Truncate long values
                    "timestamp": item.timestamp.isoformat(),
                    "access_count": item.access_count
                }
                for key, item in self._storage.items()
                if not item.is_expired()
            }
        }
