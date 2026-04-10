"""
============================================================
LONG-TERM MEMORY - Persistent Knowledge Storage
============================================================
Stores user behavior, past interactions, and learned patterns
"""

import json
import os
from typing import Any, Dict, List, Optional
from datetime import datetime
from dataclasses import dataclass, asdict
import hashlib


@dataclass
class Interaction:
    id: str
    user_input: str
    response: Any
    intent_type: str
    context: List[str]
    timestamp: datetime
    success: bool
    feedback_score: float = 0.0
    tags: List[str] = None
    
    def to_dict(self) -> Dict:
        return {
            "id": self.id,
            "user_input": self.user_input,
            "response": str(self.response)[:500] if self.response else None,
            "intent_type": self.intent_type,
            "context": self.context,
            "timestamp": self.timestamp.isoformat(),
            "success": self.success,
            "feedback_score": self.feedback_score,
            "tags": self.tags or []
        }


@dataclass
class UserPattern:
    id: str
    pattern_type: str  # query_pattern, task_pattern, preference
    pattern: str
    frequency: int
    last_seen: datetime
    associated_actions: List[str]
    success_rate: float
    
    def to_dict(self) -> Dict:
        return {
            "id": self.id,
            "pattern_type": self.pattern_type,
            "pattern": self.pattern,
            "frequency": self.frequency,
            "last_seen": self.last_seen.isoformat(),
            "associated_actions": self.associated_actions,
            "success_rate": self.success_rate
        }


@dataclass
class LearnedStrategy:
    id: str
    goal_type: str
    strategy: Dict  # Steps that worked
    success_count: int
    failure_count: int
    last_used: datetime
    description: str
    
    @property
    def success_rate(self) -> float:
        total = self.success_count + self.failure_count
        return self.success_count / total if total > 0 else 0.0


