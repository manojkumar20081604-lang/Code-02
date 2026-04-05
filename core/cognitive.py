"""
╔══════════════════════════════════════════════════════════════════════════════════╗
║                                                                              ║
║                     02 v1 - COGNITIVE ENGINE                                ║
║                                                                              ║
║                     "Think. Understand. Act. Learn."                         ║
║                                                                              ║
╚══════════════════════════════════════════════════════════════════════════════════╝

The Cognitive Engine is the brain of 02. It processes:
- Natural language understanding
- Intent classification
- Goal decomposition
- Context building
- Decision making
- Learning from interactions
"""

import os
import sys
import json
import time
import uuid
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Callable, Tuple
from dataclasses import dataclass, field, asdict
from enum import Enum
from collections import deque
from threading import Lock

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(name)s: %(message)s'
)
logger = logging.getLogger("02-Cognitive")

# ═══════════════════════════════════════════════════════════════════════════════════
# ENUMS & CONSTANTS
# ═══════════════════════════════════════════════════════════════════════════════════

class CognitiveState(Enum):
    IDLE = "idle"
    LISTENING = "listening"
    THINKING = "thinking"
    PLANNING = "planning"
    EXECUTING = "executing"
    RESPONDING = "responding"
    LEARNING = "learning"
    WAITING = "waiting"

class Intent(Enum):
    GREETING = "greeting"
    GOODBYE = "goodbye"
    CODE_REQUEST = "code_request"
    CODE_EXPLAIN = "code_explain"
    CODE_DEBUG = "code_debug"
    CODE_RUN = "code_run"
    MEMORY_STORE = "memory_store"
    MEMORY_RECALL = "memory_recall"
    MEMORY_FORGET = "memory_forget"
    DATA_ANALYZE = "data_analyze"
    DATA_PREDICT = "data_predict"
    AUTOMATION_START = "automation_start"
    AUTOMATION_STOP = "automation_stop"
    SYSTEM_CONTROL = "system_control"
    QUESTION = "question"
    TASK = "task"
    HELP = "help"
    UNKNOWN = "unknown"

class MemoryType(Enum):
    EPISODIC = "episodic"      # Specific experiences/events
    SEMANTIC = "semantic"       # Facts and knowledge
    PROCEDURAL = "procedural"    # Skills and how-to
    WORKING = "working"         # Current context/short-term

class Personality(Enum):
    JARVIS = "jarvis"           # British, formal, sophisticated
    FRIENDLY = "friendly"       # Warm, casual, encouraging
    HACKER = "hacker"           # Edgy, direct, technical
    FOCUSED = "focused"         # Minimal, efficient, no fluff

# ═══════════════════════════════════════════════════════════════════════════════════
# DATA CLASSES
# ═══════════════════════════════════════════════════════════════════════════════════

@dataclass
class Thought:
    """Represents a single thought or reasoning step"""
    id: str
    text: str
    confidence: float
    timestamp: datetime
    related_intents: List[Intent] = field(default_factory=list)
    entities: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict:
        return {
            "id": self.id,
            "text": self.text,
            "confidence": self.confidence,
            "timestamp": self.timestamp.isoformat(),
            "related_intents": [i.value for i in self.related_intents],
            "entities": self.entities
        }

@dataclass
class Goal:
    """Represents a user goal or objective"""
    id: str
    description: str
    priority: int = 2  # 1=critical, 5=low
    status: str = "pending"
    sub_goals: List['Goal'] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    completed_at: Optional[datetime] = None
    progress: float = 0.0
    context: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict:
        return {
            "id": self.id,
            "description": self.description,
            "priority": self.priority,
            "status": self.status,
            "progress": self.progress,
            "created_at": self.created_at.isoformat(),
            "completed_at": self.completed_at.isoformat() if self.completed_at else None
        }

@dataclass
class MemoryNode:
    """A node in the memory graph"""
    id: str
    content: str
    memory_type: MemoryType
    tags: List[str] = field(default_factory=list)
    connections: List[str] = field(default_factory=list)  # IDs of connected nodes
    importance: float = 0.5  # 0.0 to 1.0
    created_at: datetime = field(default_factory=datetime.now)
    last_accessed: datetime = field(default_factory=datetime.now)
    access_count: int = 0
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict:
        return {
            "id": self.id,
            "content": self.content[:100] + "..." if len(self.content) > 100 else self.content,
            "type": self.memory_type.value,
            "tags": self.tags,
            "importance": self.importance,
            "created_at": self.created_at.isoformat(),
            "last_accessed": self.last_accessed.isoformat(),
            "access_count": self.access_count,
            "connections_count": len(self.connections)
        }

