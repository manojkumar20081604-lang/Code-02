"""
╔══════════════════════════════════════════════════════════════════════════════════╗
║                                                                              ║
║               02 v1 - ADVANCED COGNITIVE MODULES                            ║
║                                                                              ║
║        Emotion Detection • Screen Understanding • Digital Twin • Context      ║
║                                                                              ║
╚══════════════════════════════════════════════════════════════════════════════════╝

ADVANCED FEATURES:

1. 🎭 EMOTION DETECTION
   - Voice tone analysis
   - Text sentiment analysis
   - Stress detection
   - Mood tracking
   
2. 👀 SCREEN UNDERSTANDING
   - UI element detection
   - Error recognition
   - Context from screenshots
   - Automatic suggestions
   
3. 🧬 DIGITAL TWIN
   - User behavior learning
   - Habit prediction
   - Productivity analysis
   - Personalized recommendations
   
4. 🧠 CONTEXT ENGINE
   - Session memory
   - Project awareness
   - Time-based patterns
   - Multi-modal context
"""

import os
import re
import time
import json
import base64
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field
from enum import Enum
from collections import deque, defaultdict
from threading import Lock

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("02-Advanced")

# ═══════════════════════════════════════════════════════════════════════════════════
# ENUMS
# ═══════════════════════════════════════════════════════════════════════════════════

class Emotion(Enum):
    HAPPY = "happy"
    SAD = "sad"
    ANGRY = "angry"
    FRUSTRATED = "frustrated"
    EXCITED = "excited"
    CALM = "calm"
    STRESSED = "stressed"
    CONFUSED = "confused"
    NEUTRAL = "neutral"
    TIRED = "tired"
    FOCUSED = "focused"
    BORED = "bored"

class Mood(Enum):
    VERY_POSITIVE = "very_positive"
    POSITIVE = "positive"
    NEUTRAL = "neutral"
    NEGATIVE = "negative"
    VERY_NEGATIVE = "very_negative"

class StressLevel(Enum):
    LOW = "low"
    MODERATE = "moderate"
    HIGH = "high"
    CRITICAL = "critical"

class ActivityType(Enum):
    CODING = "coding"
    READING = "reading"
    BROWSING = "browsing"
    WRITING = "writing"
    LEARNING = "learning"
    BREAK = "break"
    IDLE = "idle"

# ═══════════════════════════════════════════════════════════════════════════════════
# DATA CLASSES
# ═══════════════════════════════════════════════════════════════════════════════════

@dataclass
class EmotionData:
    """Detected emotion data"""
    emotion: Emotion
    confidence: float
    mood: Mood
    stress_level: StressLevel
    energy: float  # 0.0 - 1.0
    timestamp: datetime
    factors: Dict[str, float] = field(default_factory=dict)

@dataclass
class ScreenContext:
    """Screen understanding context"""
    elements: List[Dict] = field(default_factory=list)
    detected_errors: List[str] = field(default_factory=list)
    current_app: str = ""
    activity_type: ActivityType = ActivityType.IDLE
    confidence: float = 0.0
    timestamp: datetime = field(default_factory=datetime.now)

@dataclass
class UserPattern:
    """User behavioral pattern"""
    pattern_id: str
    description: str
    frequency: float  # How often (0.0 - 1.0)
    time_pattern: str  # "morning", "afternoon", "evening", "night"
    triggers: List[str] = field(default_factory=list)
    last_triggered: Optional[datetime] = None
    success_rate: float = 1.0

@dataclass
class Habit:
    """User habit"""
    habit_id: str
    name: str
    trigger: str  # What starts the habit
    action: str   # What they do
    reward: str    # What they get
    streak: int = 0
    best_streak: int = 0
    completion_rate: float = 0.0
    times_triggered: int = 0

@dataclass
class ProductivityMetrics:
    """Productivity metrics for user"""
    date: datetime
    focus_score: float
    tasks_completed: int
    break_time: int  # minutes
    context_switches: int
    productive_hours: float
    unproductive_hours: float
    mood_trend: List[Mood] = field(default_factory=list)

# ═══════════════════════════════════════════════════════════════════════════════════
# EMOTION DETECTION ENGINE
# ═══════════════════════════════════════════════════════════════════════════════════

