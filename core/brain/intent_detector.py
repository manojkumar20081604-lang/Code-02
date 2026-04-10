"""
============================================================
INTENT DETECTOR - Understanding User Goals
============================================================
Analyzes user input to understand intent, entities, and context
"""

import re
from typing import Dict, Any, List
from dataclasses import dataclass


@dataclass
class Intent:
    type: str  # task, query, command, chat, analysis
    confidence: float
    entities: Dict[str, Any]
    context: List[str]
    priority: str  # high, medium, low
    requires_planning: bool


class IntentDetector:
    """
    Detects user intent from natural language input
    """
    
    def __init__(self):
        self.patterns = {
            "task": [
                r"build\s+", r"create\s+", r"make\s+", r"develop\s+",
                r"write\s+", r"generate\s+", r"implement\s+",
                r"fix\s+", r"debug\s+", r"solve\s+",
                r"automate\s+", r"set\s+up\s+"
            ],
            "query": [
                r"what\s+(is|are)", r"how\s+(do|does|to)", 
                r"why\s+", r"when\s+", r"where\s+",
                r"explain\s+", r"tell\s+me\s+about",
                r"what's\s+the\s+(best|meaning)"
            ],
            "command": [
                r"run\s+", r"execute\s+", r"start\s+",
                r"stop\s+", r"delete\s+", r"remove\s+",
                r"open\s+", r"close\s+", r"do\s+",
                r"send\s+", r"make\s+it\s+"
            ],
            "analysis": [
                r"analyze\s+", r"check\s+", r"scan\s+",
                r"test\s+", r"review\s+", r"audit\s+",
                r"compare\s+", r"evaluate\s+", r"assess\s+"
            ],
            "security": [
                r"hack\s+", r"penetrat", r"vulnerability",
                r"exploit\s+", r"secure\s+", r"protect\s+",
                r"phishing\s+", r"malware\s+", r"threat"
            ]
        }
        
        self.context_keywords = {
            "coding": ["python", "javascript", "code", "function", "class", "api", "web"],
            "data": ["data", "dataset", "csv", "analysis", "chart", "graph", "statistics"],
            "security": ["security", "hack", "password", "encrypt", "firewall", "virus"],
            "system": ["file", "folder", "terminal", "command", "system", "process"],
            "learning": ["learn", "study", "course", "tutorial", "explain"]
        }
    
    async def analyze(self, text: str) -> Dict[str, Any]:
        """Analyze user input and detect intent"""
        text_lower = text.lower()
        
        # Detect primary intent type
        intent_type = self._detect_type(text_lower)
        
        # Extract entities
        entities = self._extract_entities(text, text_lower)
        
        # Build context
        context = self._build_context(text_lower)
        
        # Calculate confidence
        confidence = self._calculate_confidence(text_lower, intent_type)
        
        # Determine if planning is required
        requires_planning = intent_type in ["task", "analysis"]
        
        # Determine priority
        priority = self._determine_priority(intent_type, entities)
        
        intent = Intent(
            type=intent_type,
            confidence=confidence,
            entities=entities,
            context=context,
            priority=priority,
            requires_planning=requires_planning
        )
        
        return {
            "type": intent.type,
            "confidence": intent.confidence,
            "entities": intent.entities,
            "context": intent.context,
            "priority": intent.priority,
            "requires_planning": intent.requires_planning,
            "raw_input": text
        }
    
    def _detect_type(self, text: str) -> str:
        """Detect the primary intent type"""
        scores = {}
        
        for intent_type, patterns in self.patterns.items():
            score = 0
            for pattern in patterns:
                if re.search(pattern, text):
                    score += 1
            scores[intent_type] = score
        
        # Default to chat if no pattern matches
        max_score = max(scores.values()) if scores else 0
        if max_score == 0:
            return "chat"
        
        # Return the type with highest score
        for intent_type, score in scores.items():
            if score == max_score:
                return intent_type
        
        return "chat"
    
    def _extract_entities(self, text: str, text_lower: str) -> Dict[str, Any]:
        """Extract key entities from input"""
        entities = {}
        
        # Programming languages
        languages = ["python", "javascript", "java", "c++", "rust", "go", "typescript", "html", "css"]
        for lang in languages:
            if lang in text_lower:
                entities["language"] = lang
        
        # URLs
        urls = re.findall(r'https?://[^\s]+', text)
        if urls:
            entities["urls"] = urls
        
        # Email addresses
        emails = re.findall(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', text)
        if emails:
            entities["emails"] = emails
        
        # File paths
        paths = re.findall(r'[A-Za-z]:\\[^\s]+|/[^\s]+', text)
        if paths:
            entities["paths"] = paths
        
        # Numbers
        numbers = re.findall(r'\d+', text)
        if numbers:
            entities["numbers"] = [int(n) for n in numbers]
        
        # Code snippets (simplified detection)
        if '```' in text or 'def ' in text or 'function' in text or 'const ' in text:
            entities["has_code"] = True
        
        return entities
    
    def _build_context(self, text: str) -> List[str]:
        """Build context keywords"""
        context = []
        
        for category, keywords in self.context_keywords.items():
            for keyword in keywords:
                if keyword in text:
                    context.append(category)
                    break
        
        return list(set(context))
    
    def _calculate_confidence(self, text: str, intent_type: str) -> float:
        """Calculate confidence score"""
        base_confidence = 0.5
        
        # Increase confidence based on pattern matches
        patterns = self.patterns.get(intent_type, [])
        for pattern in patterns:
            if re.search(pattern, text):
                base_confidence += 0.1
        
        # Decrease for very short inputs
        if len(text.split()) < 3:
            base_confidence -= 0.2
        
        # Cap at 0.95
        return min(0.95, max(0.3, base_confidence))
    
    def _determine_priority(self, intent_type: str, entities: Dict) -> str:
        """Determine task priority"""
        if intent_type == "security":
            return "high"
        if entities.get("has_code"):
            return "medium"
        if intent_type in ["task", "analysis"]:
            return "medium"
        return "low"
