"""
02 v1 - Flask API Server
Main server integrating all 02 systems
"""

import os
import sys
import json
import logging
from datetime import datetime
from functools import wraps
from flask import Flask, request, jsonify, render_template
from flask_cors import CORS

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from core.cognitive import CognitiveSystem, create_cognitive_system, Personality, Intent
from core.agent import AutonomousAgent, WorkflowExecutor
from core.voice import VoiceEngine, VoiceConfig
from core.advanced import (
    EmotionDetector, ScreenUnderstanding, DigitalTwin, 
    ContextEngine, ProactiveSuggestionEngine,
    Emotion, Mood, StressLevel, ActivityType
)
from agents.dev import DevAssistant

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s'
)
logger = logging.getLogger("02-Server")

app = Flask(__name__, static_folder='../frontend', template_folder='../frontend')
CORS(app)

# ═══════════════════════════════════════════════════════════════════════════════════
# SYSTEM INITIALIZATION
# ═══════════════════════════════════════════════════════════════════════════════════

# Initialize systems
cognitive_system = None
agent = None
dev_assistant = None
voice_engine = None
emotion_detector = None
screen_understanding = None
digital_twin = None
context_engine = None
proactive_engine = None

def initialize_systems():
    """Initialize all 02 systems"""
    global cognitive_system, agent, dev_assistant, voice_engine
    global emotion_detector, screen_understanding, digital_twin, context_engine, proactive_engine
    
    try:
        cognitive_system = create_cognitive_system(
            personality="jarvis",
            user_id="02_user"
        )
        logger.info("Cognitive System initialized")
    except Exception as e:
        logger.error(f"Cognitive init failed: {e}")
        cognitive_system = None
    
    try:
        agent = AutonomousAgent(cognitive_system)
        logger.info("Autonomous Agent initialized")
    except Exception as e:
        logger.error(f"Agent init failed: {e}")
        agent = None
    
    try:
        dev_assistant = DevAssistant()
        logger.info("Dev Assistant initialized")
    except Exception as e:
        logger.error(f"Dev init failed: {e}")
        dev_assistant = None
    
    try:
        voice_engine = VoiceEngine()
        logger.info("Voice Engine initialized")
    except Exception as e:
        logger.error(f"Voice init failed: {e}")
        voice_engine = None
    
    # Initialize advanced systems
    try:
        emotion_detector = EmotionDetector()
        logger.info("Emotion Detector initialized")
    except Exception as e:
        logger.error(f"Emotion init failed: {e}")
        emotion_detector = None
    
    try:
        screen_understanding = ScreenUnderstanding()
        logger.info("Screen Understanding initialized")
    except Exception as e:
        logger.error(f"Screen init failed: {e}")
        screen_understanding = None
    
    try:
        digital_twin = DigitalTwin(user_id="02_user")
        logger.info("Digital Twin initialized")
    except Exception as e:
        logger.error(f"Digital Twin init failed: {e}")
        digital_twin = None
    
    try:
        context_engine = ContextEngine()
        logger.info("Context Engine initialized")
    except Exception as e:
        logger.error(f"Context init failed: {e}")
        context_engine = None
    
    try:
        proactive_engine = ProactiveSuggestionEngine(digital_twin)
        logger.info("Proactive Engine initialized")
    except Exception as e:
        logger.error(f"Proactive init failed: {e}")
        proactive_engine = None

initialize_systems()

# ═══════════════════════════════════════════════════════════════════════════════════
# API HELPERS
# ═══════════════════════════════════════════════════════════════════════════════════

def success_response(data=None, message="OK"):
    return jsonify({"success": True, "data": data, "message": message})

def error_response(message, code=400):
    return jsonify({"success": False, "error": message}), code