class EmotionDetector:
    """
    Emotion Detection Engine - Analyzes user emotional state.
    
    Methods:
    - Text sentiment analysis
    - Voice tone analysis (pitch, speed)
    - Behavioral patterns
    - Stress indicators
    """
    
    def __init__(self):
        self.history: deque = deque(maxlen=100)
        self.mood_history: deque = deque(maxlen=50)
        self.current_emotion: Optional[EmotionData] = None
        self.stress_indicators = {
            "high_frequency": 0,  # Rapid messages
            "short_messages": 0,  # Short frustrated responses
            "errors_detected": 0,  # Error messages
            "caps_lock": 0,  # Shouting
            "question_marks": 0,  # Confusion
        }
        
        # Emotion keywords
        self.emotion_keywords = {
            Emotion.HAPPY: ["happy", "great", "awesome", "love", "perfect", "excellent", "wonderful", "fantastic", "😊", "🎉", "love it", "nice"],
            Emotion.SAD: ["sad", "unhappy", "depressed", "down", "disappointed", "upset", "terrible", "awful", "😢", "😔", "unfortunately"],
            Emotion.ANGRY: ["angry", "mad", "furious", "annoyed", "hate", "stupid", "damn", "argh", "😤", "grr", "ugh"],
            Emotion.FRUSTRATED: ["frustrated", "stuck", "can't", "won't work", "impossible", "doesn't work", "useless", "why isn't", "😤", "argh"],
            Emotion.EXCITED: ["excited", "amazing", "wow", "incredible", "awesome", "can't wait", "omg", "holy", "🔥", "😮"],
            Emotion.CONFUSED: ["confused", "don't understand", "what do you mean", "unclear", "lost", "huh", "???", "🤔"],
            Emotion.TIRED: ["tired", "exhausted", "sleepy", "drained", "fatigue", "need coffee", "💤", "😴"],
            Emotion.FOCUSED: ["focused", "in the zone", "concentrating", "working on", "deep work", "flow state", "💪"],
            Emotion.BORED: ["bored", "nothing to do", "stuck", "idle", "waiting", "😐"],
        }
        
        # Sentiment words with weights
        self.positive_words = {
            "great": 0.8, "excellent": 0.9, "perfect": 1.0, "love": 0.8,
            "amazing": 0.9, "wonderful": 0.8, "fantastic": 0.9, "happy": 0.7,
            "good": 0.6, "nice": 0.6, "helpful": 0.7, "awesome": 0.8
        }
        
        self.negative_words = {
            "terrible": -0.8, "awful": -0.9, "hate": -0.9, "angry": -0.8,
            "frustrated": -0.6, "annoyed": -0.5, "sad": -0.6, "bad": -0.5,
            "useless": -0.8, "broken": -0.6, "stupid": -0.7, "wrong": -0.4
        }
        
        logger.info("Emotion Detector initialized")
    
    def analyze_text(self, text: str) -> EmotionData:
        """Analyze text for emotion"""
        text_lower = text.lower()
        words = text_lower.split()
        
        # Calculate sentiment score
        sentiment = self._calculate_sentiment(text_lower)
        
        # Detect emotion keywords
        emotion_scores = defaultdict(float)
        for emotion, keywords in self.emotion_keywords.items():
            for keyword in keywords:
                if keyword in text_lower:
                    emotion_scores[emotion] += 1.0
        
        # Determine primary emotion
        primary_emotion = Emotion.NEUTRAL
        if emotion_scores:
            primary_emotion = max(emotion_scores.items(), key=lambda x: x[1])[0]
        
        # Calculate confidence
        confidence = min(emotion_scores[primary_emotion] / 3.0, 1.0)
        if sentiment > 0.3:
            confidence = max(confidence, 0.7)
        elif sentiment < -0.3:
            confidence = max(confidence, 0.7)
        
        # Update stress indicators
        self._update_stress_indicators(text)
        
        # Calculate stress level
        stress_score = self._calculate_stress_level()
        stress_level = StressLevel.LOW
        if stress_score > 0.7:
            stress_level = StressLevel.CRITICAL
        elif stress_score > 0.5:
            stress_level = StressLevel.HIGH
        elif stress_score > 0.3:
            stress_level = StressLevel.MODERATE
        
        # Determine mood
        mood = self._sentiment_to_mood(sentiment)
        
        # Calculate energy level
        energy = self._calculate_energy(emotion_scores, stress_score)
        
        emotion_data = EmotionData(
            emotion=primary_emotion,
            confidence=confidence,
            mood=mood,
            stress_level=stress_level,
            energy=energy,
            timestamp=datetime.now(),
            factors={
                "sentiment": sentiment,
                "stress_score": stress_score,
                "word_count": len(words),
                "exclamation_count": text.count('!'),
                "question_count": text.count('?')
            }
        )
        
        self.current_emotion = emotion_data
        self.history.append(emotion_data)
        self.mood_history.append(mood)
        
        return emotion_data
    
    def analyze_voice(self, audio_data: Dict) -> EmotionData:
        """
        Analyze voice for emotion.
        
        Audio data should contain:
        - pitch: average pitch (Hz)
        - speed: words per minute
        - pause_frequency: how often pauses occur
        - volume: average volume (0.0 - 1.0)
        """
        pitch = audio_data.get("pitch", 150)
        speed = audio_data.get("speed", 150)
        pause_freq = audio_data.get("pause_frequency", 0.1)
        volume = audio_data.get("volume", 0.5)
        
        # Detect emotion from voice characteristics
        emotion = Emotion.NEUTRAL
        energy = 0.5
        
        if pitch > 200 and speed > 160:  # High pitch, fast speech
            emotion = Emotion.EXCITED
            energy = 0.9
        elif pitch < 100 and speed < 100:  # Low pitch, slow speech
            emotion = Emotion.TIRED
            energy = 0.2
        elif pause_freq > 0.3:  # Lots of pauses
            emotion = Emotion.CONFUSED
            energy = 0.4
        elif volume > 0.8 and pitch > 180:  # Loud, high pitch
            emotion = Emotion.ANGRY
            energy = 0.8
        
        stress_level = StressLevel.MODERATE if pause_freq > 0.2 else StressLevel.LOW
        
        emotion_data = EmotionData(
            emotion=emotion,
            confidence=0.6,  # Voice analysis is less certain
            mood=self._sentiment_to_mood(0.5 if energy > 0.5 else -0.3),
            stress_level=stress_level,
            energy=energy,
            timestamp=datetime.now(),
            factors={
                "pitch": pitch,
                "speed": speed,
                "pause_frequency": pause_freq,
                "volume": volume
            }
        )
        
        self.current_emotion = emotion_data
        self.history.append(emotion_data)
        
        return emotion_data
    
    def _calculate_sentiment(self, text: str) -> float:
        """Calculate sentiment score (-1.0 to 1.0)"""
        score = 0.0
        word_count = 0
        
        for word in text.split():
            if word in self.positive_words:
                score += self.positive_words[word]
                word_count += 1
            elif word in self.negative_words:
                score += self.negative_words[word]
                word_count += 1
        
        if word_count == 0:
            return 0.0
        
        return max(-1.0, min(1.0, score / word_count))
    
    def _update_stress_indicators(self, text: str):
        """Update stress indicators based on text"""
        self.stress_indicators["high_frequency"] += 1 if len(text) < 20 else 0
        self.stress_indicators["short_messages"] += 1 if len(text.split()) < 5 else 0
        self.stress_indicators["errors_detected"] += 1 if "error" in text.lower() else 0
        self.stress_indicators["caps_lock"] += 1 if text.isupper() and len(text) > 5 else 0
        self.stress_indicators["question_marks"] += text.count("?")
    
    def _calculate_stress_level(self) -> float:
        """Calculate overall stress level (0.0 - 1.0)"""
        total = 0
        
        # Weight different factors
        total += min(self.stress_indicators["errors_detected"] / 10, 1.0) * 0.4
        total += min(self.stress_indicators["question_marks"] / 10, 1.0) * 0.2
        total += min(self.stress_indicators["caps_lock"] / 5, 1.0) * 0.3
        total += min(self.stress_indicators["short_messages"] / 20, 1.0) * 0.1
        
        return min(total, 1.0)
    
    def _calculate_energy(self, emotion_scores: Dict, stress: float) -> float:
        """Calculate energy level (0.0 - 1.0)"""
        high_energy = [Emotion.EXCITED, Emotion.ANGRY, Emotion.FOCUSED]
        low_energy = [Emotion.TIRED, Emotion.SAD, Emotion.BORED]
        
        energy = 0.5  # Default
        
        for emotion in high_energy:
            if emotion in emotion_scores:
                energy += 0.2
                
        for emotion in low_energy:
            if emotion in emotion_scores:
                energy -= 0.2
        
        # Stress affects energy
        if stress > 0.6:
            energy -= 0.2
        
        return max(0.0, min(1.0, energy))
    
    def _sentiment_to_mood(self, sentiment: float) -> Mood:
        """Convert sentiment to mood"""
        if sentiment > 0.6:
            return Mood.VERY_POSITIVE
        elif sentiment > 0.2:
            return Mood.POSITIVE
        elif sentiment < -0.6:
            return Mood.VERY_NEGATIVE
        elif sentiment < -0.2:
            return Mood.NEGATIVE
        return Mood.NEUTRAL
    
    def get_mood_trend(self, days: int = 7) -> List[Dict]:
        """Get mood trend over time"""
        trends = []
        for mood in self.mood_history:
            trends.append({
                "mood": mood.value,
                "timestamp": datetime.now().isoformat()
            })
        return trends
    
    def get_recommendation(self) -> str:
        """Get recommendation based on current state"""
        if not self.current_emotion:
            return ""
        
        emotion = self.current_emotion.emotion
        stress = self.current_emotion.stress_level
        energy = self.current_emotion.energy
        
        recommendations = {
            Emotion.TIRED: "You seem tired. Consider taking a short break or having some coffee.",
            Emotion.STRESSED: "You appear stressed. Deep breathing might help, or a quick walk.",
            Emotion.FRUSTRATED: "I notice frustration. Let me help you break this problem down.",
            Emotion.CONFUSED: "I see confusion. Let me explain this more clearly.",
            Emotion.ANGRY: "I sense frustration. Let's tackle this calmly together.",
            Emotion.BORED: "Looking a bit bored? Want to try something new or take a break?",
            Emotion.HAPPY: "Great to see you happy! What's going well today?",
            Emotion.EXCITED: "Your enthusiasm is contagious! Tell me more about what excites you.",
            Emotion.FOCUSED: "You're in a great flow state. Keep up the focused work!",
        }
        
        if stress == StressLevel.HIGH or stress == StressLevel.CRITICAL:
            return "⚠️ High stress detected. I recommend taking a 5-minute break to recharge."
        
        if energy < 0.3:
            return "Low energy detected. Consider a short break or a coffee boost."
        
        return recommendations.get(emotion, "")