@dataclass
class PlanStep:
    """A single step in an execution plan"""
    id: int
    action: str
    tool: str
    parameters: Dict[str, Any] = field(default_factory=dict)
    status: str = "pending"
    result: Any = None
    error: Optional[str] = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None

@dataclass
class ExecutionContext:
    """Current execution context"""
    session_id: str
    user_id: str
    current_goal: Optional[Goal] = None
    current_plan: List[PlanStep] = field(default_factory=list)
    current_step: int = 0
    recent_memories: List[str] = field(default_factory=list)
    variables: Dict[str, Any] = field(default_factory=dict)
    started_at: datetime = field(default_factory=datetime.now)

# ═══════════════════════════════════════════════════════════════════════════════════
# MEMORY GRAPH
# ═══════════════════════════════════════════════════════════════════════════════════

class MemoryGraph:
    """
    Memory Graph - Stores and retrieves information like a neural network.
    
    Features:
    - Hierarchical storage (episodic, semantic, procedural, working)
    - Connection-based retrieval
    - Importance scoring
    - Time-based decay
    - Tag-based search
    """
    
    def __init__(self, max_memories: int = 10000):
        self.max_memories = max_memories
        self.nodes: Dict[str, MemoryNode] = {}
        self.type_index: Dict[MemoryType, List[str]] = {
            mtype: [] for mtype in MemoryType
        }
        self.tag_index: Dict[str, List[str]] = {}
        self.lock = Lock()
        self.stats = {
            "total_memories": 0,
            "memories_by_type": {mt.value: 0 for mt in MemoryType},
            "avg_importance": 0.5,
            "total_connections": 0
        }
        
    def store(
        self, 
        content: str, 
        memory_type: MemoryType = MemoryType.EPISODIC,
        tags: List[str] = None,
        importance: float = 0.5,
        metadata: Dict[str, Any] = None
    ) -> MemoryNode:
        """Store a new memory"""
        with self.lock:
            node_id = str(uuid.uuid4())
            
            # Check capacity
            if len(self.nodes) >= self.max_memories:
                self._prune_old_memories()
            
            node = MemoryNode(
                id=node_id,
                content=content,
                memory_type=memory_type,
                tags=tags or [],
                importance=importance,
                metadata=metadata or {}
            )
            
            self.nodes[node_id] = node
            self.type_index[memory_type].append(node_id)
            
            # Update tag index
            for tag in node.tags:
                if tag not in self.tag_index:
                    self.tag_index[tag] = []
                self.tag_index[tag].append(node_id)
            
            # Update stats
            self._update_stats()
            
            # Create connections based on content similarity
            self._create_connections(node)
            
            logger.info(f"Stored memory: {node_id[:8]}... ({memory_type.value})")
            return node
    
    def recall(self, query: str, memory_type: MemoryType = None, limit: int = 5) -> List[MemoryNode]:
        """Recall memories matching query"""
        with self.lock:
            results = []
            query_lower = query.lower()
            
            candidates = self.type_index.get(memory_type, list(self.nodes.keys())) if memory_type else self.nodes.keys()
            
            for node_id in candidates:
                node = self.nodes.get(node_id)
                if not node:
                    continue
                    
                # Score based on relevance
                score = 0.0
                
                # Content match
                if query_lower in node.content.lower():
                    score += 0.5
                    
                # Tag match
                for tag in node.tags:
                    if query_lower in tag.lower():
                        score += 0.3
                        
                # Recency bonus
                hours_old = (datetime.now() - node.last_accessed).total_seconds() / 3600
                score += max(0, 0.2 - hours_old * 0.01)
                
                # Importance bonus
                score += node.importance * 0.2
                
                if score > 0.1:
                    results.append((node, score))
            
            # Sort by score
            results.sort(key=lambda x: x[1], reverse=True)
            
            # Update access stats
            for node, _ in results[:limit]:
                node.access_count += 1
                node.last_accessed = datetime.now()
            
            return [r[0] for r in results[:limit]]
    
    def connect(self, node_id1: str, node_id2: str) -> bool:
        """Create connection between two memory nodes"""
        with self.lock:
            if node_id1 not in self.nodes or node_id2 not in self.nodes:
                return False
                
            if node_id2 not in self.nodes[node_id1].connections:
                self.nodes[node_id1].connections.append(node_id2)
                self.nodes[node_id2].connections.append(node_id1)
                self._update_stats()
            return True
    
    def get_context(self, limit: int = 10) -> List[Dict]:
        """Get recent context for working memory"""
        with self.lock:
            working = self.type_index[MemoryType.WORKING]
            recent = []
            
            for node_id in reversed(working):
                node = self.nodes.get(node_id)
                if node:
                    recent.append(node.to_dict())
                    if len(recent) >= limit:
                        break
                        
            return recent
    
    def forget(self, node_id: str) -> bool:
        """Remove a memory"""
        with self.lock:
            if node_id not in self.nodes:
                return False
                
            node = self.nodes[node_id]
            
            # Remove from indices
            if node_id in self.type_index[node.memory_type]:
                self.type_index[node.memory_type].remove(node_id)
                
            for tag in node.tags:
                if tag in self.tag_index and node_id in self.tag_index[tag]:
                    self.tag_index[tag].remove(node_id)
            
            # Remove connections
            for connected_id in node.connections:
                if connected_id in self.nodes:
                    if node_id in self.nodes[connected_id].connections:
                        self.nodes[connected_id].connections.remove(node_id)
            
            del self.nodes[node_id]
            self._update_stats()
            return True
    
    def _create_connections(self, node: MemoryNode):
        """Create connections to similar existing memories"""
        for existing_id, existing in self.nodes.items():
            if existing_id == node.id:
                continue
                
            # Check for content similarity
            similarity = self._calculate_similarity(node.content, existing.content)
            
            if similarity > 0.3:
                node.connections.append(existing_id)
                existing.connections.append(node.id)
    
    def _calculate_similarity(self, text1: str, text2: str) -> float:
        """Calculate simple text similarity"""
        words1 = set(text1.lower().split())
        words2 = set(text2.lower().split())
        
        if not words1 or not words2:
            return 0.0
            
        intersection = words1 & words2
        union = words1 | words2
        
        return len(intersection) / len(union)
    
    def _prune_old_memories(self):
        """Remove low-importance old memories when at capacity"""
        # Get low-importance memories
        candidates = [
            (node_id, node) for node_id, node in self.nodes.items()
            if node.memory_type != MemoryType.SEMANTIC  # Never prune semantic
        ]
        
        # Sort by importance * recency
        def prune_score(node):
            hours_old = (datetime.now() - node.last_accessed).total_seconds() / 3600
            return node.importance * 0.5 + hours_old * 0.01
            
        candidates.sort(key=lambda x: prune_score(x[1]))
        
        # Remove bottom 10%
        remove_count = len(candidates) // 10
        for node_id, _ in candidates[:remove_count]:
            self.forget(node_id)
    
    def _update_stats(self):
        """Update memory statistics"""
        self.stats["total_memories"] = len(self.nodes)
        self.stats["memories_by_type"] = {
            mt.value: len(ids) for mt, ids in self.type_index.items()
        }
        
        if self.nodes:
            self.stats["avg_importance"] = sum(
                n.importance for n in self.nodes.values()
            ) / len(self.nodes)
            
        self.stats["total_connections"] = sum(
            len(n.connections) for n in self.nodes.values()
        ) // 2