def require_cognitive(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        if not cognitive_system:
            return error_response("Cognitive system not available", 503)
        return f(*args, **kwargs)
    return wrapper

# ═══════════════════════════════════════════════════════════════════════════════════
# HEALTH & STATUS
# ═══════════════════════════════════════════════════════════════════════════════════

@app.route('/health', methods=['GET'])
def health():
    """Health check endpoint"""
    status = {
        "status": "online",
        "name": "02 v1",
        "version": "1.0.0",
        "timestamp": datetime.now().isoformat(),
        "systems": {
            "cognitive": cognitive_system is not None,
            "agent": agent is not None,
            "dev": dev_assistant is not None,
            "voice": voice_engine is not None,
        }
    }
    
    if cognitive_system:
        status.update(cognitive_system.get_status())
    
    return jsonify(status)

@app.route('/status', methods=['GET'])
@require_cognitive
def status():
    """Get full system status"""
    return success_response(cognitive_system.get_status())

# ═══════════════════════════════════════════════════════════════════════════════════
# CHAT & COGNITIVE
# ═══════════════════════════════════════════════════════════════════════════════════

@app.route('/chat', methods=['POST'])
@require_cognitive
def chat():
    """Main chat endpoint"""
    data = request.get_json() or {}
    message = data.get('message', '').strip()
    
    if not message:
        return error_response("Empty message")
    
    try:
        result = cognitive_system.process(message)
        return success_response(result)
    except Exception as e:
        logger.error(f"Chat error: {e}")
        return error_response(str(e))

@app.route('/cognitive/think', methods=['POST'])
@require_cognitive
def think():
    """Process thought without full execution"""
    data = request.get_json() or {}
    message = data.get('message', '').strip()
    
    if not message:
        return error_response("Empty message")
    
    thought = cognitive_system.brain.think(message)
    return success_response(thought.to_dict())

@app.route('/cognitive/personality', methods=['POST'])
@require_cognitive
def set_personality():
    """Change personality"""
    data = request.get_json() or {}
    personality = data.get('personality', 'jarvis').lower()
    
    personality_map = {
        "jarvis": Personality.JARVIS,
        "friendly": Personality.FRIENDLY,
        "hacker": Personality.HACKER,
        "focused": Personality.FOCUSED,
    }
    
    if personality not in personality_map:
        return error_response(f"Unknown personality: {personality}")
    
    cognitive_system.set_personality(personality_map[personality])
    return success_response({"personality": personality})

# ═══════════════════════════════════════════════════════════════════════════════════
# MEMORY
# ═══════════════════════════════════════════════════════════════════════════════════

@app.route('/memory/store', methods=['POST'])
@require_cognitive
def store_memory():
    """Store a memory"""
    data = request.get_json() or {}
    content = data.get('content', '')
    memory_type = data.get('type', 'episodic').upper()
    tags = data.get('tags', [])
    importance = data.get('importance', 0.5)
    
    if not content:
        return error_response("Empty content")
    
    from core.cognitive import MemoryType
    mt = MemoryType[memory_type] if memory_type in [m.name for m in MemoryType] else MemoryType.EPISODIC
    
    node = cognitive_system.memory.store(content, mt, tags, importance)
    return success_response(node.to_dict())

@app.route('/memory/recall', methods=['GET'])
@require_cognitive
def recall_memory():
    """Recall memories"""
    query = request.args.get('query', '')
    memory_type = request.args.get('type')
    limit = int(request.args.get('limit', 5))
    
    from core.cognitive import MemoryType
    mt = None
    if memory_type:
        mt = MemoryType[memory_type.upper()] if memory_type.upper() in [m.name for m in MemoryType] else None
    
    memories = cognitive_system.memory.recall(query, mt, limit)
    return success_response([m.to_dict() for m in memories])

@app.route('/memory/context', methods=['GET'])
@require_cognitive
def memory_context():
    """Get working memory context"""
    limit = int(request.args.get('limit', 10))
    context = cognitive_system.memory.get_context(limit)
    return success_response(context)

@app.route('/memory/forget', methods=['POST'])
@require_cognitive
def forget_memory():
    """Forget a memory"""
    data = request.get_json() or {}
    node_id = data.get('id', '')
    
    if not node_id:
        return error_response("Memory ID required")
    
    success = cognitive_system.memory.forget(node_id)
    return success_response({"forgotten": success})

@app.route('/memory/stats', methods=['GET'])
@require_cognitive
def memory_stats():
    """Get memory statistics"""
    return success_response(cognitive_system.memory.stats)

# ═══════════════════════════════════════════════════════════════════════════════════
# AUTONOMOUS AGENT
# ═══════════════════════════════════════════════════════════════════════════════════

@app.route('/agent/status', methods=['GET'])
def agent_status():
    """Get agent status"""
    if not agent:
        return error_response("Agent not available", 503)
    return success_response(agent.get_status())

@app.route('/agent/task/create', methods=['POST'])
def create_task():
    """Create a new task"""
    if not agent:
        return error_response("Agent not available", 503)
    
    data = request.get_json() or {}
    description = data.get('description', '')
    priority = data.get('priority', 2)
    
    if not description:
        return error_response("Task description required")
    
    task = agent.create_task(description, priority)
    return success_response({
        "id": task.id,
        "description": task.description,
        "status": task.status
    })

@app.route('/agent/tasks', methods=['GET'])
def list_tasks():
    """List active tasks"""
    if not agent:
        return error_response("Agent not available", 503)
    return success_response(agent.get_active_tasks())

@app.route('/agent/autonomous/start', methods=['POST'])
def start_autonomous():
    """Enable autonomous mode"""
    if not agent:
        return error_response("Agent not available", 503)
    agent.enable_autonomous_mode()
    return success_response({"autonomous": True})

@app.route('/agent/autonomous/stop', methods=['POST'])
def stop_autonomous():
    """Disable autonomous mode"""
    if not agent:
        return error_response("Agent not available", 503)
    agent.disable_autonomous_mode()
    return success_response({"autonomous": False})

@app.route('/agent/workflow/run', methods=['POST'])
def run_workflow():
    """Run a workflow"""
    if not agent:
        return error_response("Agent not available", 503)
    
    data = request.get_json() or {}
    workflow_name = data.get('workflow', '')
    
    if not workflow_name:
        return error_response("Workflow name required")
    
    executor = WorkflowExecutor(agent)
    result = executor.run_workflow(workflow_name)
    return success_response(result)

# ═══════════════════════════════════════════════════════════════════════════════════
# DEVELOPER ASSISTANT
# ═══════════════════════════════════════════════════════════════════════════════════

@app.route('/dev/generate', methods=['POST'])
def generate_code():
    """Generate code"""
    if not dev_assistant:
        return error_response("Dev assistant not available", 503)
    
    data = request.get_json() or {}
    task = data.get('task', '')
    language = data.get('language')
    
    if not task:
        return error_response("Task description required")
    
    snippet = dev_assistant.generate_code(task, language)
    return success_response({
        "language": snippet.language,
        "code": snippet.code,
        "description": snippet.description,
        "lines": snippet.lines
    })

@app.route('/dev/explain', methods=['POST'])
def explain_code():
    """Explain code"""
    if not dev_assistant:
        return error_response("Dev assistant not available", 503)
    
    data = request.get_json() or {}
    code = data.get('code', '')
    
    if not code:
        return error_response("Code required")
    
    explanation = dev_assistant.explain_code(code)
    return success_response({"explanation": explanation})

@app.route('/dev/analyze', methods=['POST'])
def analyze_code():
    """Analyze code"""
    if not dev_assistant:
        return error_response("Dev assistant not available", 503)
    
    data = request.get_json() or {}
    code = data.get('code', '')
    language = data.get('language')
    
    if not code:
        return error_response("Code required")
    
    analysis = dev_assistant.analyze_code(code, language)
    return success_response({
        "language": analysis.language,
        "issues": analysis.issues,
        "suggestions": analysis.suggestions,
        "complexity": analysis.complexity,
        "lines": analysis.lines,
        "functions": analysis.functions
    })

@app.route('/dev/fix', methods=['POST'])
def fix_error():
    """Get fix suggestions for error"""
    if not dev_assistant:
        return error_response("Dev assistant not available", 503)
    
    data = request.get_json() or {}
    error = data.get('error', '')
    language = data.get('language', 'python')
    
    if not error:
        return error_response("Error message required")
    
    fixes = dev_assistant.fix_common_errors(error, language)
    return success_response({"suggestions": fixes})

@app.route('/dev/readme', methods=['POST'])
def generate_readme():
    """Generate README"""
    if not dev_assistant:
        return error_response("Dev assistant not available", 503)
    
    data = request.get_json() or {}
    project_name = data.get('name', 'My Project')
    description = data.get('description', '')
    language = data.get('language', 'python')
    
    readme = dev_assistant.generate_readme(project_name, description, language)
    return success_response({"readme": readme})

# ═══════════════════════════════════════════════════════════════════════════════════
# VOICE
# ═══════════════════════════════════════════════════════════════════════════════════

@app.route('/voice/status', methods=['GET'])
def voice_status():
    """Get voice status"""
    if not voice_engine:
        return error_response("Voice not available", 503)
    
    return success_response({
        "available": voice_engine.is_available,
        "state": voice_engine.state.value,
        "config": {
            "language": voice_engine.config.language,
            "rate": voice_engine.config.rate
        }
    })

@app.route('/voice/voices', methods=['GET'])
def list_voices():
    """List available voices"""
    if not voice_engine:
        return error_response("Voice not available", 503)
    return success_response({"voices": voice_engine.get_voices()})

# ═══════════════════════════════════════════════════════════════════════════════════
# EMOTION DETECTION
# ═══════════════════════════════════════════════════════════════════════════════════

@app.route('/emotion/analyze', methods=['POST'])
def analyze_emotion():
    """Analyze emotion from text"""
    if not emotion_detector:
        return error_response("Emotion detector not available", 503)
    
    data = request.get_json() or {}
    text = data.get('text', '')
    
    if not text:
        return error_response("Text required")
    
    emotion = emotion_detector.analyze_text(text)
    
    # Learn from interaction
    if digital_twin:
        digital_twin.learn_from_interaction({
            "type": "emotion",
            "content": text,
            "timestamp": datetime.now(),
            "emotion": emotion.emotion.value
        })
    
    return success_response({
        "emotion": emotion.emotion.value,
        "confidence": emotion.confidence,
        "mood": emotion.mood.value,
        "stress_level": emotion.stress_level.value,
        "energy": emotion.energy,
        "recommendation": emotion_detector.get_recommendation(),
        "factors": emotion.factors
    })

@app.route('/emotion/analyze_voice', methods=['POST'])
def analyze_voice_emotion():
    """Analyze emotion from voice data"""
    if not emotion_detector:
        return error_response("Emotion detector not available", 503)
    
    data = request.get_json() or {}
    
    audio_data = {
        "pitch": data.get('pitch', 150),
        "speed": data.get('speed', 150),
        "pause_frequency": data.get('pause_frequency', 0.1),
        "volume": data.get('volume', 0.5)
    }
    
    emotion = emotion_detector.analyze_voice(audio_data)
    
    return success_response({
        "emotion": emotion.emotion.value,
        "confidence": emotion.confidence,
        "mood": emotion.mood.value,
        "energy": emotion.energy
    })

@app.route('/emotion/current', methods=['GET'])
def current_emotion():
    """Get current detected emotion"""
    if not emotion_detector:
        return error_response("Emotion detector not available", 503)
    
    if emotion_detector.current_emotion:
        e = emotion_detector.current_emotion
        return success_response({
            "emotion": e.emotion.value,
            "confidence": e.confidence,
            "mood": e.mood.value,
            "stress_level": e.stress_level.value,
            "energy": e.energy,
            "recommendation": emotion_detector.get_recommendation()
        })
    
    return success_response({"emotion": "neutral", "confidence": 0.0})

@app.route('/emotion/mood_trend', methods=['GET'])
def mood_trend():
    """Get mood trend over time"""
    if not emotion_detector:
        return error_response("Emotion detector not available", 503)
    
    return success_response({
        "trend": emotion_detector.get_mood_trend()
    })

# ═══════════════════════════════════════════════════════════════════════════════════
# SCREEN UNDERSTANDING
# ═══════════════════════════════════════════════════════════════════════════════════

@app.route('/screen/analyze', methods=['POST'])
def analyze_screen():
    """Analyze screen content"""
    if not screen_understanding:
        return error_response("Screen understanding not available", 503)
    
    data = request.get_json() or {}
    text = data.get('text', '')
    
    if not text:
        return error_response("Text or image data required")
    
    context = screen_understanding.analyze_text_content(text)
    
    return success_response({
        "current_app": context.current_app,
        "activity_type": context.activity_type.value,
        "detected_errors": context.detected_errors,
        "confidence": context.confidence,
        "suggestion": screen_understanding.get_suggestion(context)
    })

@app.route('/screen/detect_errors', methods=['POST'])
def detect_screen_errors():
    """Detect errors in screen text"""
    if not screen_understanding:
        return error_response("Screen understanding not available", 503)
    
    data = request.get_json() or {}
    text = data.get('text', '')
    
    if not text:
        return error_response("Text required")
    
    errors = screen_understanding.detect_errors(text)
    
    return success_response({"errors": errors})

@app.route('/screen/activity_summary', methods=['GET'])
def activity_summary():
    """Get screen activity summary"""
    if not screen_understanding:
        return error_response("Screen understanding not available", 503)
    
    return success_response(screen_understanding.get_activity_summary())

# ═══════════════════════════════════════════════════════════════════════════════════
# DIGITAL TWIN
# ═══════════════════════════════════════════════════════════════════════════════════

@app.route('/twin/learn', methods=['POST'])
def twin_learn():
    """Learn from interaction"""
    if not digital_twin:
        return error_response("Digital Twin not available", 503)
    
    data = request.get_json() or {}
    
    interaction = {
        "type": data.get('type', 'interaction'),
        "content": data.get('content', ''),
        "timestamp": datetime.now(),
        "success": data.get('success', True),
        "duration": data.get('duration', 0),
        "context": data.get('context', {})
    }
    
    digital_twin.learn_from_interaction(interaction)
    
    return success_response({"learned": True})

@app.route('/twin/predict', methods=['GET'])
def twin_predict():
    """Get next action prediction"""
    if not digital_twin:
        return error_response("Digital Twin not available", 503)
    
    prediction = digital_twin.predict_next_action()
    
    return success_response({"prediction": prediction})

@app.route('/twin/summary', methods=['GET'])
def twin_summary():
    """Get digital twin summary"""
    if not digital_twin:
        return error_response("Digital Twin not available", 503)
    
    return success_response(digital_twin.get_summary())

@app.route('/twin/recommendations', methods=['GET'])
def twin_recommendations():
    """Get personalized recommendations"""
    if not digital_twin:
        return error_response("Digital Twin not available", 503)
    
    return success_response({"recommendations": digital_twin.get_recommendations()})

@app.route('/twin/habits', methods=['GET'])
def twin_habits():
    """Get detected habits"""
    if not digital_twin:
        return error_response("Digital Twin not available", 503)
    
    habits = [
        {
            "id": h.habit_id,
            "name": h.name,
            "streak": h.streak,
            "completion_rate": h.completion_rate,
            "times_triggered": h.times_triggered
        }
        for h in digital_twin.habits.values()
    ]
    
    return success_response({"habits": habits})

@app.route('/twin/preferences', methods=['GET'])
def twin_preferences():
    """Get learned preferences"""
    if not digital_twin:
        return error_response("Digital Twin not available", 503)
    
    return success_response({"preferences": digital_twin.preferences})

# ═══════════════════════════════════════════════════════════════════════════════════
# CONTEXT ENGINE
# ═══════════════════════════════════════════════════════════════════════════════════

@app.route('/context/update', methods=['POST'])
def update_context():
    """Update context from source"""
    if not context_engine:
        return error_response("Context engine not available", 503)
    
    data = request.get_json() or {}
    source = data.get('source', 'text')
    context_data = data.get('data')
    
    context_engine.update_context(source, context_data)
    
    return success_response({"updated": True})

@app.route('/context/get', methods=['GET'])
def get_context():
    """Get current context"""
    if not context_engine:
        return error_response("Context engine not available", 503)
    
    return success_response(context_engine.get_context())

@app.route('/context/summary', methods=['GET'])
def context_summary():
    """Get context summary"""
    if not context_engine:
        return error_response("Context engine not available", 503)
    
    return success_response({"summary": context_engine.get_context_summary()})

@app.route('/context/project/set', methods=['POST'])
def set_project():
    """Set current project"""
    if not context_engine:
        return error_response("Context engine not available", 503)
    
    data = request.get_json() or {}
    project = data.get('project', '')
    
    if not project:
        return error_response("Project name required")
    
    context_engine.set_project(project)
    
    return success_response({"project": project})

@app.route('/context/project/switch', methods=['POST'])
def switch_project():
    """Switch to different project"""
    if not context_engine:
        return error_response("Context engine not available", 503)
    
    data = request.get_json() or {}
    project = data.get('project', '')
    
    if not project:
        return error_response("Project name required")
    
    context_engine.switch_project(project)
    
    return success_response({"project": project})

@app.route('/context/project/return', methods=['POST'])
def return_project():
    """Return to previous project"""
    if not context_engine:
        return error_response("Context engine not available", 503)
    
    previous = context_engine.return_to_previous_project()
    
    return success_response({"project": previous})

# ═══════════════════════════════════════════════════════════════════════════════════
# PROACTIVE SUGGESTIONS
# ═══════════════════════════════════════════════════════════════════════════════════

@app.route('/suggestions/evaluate', methods=['GET'])
def evaluate_suggestions():
    """Evaluate proactive suggestions"""
    if not proactive_engine:
        return error_response("Proactive engine not available", 503)
    
    context = context_engine.get_context() if context_engine else {}
    suggestions = proactive_engine.evaluate_suggestions(context)
    
    return success_response({"suggestions": suggestions})

@app.route('/suggestions/feedback', methods=['POST'])
def suggestion_feedback():
    """Record suggestion feedback"""
    if not proactive_engine:
        return error_response("Proactive engine not available", 503)
    
    data = request.get_json() or {}
    suggestion = data.get('suggestion', '')
    accepted = data.get('accepted', False)
    
    proactive_engine.record_feedback(suggestion, accepted)
    
    return success_response({"recorded": True})

# ═══════════════════════════════════════════════════════════════════════════════════
# INTEGRATED CHAT (with emotion & context)
# ═══════════════════════════════════════════════════════════════════════════════════

@app.route('/chat/enhanced', methods=['POST'])
def chat_enhanced():
    """Enhanced chat with emotion and context"""
    if not cognitive_system:
        return error_response("Cognitive system not available", 503)
    
    data = request.get_json() or {}
    message = data.get('message', '').strip()
    
    if not message:
        return error_response("Empty message")
    
    # Analyze emotion
    emotion_data = None
    if emotion_detector:
        emotion_data = emotion_detector.analyze_text(message)
    
    # Update context
    if context_engine:
        context_engine.update_context("text", {"message": message, "timestamp": datetime.now()})
    
    # Learn from interaction
    if digital_twin:
        digital_twin.learn_from_interaction({
            "type": "chat",
            "content": message,
            "timestamp": datetime.now(),
            "emotion": emotion_data.emotion.value if emotion_data else "neutral"
        })
    
    # Process with cognitive system
    result = cognitive_system.process(message)
    
    # Add emotion-aware response
    if emotion_data and emotion_detector:
        recommendation = emotion_detector.get_recommendation()
        if recommendation and emotion_data.emotion in [Emotion.STRESSED, Emotion.TIRED, Emotion.FRUSTRATED]:
            result["response"] = recommendation + "\n\n" + result.get("response", "")
    
    # Add proactive suggestions
    if proactive_engine:
        context = context_engine.get_context() if context_engine else {}
        suggestions = proactive_engine.evaluate_suggestions(context)
        if suggestions:
            result["suggestions"] = suggestions
    
    return success_response(result)

# ═══════════════════════════════════════════════════════════════════════════════════
# FRONTEND
# ═══════════════════════════════════════════════════════════════════════════════════

@app.route('/')
def index():
    """Serve main dashboard"""
    return render_template('index.html')

# ═══════════════════════════════════════════════════════════════════════════════════
# MAIN
# ═══════════════════════════════════════════════════════════════════════════════════

def main():
    """Start the server"""
    port = int(os.getenv('PORT', 5000))
    host = os.getenv('HOST', 'localhost')
    
    print("""
    ╔══════════════════════════════════════════════════════════════════════════╗
    ║                                                                      ║
    ║                    02 v1 - COGNITIVE AI ECOSYSTEM                    ║
    ║                                                                      ║
    ║                     "Think. See. Act. Learn."                        ║
    ║                                                                      ║
    ╚══════════════════════════════════════════════════════════════════════════╝
    """)
    
    print(f"\n  Server: http://{host}:{port}")
    print(f"  Dashboard: http://{host}:{port}/")
    print(f"\n  Endpoints:")
    print(f"    POST /chat          - Chat with 02")
    print(f"    POST /memory/store  - Store memory")
    print(f"    GET  /memory/recall - Recall memories")
    print(f"    POST /dev/generate  - Generate code")
    print(f"    GET  /status       - System status")
    print(f"\n  Systems Online:")
    print(f"    {'✓' if cognitive_system else '✗'} Cognitive Engine")
    print(f"    {'✓' if agent else '✗'} Autonomous Agent")
    print(f"    {'✓' if dev_assistant else '✗'} Dev Assistant")
    print(f"    {'✓' if voice_engine else '✗'} Voice Engine")
    print(f"\n{'='*70}\n")
    
    app.run(host=host, port=port, debug=False, threaded=True)

if __name__ == "__main__":
    main()