# ═══════════════════════════════════════════════════════════════════════════════════
# SCREEN UNDERSTANDING ENGINE
# ═══════════════════════════════════════════════════════════════════════════════════

class ScreenUnderstanding:
    """
    Screen Understanding Engine - Analyzes screen content and context.
    
    Features:
    - UI element detection
    - Error recognition
    - Activity classification
    - Automatic suggestions
    """
    
    def __init__(self):
        self.current_context: Optional[ScreenContext] = None
        self.activity_history: deque = deque(maxlen=50)
        self.error_patterns = [
            (r"error[:\s]+(.+)", "generic_error"),
            (r"exception[:\s]+(.+)", "exception"),
            (r"failed[:\s]+(.+)", "failure"),
            (r"cannot\s+(.+)", "cannot_do"),
            (r"undefined", "undefined"),
            (r"null\s*pointer", "null_pointer"),
            (r"syntax\s+error", "syntax_error"),
            (r"permission\s+denied", "permission_error"),
            (r"connection\s+refused", "connection_error"),
            (r"timeout", "timeout_error"),
            (r"404", "not_found"),
            (r"500", "server_error"),
        ]
        
        self.app_keywords = {
            "code": ["vscode", "visual studio", "pycharm", "intellij", "sublime", "vim", "terminal", "cmd"],
            "browser": ["chrome", "firefox", "safari", "edge", "browser"],
            "documentation": ["docs", "documentation", "readme", "wiki"],
            "communication": ["slack", "discord", "teams", "email", "outlook"],
            "design": ["figma", "sketch", "photoshop", "illustrator"],
        }
        
        self.activity_patterns = {
            ActivityType.CODING: ["def ", "function ", "class ", "import ", "const ", "let ", "var ", "=>", "{"],
            ActivityType.READING: ["scroll", "page", "article", "documentation", "read"],
            ActivityType.BROWSING: ["http", "www", ".com", ".org", "search"],
            ActivityType.WRITING: ["write", "document", "essay", "note", "content"],
            ActivityType.LEARNING: ["tutorial", "course", "learn", "study", "practice"],
        }
        
        logger.info("Screen Understanding initialized")
    
    def analyze_screenshot(self, image_data: base64.b64encode) -> ScreenContext:
        """
        Analyze screenshot for context.
        
        In a real implementation, this would use:
        - OCR for text extraction
        - Image recognition for UI elements
        - Pattern matching for activities
        
        For now, this is a simulation.
        """
        context = ScreenContext(
            timestamp=datetime.now()
        )
        
        # Simulate screen analysis
        context.elements = [
            {"type": "text", "content": "Code Editor", "position": {"x": 100, "y": 50}},
            {"type": "button", "content": "Run", "position": {"x": 200, "y": 100}},
        ]
        
        context.activity_type = ActivityType.CODING
        context.confidence = 0.8
        
        self.current_context = context
        self.activity_history.append(context)
        
        return context
    
    def analyze_text_content(self, text: str) -> ScreenContext:
        """Analyze text content to understand screen"""
        context = ScreenContext(
            timestamp=datetime.now()
        )
        
        # Detect errors
        for pattern, error_type in self.error_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            if matches:
                context.detected_errors.append(f"{error_type}: {matches[0] if matches else 'Unknown'}")
        
        # Detect current app
        text_lower = text.lower()
        for app, keywords in self.app_keywords.items():
            for keyword in keywords:
                if keyword in text_lower:
                    context.current_app = app
                    break
        
        # Detect activity type
        for activity, patterns in self.activity_patterns.items():
            for pattern in patterns:
                if pattern.lower() in text_lower:
                    context.activity_type = activity
                    context.confidence = 0.7
                    break
        
        self.current_context = context
        return context
    
    def detect_errors(self, text: str) -> List[Dict]:
        """Detect errors in text"""
        errors = []
        
        for pattern, error_type in self.error_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            for match in matches:
                errors.append({
                    "type": error_type,
                    "message": match if isinstance(match, str) else match[0] if match else "Unknown error",
                    "severity": self._get_severity(error_type)
                })
        
        return errors
    
    def _get_severity(self, error_type: str) -> str:
        """Get error severity"""
        critical = ["exception", "null_pointer", "permission_error", "server_error"]
        high = ["failure", "syntax_error", "connection_error"]
        medium = ["generic_error", "cannot_do"]
        low = ["timeout_error", "not_found"]
        
        if error_type in critical:
            return "critical"
        elif error_type in high:
            return "high"
        elif error_type in medium:
            return "medium"
        return "low"
    
    def get_suggestion(self, context: ScreenContext) -> Optional[str]:
        """Get automatic suggestion based on screen context"""
        if not context:
            return None
        
        # Error-based suggestions
        if context.detected_errors:
            error = context.detected_errors[0]
            return f"I noticed an error: {error}. Would you like me to help fix it?"
        
        # Activity-based suggestions
        if context.activity_type == ActivityType.CODING:
            return "I see you're coding. Need help with debugging or code generation?"
        elif context.activity_type == ActivityType.LEARNING:
            return "Learning something new? I can help explain concepts."
        elif context.activity_type == ActivityType.READING:
            return "Reading documentation? I can summarize key points."
        
        return None
    
    def get_activity_summary(self) -> Dict:
        """Get summary of recent activities"""
        activities = defaultdict(int)
        
        for context in self.activity_history:
            activities[context.activity_type.value] += 1
        
        return {
            "total_screens": len(self.activity_history),
            "activities": dict(activities),
            "most_active": max(activities.items(), key=lambda x: x[1])[0] if activities else "idle"
        }

