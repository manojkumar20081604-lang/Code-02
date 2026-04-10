"""
============================================================
DATA SCIENCE MODULE - ML-Based Intelligence
============================================================
Intent classification, preprocessing, and data pipeline
"""

import re
import json
import os
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
from collections import Counter
import logging
from datetime import datetime

logger = logging.getLogger("DataScience")


# ================================================================
# PREPROCESSING PIPELINE
# ================================================================

class TextPreprocessor:
    """
    Text preprocessing for command classification
    """
    
    def __init__(self):
        self.stop_words = {
            'a', 'an', 'the', 'and', 'or', 'but', 'in', 'on', 'at',
            'to', 'for', 'of', 'with', 'by', 'from', 'as', 'is', 'was',
            'are', 'were', 'been', 'be', 'have', 'has', 'had', 'do', 'does',
            'did', 'will', 'would', 'should', 'could', 'may', 'might', 'can'
        }
    
    def clean(self, text: str) -> str:
        """Clean input text"""
        # Lowercase
        text = text.lower().strip()
        
        # Remove URLs
        text = re.sub(r'https?://\S+', '', text)
        
        # Remove email addresses
        text = re.sub(r'\S+@\S+', '', text)
        
        # Remove special characters but keep spaces
        text = re.sub(r'[^\w\s]', ' ', text)
        
        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text).strip()
        
        return text
    
    def tokenize(self, text: str) -> List[str]:
        """Tokenize text into words"""
        return text.split()
    
    def remove_stopwords(self, tokens: List[str]) -> List[str]:
        """Remove stopwords"""
        return [t for t in tokens if t not in self.stop_words]
    
    def extract_features(self, text: str) -> Dict[str, Any]:
        """Extract features from text"""
        
        text_lower = text.lower()
        
        features = {
            # Length features
            'char_count': len(text),
            'word_count': len(text.split()),
            'avg_word_len': sum(len(w) for w in text.split()) / max(len(text.split()), 1),
            
            # Pattern features
            'has_command': bool(re.search(r'^(ls|cd|cat|grep|find|ps|kill)', text_lower)),
            'has_install': 'install' in text_lower,
            'has_http': 'http' in text_lower,
            'has_path': bool(re.search(r'/|\.[a-z]{1,4}', text_lower)),
            'has_number': bool(re.search(r'\d', text_lower)),
            
            # Command type indicators
            'is_shell_cmd': bool(re.search(r'^(ls|cd|cat|grep|find|ps|kill|rm|mkdir|touch|pwd|whoami|uname|echo)', text_lower)),
            'is_admin_cmd': bool(re.search(r'^(sudo|apt|pacman|dnf|yum|chmod|chown|useradd)', text_lower)),
            'is_network_cmd': bool(re.search(r'^(ping|curl|wget|netstat|ifconfig|ip)', text_lower)),
            
            # Action words
            'action_create': bool(re.search(r'\b(build|create|make|generate|new)\b', text_lower)),
            'action_delete': bool(re.search(r'\b(delete|remove|rm|uninstall)\b', text_lower)),
            'action_update': bool(re.search(r'\b(update|upgrade|install|add)\b', text_lower)),
            'action_query': bool(re.search(r'\b(show|list|get|find|search)\b', text_lower)),
        }
        
        return features
    
    def process(self, text: str) -> Dict[str, Any]:
        """Full preprocessing pipeline"""
        
        cleaned = self.clean(text)
        tokens = self.tokenize(cleaned)
        filtered = self.remove_stopwords(tokens)
        features = self.extract_features(text)
        
        return {
            'original': text,
            'cleaned': cleaned,
            'tokens': tokens,
            'filtered_tokens': filtered,
            'features': features
        }


# ================================================================
# INTENT CLASSIFIER
# ================================================================