# ═══════════════════════════════════════════════════════════════════════════════════
# COGNITIVE BRAIN
# ═══════════════════════════════════════════════════════════════════════════════════

class CognitiveBrain:
    """
    The Cognitive Brain - Core thinking engine.
    
    Responsibilities:
    - Intent classification
    - Entity extraction
    - Context building
    - Decision making
    - Response generation
    """
    
    def __init__(self, personality: Personality = Personality.JARVIS):
        self.personality = personality
        self.state = CognitiveState.IDLE
        self.current_thought: Optional[Thought] = None
        self.thought_history: deque = deque(maxlen=50)
        self.llm_provider = None
        self.llm_api_key = os.getenv("OPENAI_API_KEY", "")
        
        # Intent patterns
        self.intent_patterns = {
            Intent.GREETING: ["hello", "hi", "hey", "greetings", "good morning", "good evening", "good afternoon"],
            Intent.GOODBYE: ["bye", "goodbye", "see you", "later", "exit", "quit"],
            Intent.CODE_REQUEST: ["write code", "create code", "generate code", "make a function", "code for", "build"],
            Intent.CODE_EXPLAIN: ["explain", "what does", "how does", "tell me about", "describe"],
            Intent.CODE_DEBUG: ["debug", "fix", "error", "bug", "not working", "broken"],
            Intent.CODE_RUN: ["run", "execute", "start", "compile", "build"],
            Intent.MEMORY_STORE: ["remember", "store", "save", "note that", "keep in mind", "don't forget"],
            Intent.MEMORY_RECALL: ["what did i", "do you remember", "recall", "what's my", "where did i"],
            Intent.MEMORY_FORGET: ["forget", "delete memory", "remove", "erase", "clear memory"],
            Intent.DATA_ANALYZE: ["analyze", "analysis", "insights", "patterns", "trends"],
            Intent.DATA_PREDICT: ["predict", "forecast", "will", "guess", "estimate"],
            Intent.AUTOMATION_START: ["do this", "automate", "handle this", "take care of", "for me"],
            Intent.AUTOMATION_STOP: ["stop", "cancel", "halt", "abort", "never mind"],
            Intent.SYSTEM_CONTROL: ["open", "close", "launch", "shutdown", "restart", "minimize", "maximize"],
            Intent.HELP: ["help", "assist", "support", "what can you do", "commands"],
            Intent.QUESTION: ["what", "why", "how", "when", "where", "who", "which", "?"],
        }
        
        logger.info(f"Cognitive Brain initialized with {personality.value} personality")
    
    def think(self, user_input: str, context: Dict = None) -> Thought:
        """
        Process user input and generate a thought.
        
        This is the main entry point for cognitive processing.
        """
        self.state = CognitiveState.THINKING
        
        thought_id = str(uuid.uuid4())
        
        # Step 1: Classify intent
        intent = self._classify_intent(user_input)
        
        # Step 2: Extract entities
        entities = self._extract_entities(user_input, intent)
        
        # Step 3: Build reasoning
        reasoning = self._build_reasoning(user_input, intent, entities)
        
        # Step 4: Calculate confidence
        confidence = self._calculate_confidence(intent, entities)
        
        thought = Thought(
            id=thought_id,
            text=user_input,
            confidence=confidence,
            timestamp=datetime.now(),
            related_intents=[intent],
            entities=entities
        )
        
        self.current_thought = thought
        self.thought_history.append(thought)
        
        self.state = CognitiveState.IDLE
        return thought
    
    def _classify_intent(self, text: str) -> Intent:
        """Classify user intent from text"""
        text_lower = text.lower()
        
        scores = {}
        
        for intent, patterns in self.intent_patterns.items():
            score = 0
            for pattern in patterns:
                if pattern in text_lower:
                    score += 1
            scores[intent] = score
        
        # Find best match
        best_intent = max(scores.items(), key=lambda x: x[1])
        
        if best_intent[1] > 0:
            return best_intent[0]
        
        # Fallback logic
        if any(q in text_lower for q in ["?", "what", "how", "why"]):
            return Intent.QUESTION
        if any(cmd in text_lower for cmd in ["do", "make", "create", "build", "generate"]):
            return Intent.TASK
            
        return Intent.UNKNOWN
    
    def _extract_entities(self, text: str, intent: Intent) -> Dict[str, Any]:
        """Extract key entities from text"""
        entities = {}
        text_lower = text.lower()
        
        # Code language detection
        languages = ["python", "javascript", "js", "typescript", "java", "c++", "cpp", "go", "rust", "ruby", "php", "swift", "kotlin", "html", "css", "sql", "bash", "shell"]
        for lang in languages:
            if lang in text_lower:
                entities["language"] = lang
                break
        
        # File extensions
        extensions = [".py", ".js", ".ts", ".java", ".cpp", ".go", ".rs", ".rb", ".php", ".swift", ".kt", ".html", ".css", ".sql", ".sh"]
        for ext in extensions:
            if ext in text_lower:
                entities["file_extension"] = ext
                break
        
        # URLs
        import re
        urls = re.findall(r'https?://[^\s]+', text)
        if urls:
            entities["urls"] = urls
        
        # Email
        emails = re.findall(r'\S+@\S+\.\S+', text)
        if emails:
            entities["emails"] = emails
        
        # Numbers
        numbers = re.findall(r'\d+', text)
        if numbers:
            entities["numbers"] = [int(n) for n in numbers]
        
        # Commands
        if any(cmd in text_lower for cmd in ["open", "launch", "start"]):
            entities["action"] = "open"
        elif any(cmd in text_lower for cmd in ["close", "quit", "exit"]):
            entities["action"] = "close"
        
        return entities
    
    def _build_reasoning(self, text: str, intent: Intent, entities: Dict) -> str:
        """Build reasoning about the input"""
        # Simple reasoning based on intent
        reasoning_map = {
            Intent.GREETING: "User is greeting. Respond warmly.",
            Intent.GOODBYE: "User wants to end session.",
            Intent.CODE_REQUEST: f"User wants code generation. Language: {entities.get('language', 'auto')}",
            Intent.CODE_EXPLAIN: "User wants code explanation.",
            Intent.CODE_DEBUG: "User needs debugging help.",
            Intent.MEMORY_STORE: "User wants to store information.",
            Intent.MEMORY_RECALL: "User wants to recall stored information.",
            Intent.AUTOMATION_START: "User wants autonomous task execution.",
            Intent.HELP: "User needs help understanding capabilities.",
            Intent.QUESTION: "User has a question requiring response.",
            Intent.UNKNOWN: "Intent unclear, need more context."
        }
        
        return reasoning_map.get(intent, "Processing request...")
    
    def _calculate_confidence(self, intent: Intent, entities: Dict) -> float:
        """Calculate confidence score for the classification"""
        base_confidence = 0.7
        
        # Higher confidence with more entities
        if entities:
            base_confidence += 0.1
            
        # Specific intents are more confident
        if intent in [Intent.GREETING, Intent.GOODBYE, Intent.HELP]:
            base_confidence = 0.95
            
        # Unknown intent is less confident
        if intent == Intent.UNKNOWN:
            base_confidence = 0.4
            
        return min(base_confidence, 1.0)
    
    def respond(self, thought: Thought, memory: MemoryGraph = None) -> str:
        """Generate response based on thought"""
        self.state = CognitiveState.RESPONDING
        
        response = ""
        
        # Generate personality-aware response
        if self.personality == Personality.JARVIS:
            response = self._jarvis_response(thought)
        elif self.personality == Personality.FRIENDLY:
            response = self._friendly_response(thought)
        elif self.personality == Personality.HACKER:
            response = self._hacker_response(thought)
        else:
            response = self._focused_response(thought)
        
        self.state = CognitiveState.IDLE
        return response
    
    def _jarvis_response(self, thought: Thought) -> str:
        """JARVIS-style response (British, formal)"""
        responses = {
            Intent.GREETING: "Good day. How may I assist you today?",
            Intent.GOODBYE: "Until next time, sir.",
            Intent.HELP: "I am 02, at your service. I can help with coding, data analysis, automation, and much more.",
            Intent.UNKNOWN: "I understand. Please provide more details.",
        }
        return responses.get(thought.related_intents[0], "Certainly.")
    
    def _friendly_response(self, thought: Thought) -> str:
        """Friendly response style"""
        responses = {
            Intent.GREETING: "Hey there! What can I help you with?",
            Intent.GOODBYE: "Take care! See you soon!",
            Intent.HELP: "Hey! I'm here to help! I can do coding, analysis, automation, and more.",
            Intent.UNKNOWN: "Hmm, let me think about that...",
        }
        return responses.get(thought.related_intents[0], "Got it!")
    
    def _hacker_response(self, thought: Thought) -> str:
        """Hacker-style response"""
        responses = {
            Intent.GREETING: "Sup. What do you need?",
            Intent.GOODBYE: "Later.",
            Intent.HELP: "02 active. Code, data, automation, all systems ready.",
            Intent.UNKNOWN: "Need more data. Try again.",
        }
        return responses.get(thought.related_intents[0], "Processing.")
    
    def _focused_response(self, thought: Thought) -> str:
        """Minimal, focused response"""
        responses = {
            Intent.GREETING: "Hello.",
            Intent.GOODBYE: "Bye.",
            Intent.HELP: "Commands: code, analyze, automate, remember, recall.",
            Intent.UNKNOWN: "Clarify request.",
        }
        return responses.get(thought.related_intents[0], ".")