# ═══════════════════════════════════════════════════════════════════════════════════
# DIGITAL TWIN ENGINE
# ═══════════════════════════════════════════════════════════════════════════════════

class DigitalTwin:
    """
    Digital Twin - Creates a virtual model of the user.
    
    Features:
    - Behavior learning
    - Habit tracking
    - Productivity analysis
    - Personalized recommendations
    - Prediction of needs
    """
    
    def __init__(self, user_id: str = "default"):
        self.user_id = user_id
        self.habits: Dict[str, Habit] = {}
        self.patterns: Dict[str, UserPattern] = {}
        self.productivity_history: List[ProductivityMetrics] = []
        self.preferences: Dict[str, Any] = {}
        self.learning_data: Dict[str, List] = defaultdict(list)
        
        # Time-based patterns
        self.time_patterns = {
            "morning": [],    # 5am - 12pm
            "afternoon": [],   # 12pm - 5pm
            "evening": [],    # 5pm - 9pm
            "night": []       # 9pm - 5am
        }
        
        # Weekly patterns
        self.weekly_patterns = defaultdict(list)
        
        # Learning thresholds
        self.min_occurrences = 3  # Min times to establish pattern
        
        logger.info(f"Digital Twin initialized for user: {user_id}")
    
    def learn_from_interaction(self, interaction: Dict):
        """
        Learn from user interaction.
        
        Interaction should contain:
        - timestamp: datetime
        - type: "command", "question", "feedback"
        - content: str
        - context: dict
        - success: bool
        - duration: float (seconds)
        """
        timestamp = interaction.get("timestamp", datetime.now())
        interaction_type = interaction.get("type", "")
        content = interaction.get("content", "")
        success = interaction.get("success", True)
        
        # Update time patterns
        self._update_time_patterns(timestamp, interaction)
        
        # Update weekly patterns
        self._update_weekly_patterns(timestamp, interaction)
        
        # Learn preferences
        self._learn_preferences(interaction)
        
        # Detect and update habits
        self._detect_habits(interaction)
        
        # Learn from success/failure
        if success:
            self._learn_from_success(interaction)
        else:
            self._learn_from_failure(interaction)
    
    def _update_time_patterns(self, timestamp: datetime, interaction: Dict):
        """Update time-based patterns"""
        hour = timestamp.hour
        
        if 5 <= hour < 12:
            time_slot = "morning"
        elif 12 <= hour < 17:
            time_slot = "afternoon"
        elif 17 <= hour < 21:
            time_slot = "evening"
        else:
            time_slot = "night"
        
        self.time_patterns[time_slot].append(interaction)
    
    def _update_weekly_patterns(self, timestamp: datetime, interaction: Dict):
        """Update weekly patterns"""
        day = timestamp.strftime("%A")
        self.weekly_patterns[day].append(interaction)
    
    def _learn_preferences(self, interaction: Dict):
        """Learn user preferences"""
        content = interaction.get("content", "").lower()
        interaction_type = interaction.get("type", "")
        
        # Learn language preferences
        if "python" in content:
            self.preferences["preferred_language"] = "python"
        elif "javascript" in content or "js" in content:
            self.preferences["preferred_language"] = "javascript"
        
        # Learn response style preferences
        if interaction_type == "feedback":
            if any(word in content for word in ["detailed", "explain", "more"]):
                self.preferences["response_style"] = "detailed"
            elif any(word in content for word in ["brief", "short", "quick"]):
                self.preferences["response_style"] = "concise"
        
        # Learn time preferences
        hour = interaction.get("timestamp", datetime.now()).hour
        if 22 <= hour or hour < 6:
            self.preferences["night_owl"] = True
    
    def _detect_habits(self, interaction: Dict):
        """Detect and track habits"""
        content = interaction.get("content", "").lower()
        timestamp = interaction.get("timestamp", datetime.now())
        
        # Check for common habit triggers
        habit_triggers = {
            "morning coffee": ["coffee", "morning", "start"],
            "code review": ["review", "check code", "pull request"],
            "break time": ["break", "rest", "lunch"],
            "end of day": ["wrap up", "finish", "done for today"],
        }
        
        for habit_name, keywords in habit_triggers.items():
            if any(kw in content for kw in keywords):
                if habit_name not in self.habits:
                    self.habits[habit_name] = Habit(
                        habit_id=habit_name,
                        name=habit_name,
                        trigger=keywords[0],
                        action=habit_name,
                        reward="productivity"
                    )
                
                habit = self.habits[habit_name]
                habit.times_triggered += 1
                habit.last_triggered = timestamp
    
    def _learn_from_success(self, interaction: Dict):
        """Learn from successful interactions"""
        content = interaction.get("content", "")
        self.learning_data["successful_interactions"].append({
            "content": content,
            "timestamp": datetime.now().isoformat()
        })
    
    def _learn_from_failure(self, interaction: Dict):
        """Learn from failed interactions"""
        content = interaction.get("content", "")
        self.learning_data["failed_interactions"].append({
            "content": content,
            "timestamp": datetime.now().isoformat(),
            "failure_reason": interaction.get("failure_reason", "unknown")
        })
    
    def predict_next_action(self) -> Optional[str]:
        """Predict user's next likely action"""
        current_hour = datetime.now().hour
        current_day = datetime.now().strftime("%A")
        
        predictions = []
        
        # Time-based prediction
        if 5 <= current_hour < 12:
            recent = self.time_patterns.get("morning", [])
        elif 12 <= current_hour < 17:
            recent = self.time_patterns.get("afternoon", [])
        elif 17 <= current_hour < 21:
            recent = self.time_patterns.get("evening", [])
        else:
            recent = self.time_patterns.get("night", [])
        
        if recent:
            # Find most common interaction type
            from collections import Counter
            types = [r.get("type", "unknown") for r in recent[-10:]]
            most_common = Counter(types).most_common(1)
            if most_common:
                predictions.append(f"You usually do {most_common[0][0]} tasks at this time")
        
        # Day-based prediction
        day_activities = self.weekly_patterns.get(current_day, [])
        if day_activities:
            from collections import Counter
            types = [a.get("type", "unknown") for a in day_activities[-10:]]
            most_common = Counter(types).most_common(1)
            if most_common:
                predictions.append(f"On {current_day}s, you often do {most_common[0][0]}")
        
        return predictions[0] if predictions else None
    
    def get_productivity_insights(self) -> Dict:
        """Get productivity insights"""
        if not self.productivity_history:
            return {
                "status": "No data yet",
                "message": "Keep using 02 to build your productivity profile"
            }
        
        latest = self.productivity_history[-1]
        
        return {
            "focus_score": latest.focus_score,
            "tasks_completed": latest.tasks_completed,
            "productive_hours": latest.productive_hours,
            "mood_trend": [m.value for m in latest.mood_trend[-5:]] if latest.mood_trend else []
        }
    
    def get_recommendations(self) -> List[str]:
        """Get personalized recommendations"""
        recommendations = []
        
        # Habit-based recommendations
        for habit in self.habits.values():
            if habit.completion_rate < 0.5:
                recommendations.append(
                    f"Your '{habit.name}' habit has low completion. Try breaking it into smaller steps."
                )
        
        # Time-based recommendations
        morning_count = len(self.time_patterns.get("morning", []))
        night_count = len(self.time_patterns.get("night", []))
        
        if night_count > morning_count * 2:
            recommendations.append(
                "You're more active at night. Consider shifting some tasks to morning for better energy."
            )
        
        # Preference-based recommendations
        if self.preferences.get("response_style") == "detailed":
            recommendations.append("I'll provide thorough explanations with examples.")
        
        return recommendations
    
    def get_summary(self) -> Dict:
        """Get digital twin summary"""
        return {
            "user_id": self.user_id,
            "habits_count": len(self.habits),
            "patterns_count": len(self.patterns),
            "preferences": self.preferences,
            "insights": self.get_productivity_insights(),
            "recommendations": self.get_recommendations(),
            "next_prediction": self.predict_next_action()
        }