class IntentClassifier:
    """
    Rule-based + Statistical intent classifier
    Uses keyword matching with confidence scoring
    """
    
    def __init__(self):
        self.preprocessor = TextPreprocessor()
        self.intents = {
            'command': {
                'keywords': ['ls', 'cd', 'cat', 'grep', 'find', 'ps', 'kill', 'rm', 'mkdir', 
                            'touch', 'pwd', 'whoami', 'uname', 'echo', 'chmod', 'chown', 'cp', 'mv'],
                'weight': 1.0
            },
            'install': {
                'keywords': ['install', 'pip install', 'npm install', 'apt install', 'pacman -s',
                            'brew install', 'download', 'setup', 'add package'],
                'weight': 1.0
            },
            'security_scan': {
                'keywords': ['scan', 'port scan', 'nmap', 'vulnerability', 'check security',
                            'threat', 'malware', 'phishing', 'hack', 'penetrat'],
                'weight': 1.0
            },
            'network': {
                'keywords': ['ping', 'curl', 'wget', 'network', 'ip', 'connection', 'download',
                            'fetch', 'http', 'url'],
                'weight': 0.8
            },
            'file': {
                'keywords': ['file', 'read', 'write', 'open', 'save', 'delete file', 
                            'create file', 'directory', 'folder'],
                'weight': 0.9
            },
            'system': {
                'keywords': ['system', 'process', 'memory', 'cpu', 'disk', 'monitor',
                            'status', 'uptime', 'service', 'daemon'],
                'weight': 0.8
            },
            'think': {
                'keywords': ['think', 'reason', 'analyze', 'explain', 'how does', 'why',
                            'what is', 'understand'],
                'weight': 0.7
            },
            'help': {
                'keywords': ['help', 'command', 'how to', 'what can', 'show'],
                'weight': 0.9
            },
            'chat': {
                'keywords': ['hello', 'hi', 'hey', 'thanks', 'bye', 'good morning'],
                'weight': 0.5
            }
        }
        
        logger.info("Intent classifier initialized")
    
    def classify(self, text: str) -> Dict[str, Any]:
        """Classify text intent"""
        
        # Preprocess
        processed = self.preprocessor.process(text)
        text_lower = processed['cleaned']
        tokens = set(processed['tokens'])
        
        # Score each intent
        scores = {}
        
        for intent_name, intent_info in self.intents.items():
            score = 0.0
            matches = []
            
            for keyword in intent_info['keywords']:
                if keyword in text_lower:
                    score += intent_info['weight']
                    matches.append(keyword)
            
            if matches:
                # Normalize score
                scores[intent_name] = {
                    'score': score,
                    'matches': matches,
                    'confidence': min(score / 3.0, 1.0)  # Cap at 1.0
                }
        
        # Get best match
        if scores:
            best = max(scores.items(), key=lambda x: x[1]['score'])
            return {
                'intent': best[0],
                'confidence': best[1]['confidence'],
                'all_scores': scores,
                'features': processed['features']
            }
        
        return {
            'intent': 'unknown',
            'confidence': 0.0,
            'all_scores': {},
            'features': processed['features']
        }
    
    def extract_entities(self, text: str, intent: str) -> Dict[str, Any]:
        """Extract entities based on intent"""
        
        entities = {}
        text_lower = text.lower()
        
        # Package names
        if intent == 'install':
            packages = re.findall(r'(?:install|add)\s+(\w+)', text_lower)
            if not packages:
                packages = re.findall(r'(pip|npm|apt|pacman)\s+(\w+)', text_lower)
                entities['packages'] = [p[1] for p in packages] if packages else []
            else:
                entities['packages'] = packages
        
        # Commands
        if intent == 'command':
            cmd_match = re.search(r'^(ls|cd|cat|grep|find|ps|kill|rm|mkdir)', text_lower)
            if cmd_match:
                entities['command'] = cmd_match.group(1)
        
        # URLs
        urls = re.findall(r'https?://\S+', text)
        if urls:
            entities['url'] = urls[0]
        
        # IP addresses
        ips = re.findall(r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}', text)
        if ips:
            entities['ip'] = ips[0]
        
        # Ports
        ports = re.findall(r'port[:\s]+(\d+)', text_lower)
        if ports:
            entities['port'] = int(ports[0])
        
        return entities


# ================================================================
# DATA COLLECTION
# ================================================================