# ═══════════════════════════════════════════════════════════════════════════════════
# GOAL ENGINE
# ═══════════════════════════════════════════════════════════════════════════════════

class GoalEngine:
    """
    Goal Engine - Breaks down goals into actionable steps.
    
    Features:
    - Goal decomposition
    - Step planning
    - Progress tracking
    - Adaptive planning
    """
    
    def __init__(self):
        self.goals: Dict[str, Goal] = {}
        self.current_goal: Optional[Goal] = None
        self.plans: Dict[str, List[PlanStep]] = {}
        
    def create_goal(self, description: str, priority: int = 2) -> Goal:
        """Create a new goal"""
        goal_id = str(uuid.uuid4())
        goal = Goal(id=goal_id, description=description, priority=priority)
        self.goals[goal_id] = goal
        self.current_goal = goal
        return goal
    
    def decompose_goal(self, goal: Goal, thought: Thought = None) -> List[PlanStep]:
        """Break goal into executable steps"""
        steps = []
        step_id = 0
        
        description_lower = goal.description.lower()
        
        # Code generation task
        if "code" in description_lower or "write" in description_lower:
            steps.extend([
                PlanStep(id=step_id, action="Understand requirements", tool="cognitive", 
                        parameters={"thought": goal.description}),
                PlanStep(id=step_id+1, action="Generate code", tool="llm",
                        parameters={"task": "generate_code", "language": thought.entities.get("language") if thought else None}),
                PlanStep(id=step_id+2, action="Review code", tool="cognitive"),
                PlanStep(id=step_id+3, action="Return result", tool="response"),
            ])
            step_id += 4
        
        # Analysis task
        elif "analyze" in description_lower or "analysis" in description_lower:
            steps.extend([
                PlanStep(id=step_id, action="Gather data", tool="data"),
                PlanStep(id=step_id+1, action="Process data", tool="data"),
                PlanStep(id=step_id+2, action="Generate insights", tool="llm"),
                PlanStep(id=step_id+3, action="Present results", tool="response"),
            ])
            step_id += 4
        
        # Automation task
        elif "do" in description_lower or "automate" in description_lower:
            steps.extend([
                PlanStep(id=step_id, action="Understand task", tool="cognitive"),
                PlanStep(id=step_id+1, action="Break into subtasks", tool="cognitive"),
                PlanStep(id=step_id+2, action="Execute subtasks", tool="automation"),
                PlanStep(id=step_id+3, action="Verify results", tool="cognitive"),
                PlanStep(id=step_id+4, action="Report completion", tool="response"),
            ])
            step_id += 5
        
        # Memory task
        elif "remember" in description_lower:
            steps.extend([
                PlanStep(id=step_id, action="Extract information", tool="cognitive"),
                PlanStep(id=step_id+1, action="Store in memory", tool="memory"),
            ])
            step_id += 2
        
        # Default task
        else:
            steps.extend([
                PlanStep(id=step_id, action="Process request", tool="cognitive"),
                PlanStep(id=step_id+1, action="Generate response", tool="llm"),
            ])
        
        self.plans[goal.id] = steps
        goal.sub_goals = []
        
        return steps
    
    def update_progress(self, goal_id: str, progress: float) -> bool:
        """Update goal progress"""
        if goal_id not in self.goals:
            return False
            
        goal = self.goals[goal_id]
        goal.progress = min(max(progress, 0.0), 1.0)
        goal.updated_at = datetime.now()
        
        if goal.progress >= 1.0:
            goal.status = "completed"
            goal.completed_at = datetime.now()
            
        return True
    
    def complete_step(self, goal_id: str, step_id: int, result: Any = None) -> bool:
        """Mark a step as completed"""
        if goal_id not in self.plans:
            return False
            
        steps = self.plans[goal_id]
        for step in steps:
            if step.id == step_id:
                step.status = "completed"
                step.result = result
                step.completed_at = datetime.now()
                break
        
        # Update goal progress
        completed = sum(1 for s in steps if s.status == "completed")
        progress = completed / len(steps)
        self.update_progress(goal_id, progress)
        
        return True
    
    def get_active_goals(self) -> List[Goal]:
        """Get all active goals"""
        return [
            goal for goal in self.goals.values()
            if goal.status not in ["completed", "cancelled"]
        ]