# ═══════════════════════════════════════════════════════════════════════════════════
# CONTEXT ENGINE
# ═══════════════════════════════════════════════════════════════════════════════════

class ContextEngine:
    """
    Context Engine - Maintains multi-modal context.
    
    Features:
    - Session memory
    - Project awareness
    - Time-based context
    - Cross-modal context
    """
    
    def __init__(self):
        self.current_project: Optional[str] = None
        self.project_stack: List[str] = []
        self.session_context: Dict[str, Any] = {}
        self.context_history: deque = deque(maxlen=100)
        
        self.context_sources = {
            "screen": None,
            "voice": None,
            "text": None,
            "emotion": None,
            "time": None,
            "location": None
        }
        
        logger.info("Context Engine initialized")
    
    def update_context(self, source: str, data: Any):
        """Update context from a source"""
        self.context_sources[source] = data
        self._push_to_history(source, data)
    
    def _push_to_history(self, source: str, data: Any):
        """Push context to history"""
        self.context_history.append({
            "source": source,
            "data": data,
            "timestamp": datetime.now()
        })
    
    def get_context(self) -> Dict[str, Any]:
        """Get current consolidated context"""
        context = {
            "sources": {k: v for k, v in self.context_sources.items() if v is not None},
            "project": self.current_project,
            "project_stack": self.project_stack.copy(),
            "session_duration": self._get_session_duration()
        }
        context.update(self.session_context)
        return context
    
    def _get_session_duration(self) -> float:
        """Get session duration in minutes"""
        if not self.context_history:
            return 0.0
        first = self.context_history[0]["timestamp"]
        return (datetime.now() - first).total_seconds() / 60
    
    def set_project(self, project_name: str):
        """Set current project context"""
        if self.current_project and self.current_project != project_name:
            self.project_stack.append(self.current_project)
        self.current_project = project_name
        logger.info(f"Project set to: {project_name}")
    
    def switch_project(self, project_name: str):
        """Switch to a different project"""
        if self.current_project and self.current_project != project_name:
            self.project_stack.append(self.current_project)
        self.current_project = project_name
    
    def return_to_previous_project(self) -> Optional[str]:
        """Return to previous project"""
        if self.project_stack:
            self.current_project = self.project_stack.pop()
            return self.current_project
        return None
    
    def get_context_summary(self) -> str:
        """Get human-readable context summary"""
        parts = []
        
        if self.current_project:
            parts.append(f"Working on: {self.current_project}")
        
        if self.context_sources.get("screen"):
            parts.append("Screen active")
        
        if self.context_sources.get("emotion"):
            emotion = self.context_sources["emotion"]
            parts.append(f"Mood: {emotion.emotion.value}")
        
        duration = self._get_session_duration()
        if duration > 0:
            parts.append(f"Session: {int(duration)}m")
        
        return " | ".join(parts) if parts else "No active context"