class DataCollector:
    """
    Collects and stores training data for improvement
    """
    
    def __init__(self, data_dir: str = "data/logs"):
        self.data_dir = data_dir
        os.makedirs(data_dir, exist_ok=True)
        
        self.interactions_file = os.path.join(data_dir, "interactions.jsonl")
        self.decisions_file = os.path.join(data_dir, "decisions.jsonl")
        
        self.interaction_count = 0
        self._load_count()
    
    def _load_count(self):
        """Load interaction count"""
        if os.path.exists(self.interactions_file):
            try:
                with open(self.interactions_file, 'r') as f:
                    self.interaction_count = sum(1 for _ in f)
            except:
                self.interaction_count = 0
    
    def log_interaction(self, user_input: str, intent: str, confidence: float,
                        entities: Dict, result: Dict):
        """Log an interaction for future training"""
        
        entry = {
            "timestamp": datetime.now().isoformat(),
            "user_input": user_input,
            "intent": intent,
            "confidence": confidence,
            "entities": entities,
            "success": result.get("success", False),
            "module_used": result.get("module", "unknown")
        }
        
        with open(self.interactions_file, 'a') as f:
            f.write(json.dumps(entry) + "\n")
        
        self.interaction_count += 1
    
    def log_decision(self, input_text: str, decision: str, reasoning: str):
        """Log a decision for analysis"""
        
        entry = {
            "timestamp": datetime.now().isoformat(),
            "input": input_text,
            "decision": decision,
            "reasoning": reasoning
        }
        
        with open(self.decisions_file, 'a') as f:
            f.write(json.dumps(entry) + "\n")
    
    def get_training_data(self, limit: int = 1000) -> List[Dict]:
        """Get recent interactions for training"""
        
        data = []
        
        if os.path.exists(self.interactions_file):
            try:
                with open(self.interactions_file, 'r') as f:
                    lines = f.readlines()
                
                for line in lines[-limit:]:
                    try:
                        data.append(json.loads(line.strip()))
                    except:
                        continue
            except:
                pass
        
        return data
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get data statistics"""
        
        interactions = self.get_training_data(limit=10000)
        
        intent_counts = Counter(i.get('intent', 'unknown') for i in interactions)
        success_rate = sum(1 for i in interactions if i.get('success')) / max(len(interactions), 1)
        
        return {
            "total_interactions": len(interactions),
            "intent_distribution": dict(intent_counts.most_common(10)),
            "success_rate": success_rate,
            "most_successful_intent": intent_counts.most_common(1)[0][0] if intent_counts else "none"
        }
    
    def export_data(self, filepath: str) -> bool:
        """Export all data to JSON"""
        
        try:
            data = self.get_training_data(limit=100000)
            
            with open(filepath, 'w') as f:
                json.dump(data, f, indent=2)
            
            return True
        except Exception as e:
            logger.error(f"Export failed: {e}")
            return False


# ================================================================
# SMART ROUTER
# ================================================================

class SmartRouter:
    """
    Combines ML classifier with rule-based routing
    """
    
    def __init__(self):
        self.classifier = IntentClassifier()
        self.preprocessor = TextPreprocessor()
        self.data_collector = DataCollector()
        
        # Module routing
        self.module_map = {
            'command': 'automation',
            'install': 'installer',
            'security_scan': 'security',
            'network': 'automation',
            'file': 'automation',
            'system': 'automation',
            'think': 'brain',
            'help': 'brain',
            'chat': 'brain'
        }
        
        logger.info("Smart router initialized")
    
    def route(self, user_input: str) -> Dict[str, Any]:
        """Route user input to appropriate module"""
        
        # Classify intent
        classification = self.classifier.classify(user_input)
        intent = classification['intent']
        
        # Extract entities
        entities = self.classifier.extract_entities(user_input, intent)
        
        # Determine module
        module = self.module_map.get(intent, 'brain')
        
        # Generate routing info
        routing = {
            'intent': intent,
            'confidence': classification['confidence'],
            'module': module,
            'entities': entities,
            'features': classification['features'],
            'all_intents': {k: v['score'] for k, v in classification['all_scores'].items()}
        }
        
        # Log for learning
        self.data_collector.log_decision(
            user_input,
            intent,
            f"Routed to {module} (confidence: {classification['confidence']:.2f})"
        )
        
        return routing
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get routing statistics"""
        return self.data_collector.get_statistics()


# Singletons
_preprocessor: Optional[TextPreprocessor] = None
_classifier: Optional[IntentClassifier] = None
_collector: Optional[DataCollector] = None
_router: Optional[SmartRouter] = None


def get_preprocessor() -> TextPreprocessor:
    global _preprocessor
    if _preprocessor is None:
        _preprocessor = TextPreprocessor()
    return _preprocessor


def get_classifier() -> IntentClassifier:
    global _classifier
    if _classifier is None:
        _classifier = IntentClassifier()
    return _classifier


def get_collector() -> DataCollector:
    global _collector
    if _collector is None:
        _collector = DataCollector()
    return _collector


def get_router() -> SmartRouter:
    global _router
    if _router is None:
        _router = SmartRouter()
    return _router


__all__ = [
    'TextPreprocessor',
    'IntentClassifier', 
    'DataCollector',
    'SmartRouter',
    'get_preprocessor',
    'get_classifier',
    'get_collector',
    'get_router'
]