# ═══════════════════════════════════════════════════════════════════════════════════
# CONTEXT MANAGER
# ═══════════════════════════════════════════════════════════════════════════════════

class ContextManager:
    """
    Context Manager - Maintains conversation and execution context.
    
    Features:
    - Session tracking
    - Variable storage
    - History management
    - Context switching
    """
    
    def __init__(self):
        self.sessions: Dict[str, ExecutionContext] = {}
        self.current_session_id: Optional[str] = None
        
    def start_session(self, user_id: str = "default") -> ExecutionContext:
        """Start a new session"""
        session_id = str(uuid.uuid4())
        context = ExecutionContext(session_id=session_id, user_id=user_id)
        self.sessions[session_id] = context
        self.current_session_id = session_id
        return context
    
    def get_current_session(self) -> Optional[ExecutionContext]:
        """Get current session context"""
        if self.current_session_id:
            return self.sessions.get(self.current_session_id)
        return None
    
    def set_variable(self, key: str, value: Any):
        """Set session variable"""
        session = self.get_current_session()
        if session:
            session.variables[key] = value
    
    def get_variable(self, key: str) -> Any:
        """Get session variable"""
        session = self.get_current_session()
        if session:
            return session.variables.get(key)
        return None
    
    def add_memory_to_context(self, memory_id: str):
        """Add memory to recent context"""
        session = self.get_current_session()
        if session:
            session.recent_memories.append(memory_id)
            if len(session.recent_memories) > 20:
                session.recent_memories.pop(0)
    
    def clear_session(self, session_id: str = None):
        """Clear a session"""
        sid = session_id or self.current_session_id
        if sid and sid in self.sessions:
            del self.sessions[sid]
            if self.current_session_id == sid:
                self.current_session_id = None