# ═══════════════════════════════════════════════════════════════════════════════════
# PROACTIVE SUGGESTION ENGINE
# ═══════════════════════════════════════════════════════════════════════════════════

class ProactiveSuggestionEngine:
    """
    Proactive Suggestion Engine - Anticipates user needs.
    
    Features:
    - Time-based suggestions
    - Pattern-based suggestions
    - Context-aware suggestions
    - Learning-based suggestions
    """
    
    def __init__(self, digital_twin: DigitalTwin = None):
        self.digital_twin = digital_twin
        self.suggestion_history: deque = deque(maxlen=50)
        self.acceptance_rate = 0.0
        
        # Suggestion rules
        self.rules = [
            {
                "name": "break_reminder",
                "condition": lambda ctx: ctx.get("session_duration", 0) > 60,
                "suggestion": "You've been working for over an hour. Consider taking a short break!",
                "priority": 1
            },
            {
                "name": "morning_planning",
                "condition": lambda ctx: ctx.get("hour", 0) == 9,
                "suggestion": "Good morning! Would you like to plan your day?",
                "priority": 2
            },
            {
                "name": "end_of_day",
                "condition": lambda ctx: ctx.get("hour", 0) == 17,
                "suggestion": "End of workday approaching. Want to review what you accomplished?",
                "priority": 2
            },
            {
                "name": "code_reminder",
                "condition": lambda ctx: ctx.get("project") and "code" in ctx.get("project", "").lower(),
                "suggestion": "Remember to commit your code regularly!",
                "priority": 3
            },
        ]
        
        logger.info("Proactive Suggestion Engine initialized")
    
    def evaluate_suggestions(self, context: Dict) -> List[Dict]:
        """Evaluate which suggestions to make"""
        suggestions = []
        
        context["hour"] = datetime.now().hour
        
        for rule in self.rules:
            if rule["condition"](context):
                suggestions.append({
                    "suggestion": rule["suggestion"],
                    "priority": rule["priority"],
                    "rule": rule["name"]
                })
        
        # Add digital twin predictions
        if self.digital_twin:
            prediction = self.digital_twin.predict_next_action()
            if prediction:
                suggestions.append({
                    "suggestion": f"Based on your patterns: {prediction}",
                    "priority": 4,
                    "rule": "digital_twin"
                })
        
        # Sort by priority
        suggestions.sort(key=lambda x: x["priority"])
        
        return suggestions[:3]  # Return top 3
    
    def record_feedback(self, suggestion: str, accepted: bool):
        """Record user feedback on suggestion"""
        self.suggestion_history.append({
            "suggestion": suggestion,
            "accepted": accepted,
            "timestamp": datetime.now()
        })
        
        # Update acceptance rate
        total = len(self.suggestion_history)
        accepted_count = sum(1 for s in self.suggestion_history if s["accepted"])
        self.acceptance_rate = accepted_count / total if total > 0 else 0

# ═══════════════════════════════════════════════════════════════════════════════════
# EXPORTS
# ═══════════════════════════════════════════════════════════════════════════════════

__all__ = [
    'EmotionDetector',
    'ScreenUnderstanding', 
    'DigitalTwin',
    'ContextEngine',
    'ProactiveSuggestionEngine',
    'Emotion',
    'Mood',
    'StressLevel',
    'ActivityType',
    'EmotionData',
    'ScreenContext',
    'UserPattern',
    'Habit',
    'ProductivityMetrics'
]
