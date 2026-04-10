"""
============================================================
AI DECISION ENGINE - Intent Classification & Routing
============================================================
Classifies user input and routes to appropriate modules
"""

import re
from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass
from enum import Enum
import logging

logger = logging.getLogger("DecisionEngine")


class Intent(Enum):
    COMMAND = "command"           # Execute a command
    INSTALL = "install"          # Install something
    QUERY = "query"              # Ask a question
    CHAT = "chat"                # General conversation
    TASK = "task"                # Perform a task
    ANALYSIS = "analysis"         # Analyze something
    FILE_OP = "file_operation"   # File operations
    SYSTEM = "system"            # System operations
    SECURITY = "security"        # Security operations
    THINK = "think"              # Deep thinking
    HELP = "help"                # Get help
    UNKNOWN = "unknown"


class ActionRoute:
    """Maps intents to action handlers"""
    
    def __init__(self, intent: Intent, action: Callable, priority: int = 0):
        self.intent = intent
        self.action = action
        self.priority = priority


@dataclass
class Decision:
    intent: Intent
    confidence: float
    entities: Dict[str, Any]
    action: Optional[str] = None
    parameters: Dict[str, Any] = None
    reasoning: str = ""


class DecisionEngine:
    """
    AI Decision Engine that:
    - Classifies user input into intents
    - Extracts entities and parameters
    - Routes to appropriate action handler
    """
    
    # Intent patterns
    PATTERNS = {
        Intent.COMMAND: [
            r"^(ls|cd|cat|grep|find|ps|kill|rm|mkdir|touch|chmod|chown)\s",
            r"^run\s+", r"^execute\s+", r"^exec\s+",
            r"^terminal\s+", r"^shell\s+",
        ],
        Intent.INSTALL: [
            r"^install\s+", r"^pip install\s+", r"^npm install\s+",
            r"^apt install\s+", r"^pacman -S\s+",
            r"^download\s+", r"^get\s+", r"^setup\s+",
            r"install", r"installing",
        ],
        Intent.QUERY: [
            r"^what\s+", r"^how\s+", r"^why\s+",
            r"^when\s+", r"^where\s+", r"^who\s+",
            r"^tell me\s+", r"^explain\s+", r"^describe\s+",
        ],
        Intent.TASK: [
            r"^build\s+", r"^create\s+", r"^make\s+",
            r"^generate\s+", r"^write\s+", r"^develop\s+",
            r"^implement\s+", r"^fix\s+", r"^solve\s+",
        ],
        Intent.ANALYSIS: [
            r"^analyze\s+", r"^check\s+", r"^scan\s+",
            r"^review\s+", r"^audit\s+", r"^examine\s+",
        ],
        Intent.FILE_OP: [
            r"^open\s+", r"^read\s+", r"^write\s+",
            r"^delete\s+", r"^move\s+", r"^copy\s+",
            r"file", r"directory", r"folder",
        ],
        Intent.SYSTEM: [
            r"^system\s+", r"^process\s+", r"^memory\s+",
            r"^cpu\s+", r"^network\s+", r"^disk\s+",
            r"status", r"monitor",
        ],
        Intent.SECURITY: [
            r"^hack\s+", r"^penetrat", r"^vulnerability",
            r"^secure\s+", r"^phishing\s+", r"^scan\s+",
            r"security", r"malware", r"threat",
        ],
        Intent.THINK: [
            r"^think\s+", r"^reason\s+", r"^analyze\s+",
            r"^consider\s+", r"^wrestle\s+",
        ],
        Intent.HELP: [
            r"^help\s+", r"^commands\s+", r"^what can\s+",
            r"^how to\s+", r"^show\s+",
        ],
    }
    
    # Keywords for entity extraction
    ENTITY_PATTERNS = {
        "language": r"\b(python|javascript|java|c\+\+|rust|go|typescript|html|css)\b",
        "package": r"\b(pip|npm|apt|pacman|dnf)\b",
        "url": r"https?://[^\s]+",
        "email": r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b",
        "filepath": r"[A-Za-z]:\\[^\s]+|/[^\s]+|\.[a-z]{1,4}$",
        "number": r"\b\d+\.?\d*\b",
        "command": r"^\s*(ls|cd|cat|grep|find|ps|kill|rm|mkdir|touch|pwd|whoami|uname)\b",
    }
    
    def __init__(self):
        self.routes: Dict[Intent, List[ActionRoute]] = {}
        self.context: Dict[str, Any] = {}
        self.last_intent: Optional[Intent] = None
    
    def register_route(self, intent: Intent, action: Callable, priority: int = 0):
        """Register an action route for an intent"""
        if intent not in self.routes:
            self.routes[intent] = []
        
        self.routes[intent].append(ActionRoute(intent, action, priority))
        self.routes[intent].sort(key=lambda x: x.priority, reverse=True)
    
    def classify(self, user_input: str) -> Decision:
        """Classify user input and extract entities"""
        
        text = user_input.strip()
        text_lower = text.lower()
        
        # Score each intent
        scores = {}
        
        for intent, patterns in self.PATTERNS.items():
            score = 0
            for pattern in patterns:
                if re.search(pattern, text_lower):
                    score += 1
            
            if score > 0:
                scores[intent] = score
        
        # Determine best intent
        if scores:
            best_intent = max(scores.items(), key=lambda x: x[1])[0]
            confidence = scores[best_intent] / 10  # Normalize
        else:
            best_intent = Intent.UNKNOWN
            confidence = 0.0
        
        # Extract entities
        entities = self._extract_entities(text)
        
        # Generate action name
        action = self._generate_action(best_intent, entities, text)
        
        # Generate reasoning
        reasoning = self._generate_reasoning(best_intent, entities, text)
        
        self.last_intent = best_intent
        self.context["last_input"] = user_input
        
        logger.info(f"Classified: {best_intent.value} (confidence: {confidence:.2f})")
        
        return Decision(
            intent=best_intent,
            confidence=min(confidence, 1.0),
            entities=entities,
            action=action,
            parameters=self._extract_parameters(best_intent, text),
            reasoning=reasoning
        )
    
    def _extract_entities(self, text: str) -> Dict[str, Any]:
        """Extract entities from text"""
        
        entities = {}
        
        for entity_type, pattern in self.ENTITY_PATTERNS.items():
            matches = re.findall(pattern, text.lower() if entity_type != "url" else text)
            if matches:
                if len(matches) == 1:
                    entities[entity_type] = matches[0]
                else:
                    entities[entity_type] = matches
        
        return entities
    
    def _extract_parameters(self, intent: Intent, text: str) -> Dict[str, Any]:
        """Extract action-specific parameters"""
        
        params = {}
        
        if intent == Intent.INSTALL:
            # Extract package name
            words = text.split()
            if len(words) > 1:
                # Find the package name
                for i, word in enumerate(words):
                    if word.lower() in ["install", "pip", "npm", "apt", "pacman"]:
                        if i + 1 < len(words):
                            params["package"] = words[i + 1]
                            break
                else:
                    params["package"] = " ".join(words[1:])
        
        elif intent == Intent.COMMAND:
            params["command"] = text.strip()
        
        elif intent == Intent.QUERY:
            params["question"] = text
        
        elif intent == Intent.THINK:
            params["problem"] = text
        
        return params
    
    def _generate_action(self, intent: Intent, entities: Dict, text: str) -> str:
        """Generate action name for the decision"""
        
        action_map = {
            Intent.COMMAND: "execute_command",
            Intent.INSTALL: "install_package",
            Intent.QUERY: "answer_query",
            Intent.CHAT: "chat_response",
            Intent.TASK: "execute_task",
            Intent.ANALYSIS: "analyze",
            Intent.FILE_OP: "file_operation",
            Intent.SYSTEM: "system_operation",
            Intent.SECURITY: "security_operation",
            Intent.THINK: "deep_think",
            Intent.HELP: "show_help",
            Intent.UNKNOWN: "fallback_response",
        }
        
        return action_map.get(intent, "unknown_action")
    
    def _generate_reasoning(self, intent: Intent, entities: Dict, text: str) -> str:
        """Generate reasoning for the decision"""
        
        base = f"Detected {intent.value} intent"
        
        if entities:
            entity_str = ", ".join(f"{k}={v}" for k, v in entities.items())
            base += f" with entities: {entity_str}"
        
        return base
    
    def decide(self, user_input: str) -> Decision:
        """Main decision method - classify and prepare action"""
        
        decision = self.classify(user_input)
        
        # Store in context
        self.context["last_decision"] = decision
        
        return decision
    
    def get_routes(self) -> Dict[Intent, List[str]]:
        """Get available routes"""
        return {
            intent: [f"{r.action.__name__} (priority: {r.priority})" for r in routes]
            for intent, routes in self.routes.items()
        }
    
    def get_context(self) -> Dict[str, Any]:
        """Get current context"""
        return self.context.copy()


# Singleton
_decision_engine: Optional[DecisionEngine] = None

def get_decision_engine() -> DecisionEngine:
    global _decision_engine
    if _decision_engine is None:
        _decision_engine = DecisionEngine()
    return _decision_engine