# ═══════════════════════════════════════════════════════════════════════════════════
# COGNITIVE SYSTEM (MAIN ORCHESTRATOR)
# ═══════════════════════════════════════════════════════════════════════════════════

class CognitiveSystem:
    """
    Cognitive System - Main orchestrator that combines all cognitive components.
    
    This is the main entry point for 02's cognitive capabilities.
    """
    
    def __init__(
        self, 
        personality: Personality = Personality.JARVIS,
        user_id: str = "default"
    ):
        # Initialize components
        self.brain = CognitiveBrain(personality)
        self.memory = MemoryGraph()
        self.goals = GoalEngine()
        self.context = ContextManager()
        
        # Start session
        self.context.start_session(user_id)
        
        # Statistics
        self.stats = {
            "requests_processed": 0,
            "memories_stored": 0,
            "goals_created": 0,
            "avg_response_time": 0.0
        }
        
        # Personality responses
        self.personality_responses = {
            Personality.JARVIS: {
                Intent.GREETING: "Good day, sir. I am 02, at your service.",
                Intent.GOODBYE: "Until next time, sir.",
                Intent.HELP: "I can assist with coding, data analysis, automation, and general inquiries.",
            },
            Personality.FRIENDLY: {
                Intent.GREETING: "Hey! Great to see you! How can I help today?",
                Intent.GOODBYE: "Bye for now! Take care!",
                Intent.HELP: "I'm here to help! Ask me anything about coding, data, or automation!",
            },
            Personality.HACKER: {
                Intent.GREETING: "System online. What's the objective?",
                Intent.GOODBYE: "Connection terminated.",
                Intent.HELP: "02 operational. Core functions: code, data, auto, memory.",
            },
            Personality.FOCUSED: {
                Intent.GREETING: "Ready.",
                Intent.GOODBYE: "Offline.",
                Intent.HELP: "Code. Data. Auto. Memory.",
            },
        }
        
        logger.info("Cognitive System initialized")
    
    def process(self, user_input: str) -> Dict:
        """
        Main processing pipeline.
        
        Pipeline:
        1. Think (classify intent, extract entities)
        2. Remember (recall relevant memories)
        3. Plan (decompose goal if needed)
        4. Execute (delegate to appropriate module)
        5. Learn (store result in memory)
        6. Respond (generate output)
        """
        start_time = time.time()
        self.stats["requests_processed"] += 1
        
        # Step 1: Think
        thought = self.brain.think(user_input)
        intent = thought.related_intents[0] if thought.related_intents else Intent.UNKNOWN
        
        # Step 2: Remember (context from memories)
        relevant_memories = self.memory.recall(user_input, limit=3)
        context_text = "\n".join([m.content for m in relevant_memories]) if relevant_memories else ""
        
        # Step 3: Handle based on intent
        response = ""
        actions = []
        data = None
        
        if intent == Intent.GREETING:
            response = self.personality_responses[self.brain.personality].get(
                Intent.GREETING, "Hello."
            )
            
        elif intent == Intent.GOODBYE:
            response = self.personality_responses[self.brain.personality].get(
                Intent.GOODBYE, "Goodbye."
            )
            
        elif intent == Intent.MEMORY_STORE:
            response = self._handle_memory_store(user_input)
            
        elif intent == Intent.MEMORY_RECALL:
            response = self._handle_memory_recall(user_input)
            
        elif intent == Intent.MEMORY_FORGET:
            response = self._handle_memory_forget(user_input)
            
        elif intent == Intent.CODE_REQUEST:
            response, data = self._handle_code_request(user_input, thought)
            
        elif intent == Intent.HELP:
            response = self.personality_responses[self.brain.personality].get(
                Intent.HELP, "I can help you."
            )
            
        else:
            response = self._handle_general_query(user_input, thought, context_text)
        
        # Step 5: Learn (store interaction)
        self.memory.store(
            content=f"User: {user_input}\n02: {response}",
            memory_type=MemoryType.EPISODIC,
            tags=[intent.value],
            metadata={"intent": intent.value}
        )
        self.stats["memories_stored"] += 1
        
        # Update stats
        elapsed = time.time() - start_time
        self.stats["avg_response_time"] = (
            (self.stats["avg_response_time"] * (self.stats["requests_processed"] - 1) + elapsed)
            / self.stats["requests_processed"]
        )
        
        return {
            "response": response,
            "intent": intent.value,
            "confidence": thought.confidence,
            "actions": actions,
            "data": data,
            "context": {
                "relevant_memories": [m.to_dict() for m in relevant_memories[:3]],
                "session_id": self.context.current_session_id
            },
            "stats": {
                "response_time": elapsed,
                "memories_available": len(self.memory.nodes)
            }
        }
    
    def _handle_memory_store(self, text: str) -> str:
        """Handle memory storage request"""
        # Extract what to remember
        text_lower = text.lower()
        
        # Remove common prefixes
        for prefix in ["remember", "store", "save", "note that", "keep in mind"]:
            if prefix in text_lower:
                text = text_lower.replace(prefix, "").strip()
                break
        
        if len(text) > 5:
            self.memory.store(
                content=text,
                memory_type=MemoryType.SEMANTIC,
                tags=["user_data"]
            )
            return f"Memorized: {text[:50]}{'...' if len(text) > 50 else ''}"
        
        return "What would you like me to remember?"
    
    def _handle_memory_recall(self, text: str) -> str:
        """Handle memory recall request"""
        text_lower = text.lower()
        
        # Remove question words
        for word in ["what did i", "do you remember", "recall", "what's my", "where did i"]:
            if word in text_lower:
                text = text_lower.replace(word, "").strip()
                break
        
        memories = self.memory.recall(text, limit=5)
        
        if memories:
            results = [f"• {m.content}" for m in memories[:3]]
            return f"I recall:\n" + "\n".join(results)
        
        return "I don't have any memories matching that."
    
    def _handle_memory_forget(self, text: str) -> str:
        """Handle memory deletion"""
        # Find and remove recent memories
        recent = self.memory.type_index[MemoryType.EPISODIC][-1:]
        for node_id in recent:
            self.memory.forget(node_id)
        return "Cleared recent memory."
    
    def _handle_code_request(self, text: str, thought: Thought) -> Tuple[str, Any]:
        """Handle code generation request"""
        lang = thought.entities.get("language", "python")
        
        response = f"Understood. I'll generate {lang} code for you."
        data = {
            "language": lang,
            "task": "code_generation",
            "prompt": text
        }
        
        return response, data
    
    def _handle_general_query(self, text: str, thought: Thought, context: str) -> str:
        """Handle general queries"""
        responses = {
            Intent.QUESTION: "That's an interesting question. Let me think...",
            Intent.TASK: "I understand. I'll work on that.",
            Intent.SYSTEM_CONTROL: "Executing system command.",
            Intent.DATA_ANALYZE: "I'll analyze that for you.",
            Intent.DATA_PREDICT: "Let me make a prediction based on the data.",
            Intent.AUTOMATION_START: "Initiating automated task execution.",
            Intent.AUTOMATION_STOP: "Stopping current operation.",
            Intent.UNKNOWN: self.personality_responses[self.brain.personality].get(
                Intent.UNKNOWN, "I'll do my best to help."
            ),
        }
        
        return responses.get(thought.related_intents[0], "Processing your request.")
    
    def get_status(self) -> Dict:
        """Get system status"""
        return {
            "state": self.brain.state.value,
            "personality": self.brain.personality.value,
            "stats": self.stats,
            "memory": self.memory.stats,
            "active_goals": len(self.goals.get_active_goals()),
            "session_id": self.context.current_session_id
        }
    
    def set_personality(self, personality: Personality):
        """Change personality"""
        self.brain.personality = personality
        logger.info(f"Personality changed to {personality.value}")

# ═══════════════════════════════════════════════════════════════════════════════════
# FACTORY & EXPORTS
# ═══════════════════════════════════════════════════════════════════════════════════

def create_cognitive_system(
    personality: str = "jarvis",
    user_id: str = "default"
) -> CognitiveSystem:
    """Factory function to create a cognitive system"""
    personality_map = {
        "jarvis": Personality.JARVIS,
        "friendly": Personality.FRIENDLY,
        "hacker": Personality.HACKER,
        "focused": Personality.FOCUSED,
    }
    
    p = personality_map.get(personality.lower(), Personality.JARVIS)
    return CognitiveSystem(personality=p, user_id=user_id)

# Export classes
__all__ = [
    'CognitiveSystem',
    'CognitiveBrain', 
    'MemoryGraph',
    'GoalEngine',
    'ContextManager',
    'Intent',
    'MemoryType',
    'Personality',
    'Thought',
    'Goal',
    'MemoryNode',
    'PlanStep',
    'ExecutionContext',
    'create_cognitive_system'
]