class LongTermMemory:
    """
    Long-term memory for persistent storage
    - Stores user preferences
    - Remembers successful strategies
    - Learns from past interactions
    """
    
    def __init__(self, user_id: str, data_dir: str = "data/memory"):
        self.user_id = user_id
        self.data_dir = data_dir
        self.memory_file = os.path.join(data_dir, f"memory_{user_id}.json")
        
        # In-memory cache
        self.interactions: List[Interaction] = []
        self.patterns: Dict[str, UserPattern] = {}
        self.strategies: Dict[str, LearnedStrategy] = {}
        
        # Load existing memory
        self._load()
    
    def store_interaction(self, user_input: str, response: Any, 
                         intent_type: str = None, context: List[str] = None) -> None:
        """Store a user interaction"""
        
        interaction = Interaction(
            id=self._generate_id(user_input),
            user_input=user_input,
            response=response,
            intent_type=intent_type or "unknown",
            context=context or [],
            timestamp=datetime.now(),
            success=True
        )
        
        self.interactions.append(interaction)
        
        # Extract and store patterns
        self._extract_pattern(user_input, intent_type)
        
        # Save to disk
        self._save()
    
    def _extract_pattern(self, user_input: str, intent_type: str = None) -> None:
        """Extract patterns from user input"""
        
        words = user_input.lower().split()
        
        # Create bigrams
        for i in range(len(words) - 1):
            bigram = f"{words[i]} {words[i+1]}"
            pattern_key = self._hash_key(bigram)
            
            if pattern_key in self.patterns:
                pattern = self.patterns[pattern_key]
                pattern.frequency += 1
                pattern.last_seen = datetime.now()
            else:
                self.patterns[pattern_key] = UserPattern(
                    id=pattern_key,
                    pattern_type="phrase",
                    pattern=bigram,
                    frequency=1,
                    last_seen=datetime.now(),
                    associated_actions=[intent_type] if intent_type else [],
                    success_rate=0.5
                )
    
    def get_recent_interactions(self, n: int = 10) -> List[Dict]:
        """Get n most recent interactions"""
        sorted_interactions = sorted(
            self.interactions, 
            key=lambda x: x.timestamp, 
            reverse=True
        )
        return [i.to_dict() for i in sorted_interactions[:n]]
    
    def get_similar_interactions(self, query: str, n: int = 5) -> List[Dict]:
        """Find similar past interactions"""
        query_words = set(query.lower().split())
        results = []
        
        for interaction in reversed(self.interactions):
            interaction_words = set(interaction.user_input.lower().split())
            
            # Calculate similarity
            intersection = query_words & interaction_words
            if intersection:
                similarity = len(intersection) / max(len(query_words), len(interaction_words))
                results.append((similarity, interaction))
        
        # Sort by similarity and return top n
        results.sort(key=lambda x: x[0], reverse=True)
        return [r.to_dict() for _, r in results[:n]]
    
    def store_strategy(self, goal_type: str, strategy: Dict, success: bool) -> None:
        """Store a learned strategy"""
        
        strategy_key = self._hash_key(json.dumps(strategy, sort_keys=True))
        
        if strategy_key in self.strategies:
            strategy_obj = self.strategies[strategy_key]
            if success:
                strategy_obj.success_count += 1
            else:
                strategy_obj.failure_count += 1
            strategy_obj.last_used = datetime.now()
        else:
            self.strategies[strategy_key] = LearnedStrategy(
                id=strategy_key,
                goal_type=goal_type,
                strategy=strategy,
                success_count=1 if success else 0,
                failure_count=0 if success else 1,
                last_used=datetime.now(),
                description=f"Strategy for {goal_type}"
            )
    
    def get_best_strategy(self, goal_type: str) -> Optional[Dict]:
        """Get the most successful strategy for a goal type"""
        
        best_strategy = None
        best_rate = 0.0
        
        for strategy in self.strategies.values():
            if strategy.goal_type == goal_type and strategy.success_rate > best_rate:
                best_rate = strategy.success_rate
                best_strategy = strategy
        
        return best_strategy.strategy if best_strategy else None
    
    def get_user_preferences(self) -> Dict[str, Any]:
        """Extract user preferences from memory"""
        preferences = {
            "common_intents": {},
            "preferred_topics": {},
            "interaction_count": len(self.interactions)
        }
        
        # Count intent types
        for interaction in self.interactions:
            intent = interaction.intent_type
            preferences["common_intents"][intent] = \
                preferences["common_intents"].get(intent, 0) + 1
        
        # Count context topics
        for interaction in self.interactions:
            for ctx in interaction.context:
                preferences["preferred_topics"][ctx] = \
                    preferences["preferred_topics"].get(ctx, 0) + 1
        
        return preferences
    
    def search_memory(self, query: str) -> Dict[str, List]:
        """Search all memory for query"""
        query_lower = query.lower()
        results = {
            "interactions": [],
            "patterns": [],
            "strategies": []
        }
        
        # Search interactions
        for interaction in self.interactions:
            if query_lower in interaction.user_input.lower():
                results["interactions"].append(interaction.to_dict())
        
        # Search patterns
        for pattern in self.patterns.values():
            if query_lower in pattern.pattern.lower():
                results["patterns"].append(pattern.to_dict())
        
        # Search strategies
        for strategy in self.strategies.values():
            if query_lower in strategy.goal_type.lower():
                results["strategies"].append({
                    "id": strategy.id,
                    "goal_type": strategy.goal_type,
                    "success_rate": strategy.success_rate,
                    "description": strategy.description
                })
        
        return results
    
    def _load(self) -> None:
        """Load memory from disk"""
        if os.path.exists(self.memory_file):
            try:
                with open(self.memory_file, 'r') as f:
                    data = json.load(f)
                    
                    # Load interactions
                    for i_data in data.get("interactions", []):
                        i_data["timestamp"] = datetime.fromisoformat(i_data["timestamp"])
                        self.interactions.append(Interaction(**i_data))
                    
                    # Load patterns
                    for p_data in data.get("patterns", {}).values():
                        p_data["last_seen"] = datetime.fromisoformat(p_data["last_seen"])
                        self.patterns[p_data["id"]] = UserPattern(**p_data)
                    
                    # Load strategies
                    for s_data in data.get("strategies", {}).values():
                        s_data["last_used"] = datetime.fromisoformat(s_data["last_used"])
                        self.strategies[s_data["id"]] = LearnedStrategy(**s_data)
                        
            except Exception as e:
                print(f"Error loading memory: {e}")
    
    def _save(self) -> None:
        """Save memory to disk"""
        os.makedirs(self.data_dir, exist_ok=True)
        
        data = {
            "user_id": self.user_id,
            "last_updated": datetime.now().isoformat(),
            "interactions": [i.to_dict() for i in self.interactions[-100:]],  # Keep last 100
            "patterns": {k: v.to_dict() for k, v in self.patterns.items()},
            "strategies": {k: {
                "id": v.id,
                "goal_type": v.goal_type,
                "strategy": v.strategy,
                "success_count": v.success_count,
                "failure_count": v.failure_count,
                "last_used": v.last_used.isoformat(),
                "description": v.description
            } for k, v in self.strategies.items()}
        }
        
        with open(self.memory_file, 'w') as f:
            json.dump(data, f, indent=2)
    
    def _generate_id(self, text: str) -> str:
        """Generate unique ID"""
        return hashlib.md5(f"{text}{datetime.now()}".encode()).hexdigest()[:12]
    
    def _hash_key(self, text: str) -> str:
        """Create hash key for storage"""
        return hashlib.md5(text.encode()).hexdigest()[:16]
