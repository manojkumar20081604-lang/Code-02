"""
02 Ultra - Flask API Server
Level 5 Cognitive Autonomous AI System
"""

import os
import sys
import json
import asyncio
import logging
from datetime import datetime
from functools import wraps
from flask import Flask, request, jsonify, render_template
from flask_cors import CORS

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s'
)
logger = logging.getLogger("02-Ultra-Server")

app = Flask(__name__, static_folder='../frontend', template_folder='../frontend')
CORS(app)

# Initialize Ultra System
ultra_system = None

def initialize_ultra():
    global ultra_system
    try:
        from ultra.core import System02Ultra
        ultra_system = System02Ultra()
        ultra_system.start()
        logger.info("02 Ultra System initialized")
    except Exception as e:
        logger.error(f"Ultra init failed: {e}")
        ultra_system = None

initialize_ultra()

# ═══════════════════════════════════════════════════════════════════════════════════
# HELPERS
# ═══════════════════════════════════════════════════════════════════════════════════

def success(data=None, message="OK"):
    return jsonify({"success": True, "data": data, "message": message})

def error_response(message, code=400):
    return jsonify({"success": False, "error": message}), code

def require_ultra(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        if not ultra_system:
            return error_response("02 Ultra not available", 503)
        return f(*args, **kwargs)
    return wrapper

# ═══════════════════════════════════════════════════════════════════════════════════
# HEALTH & STATUS
# ═══════════════════════════════════════════════════════════════════════════════════

@app.route('/health', methods=['GET'])
def health():
    """Health check"""
    return jsonify({
        "status": "online",
        "name": "02 Ultra",
        "level": 5,
        "version": "1.0.0",
        "ultra_available": ultra_system is not None,
        "timestamp": datetime.now().isoformat()
    })

@app.route('/status', methods=['GET'])
@require_ultra
def status():
    """Get full system status"""
    return success(ultra_system.get_status())

# ═══════════════════════════════════════════════════════════════════════════════════
# MAIN PROCESSING
# ═══════════════════════════════════════════════════════════════════════════════════

@app.route('/process', methods=['POST'])
@require_ultra
async def process():
    """Main processing endpoint - handles any request through the complete AI system"""
    data = request.get_json() or {}
    user_input = data.get('message', '').strip()
    
    if not user_input:
        return error_response("Empty message")
    
    try:
        result = await ultra_system.process(user_input)
        return success(result)
    except Exception as e:
        logger.error(f"Process error: {e}")
        return error_response(str(e))

@app.route('/chat', methods=['POST'])
@require_ultra
async def chat():
    """Chat endpoint"""
    data = request.get_json() or {}
    message = data.get('message', '').strip()
    
    if not message:
        return error_response("Empty message")
    
    try:
        result = await ultra_system.process(message)
        return success({
            "response": result.get("result", {}).get("response", "Processed"),
            "thought": result.get("thought"),
            "action": result.get("action"),
            "reflection": result.get("reflection", {})
        })
    except Exception as e:
        logger.error(f"Chat error: {e}")
        return error_response(str(e))

# ═══════════════════════════════════════════════════════════════════════════════════
# RECURSIVE AGENTS
# ═══════════════════════════════════════════════════════════════════════════════════

@app.route('/agents/spawn', methods=['POST'])
@require_ultra
def spawn_agent():
    """Spawn a new sub-agent"""
    data = request.get_json() or {}
    name = data.get('name', 'agent')
    task = data.get('task', '')
    agent_type = data.get('type', 'planner')
    
    if not task:
        return error_response("Task required")
    
    agent = ultra_system.recursive_agents.spawn_agent(name, task, agent_type=agent_type)
    return success({
        "id": agent.id,
        "name": agent.name,
        "state": agent.state.value
    })

@app.route('/agents/tree', methods=['GET'])
@require_ultra
def get_agent_tree():
    """Get agent tree structure"""
    root_id = request.args.get('root_id')
    tree = ultra_system.recursive_agents.get_agent_tree(root_id)
    return success(tree)

@app.route('/agents/kill', methods=['POST'])
@require_ultra
def kill_agent():
    """Kill an agent"""
    data = request.get_json() or {}
    agent_id = data.get('id', '')
    
    if not agent_id:
        return error_response("Agent ID required")
    
    success = ultra_system.recursive_agents.kill_agent(agent_id)
    return success({"killed": success})

# ═══════════════════════════════════════════════════════════════════════════════════
# WORLD MODEL
# ═══════════════════════════════════════════════════════════════════════════════════

@app.route('/world/entity/add', methods=['POST'])
@require_ultra
def add_entity():
    """Add entity to world model"""
    data = request.get_json() or {}
    name = data.get('name', '')
    entity_type = data.get('type', 'concept').upper()
    properties = data.get('properties', {})
    
    if not name:
        return error_response("Name required")
    
    from ultra.core import EntityType
    et = EntityType[entity_type] if entity_type in [e.name for e in EntityType] else EntityType.CONCEPT
    
    entity = ultra_system.world_model.add_entity(name, et, properties)
    return success({
        "id": entity.id,
        "name": entity.name,
        "type": entity.entity_type.value
    })

@app.route('/world/entity/query', methods=['GET'])
@require_ultra
def query_entities():
    """Query entities"""
    entity_type = request.args.get('type')
    
    from ultra.core import EntityType
    et = None
    if entity_type:
        et = EntityType[entity_type.upper()] if entity_type.upper() in [e.name for e in EntityType] else None
    
    entities = ultra_system.world_model.query(entity_type=et)
    return success({
        "entities": [
            {"id": e.id, "name": e.name, "type": e.entity_type.value, "properties": e.properties}
            for e in entities
        ],
        "count": len(entities)
    })

@app.route('/world/entity/<entity_id>', methods=['GET'])
@require_ultra
def get_entity_context(entity_id):
    """Get entity context"""
    context = ultra_system.world_model.get_entity_context(entity_id)
    return success(context)

@app.route('/world/relate', methods=['POST'])
@require_ultra
def relate_entities():
    """Create relationship between entities"""
    data = request.get_json() or {}
    entity1 = data.get('entity1', '')
    entity2 = data.get('entity2', '')
    relationship = data.get('relationship', 'related_to')
    
    if not entity1 or not entity2:
        return error_response("Both entity IDs required")
    
    ultra_system.world_model.relate(entity1, entity2, relationship)
    return success({"related": True})

@app.route('/world/summary', methods=['GET'])
@require_ultra
def world_summary():
    """Get world model summary"""
    return success(ultra_system.world_model.get_world_summary())

# ═══════════════════════════════════════════════════════════════════════════════════
# GOALS
# ═══════════════════════════════════════════════════════════════════════════════════

@app.route('/goals/create', methods=['POST'])
@require_ultra
def create_goal():
    """Create evolutionary goal"""
    data = request.get_json() or {}
    description = data.get('description', '')
    priority = data.get('priority', 'MEDIUM')
    
    if not description:
        return error_response("Description required")
    
    from ultra.core import TaskPriority
    p = TaskPriority[priority.upper()] if priority.upper() in [t.name for t in TaskPriority] else TaskPriority.MEDIUM
    
    goal = ultra_system.goal_evolution.create_evolutionary_goal(description, p)
    sub_goals = ultra_system.goal_evolution.decompose_goal(goal.id)
    
    return success({
        "id": goal.id,
        "description": goal.description,
        "original": goal.original_description,
        "priority": goal.priority.value,
        "sub_goals": [{"id": sg.id, "description": sg.description} for sg in sub_goals]
    })

@app.route('/goals/evolve', methods=['POST'])
@require_ultra
def evolve_goal():
    """Evolve a goal"""
    data = request.get_json() or {}
    goal_id = data.get('id', '')
    feedback = data.get('feedback')
    
    if not goal_id:
        return error_response("Goal ID required")
    
    goal = ultra_system.goal_evolution.evolve_goal(goal_id, feedback)
    if not goal:
        return error_response("Goal not found")
    
    return success({
        "id": goal.id,
        "description": goal.description,
        "evolution_history": goal.evolution_history
    })

@app.route('/goals/progress', methods=['POST'])
@require_ultra
def update_goal_progress():
    """Update goal progress"""
    data = request.get_json() or {}
    goal_id = data.get('id', '')
    progress = data.get('progress', 0.0)
    
    if not goal_id:
        return error_response("Goal ID required")
    
    ultra_system.goal_evolution.update_progress(goal_id, progress)
    return success({"updated": True})

@app.route('/goals/summary', methods=['GET'])
@require_ultra
def goals_summary():
    """Get goals summary"""
    return success(ultra_system.goal_evolution.get_goals_summary())

# ═══════════════════════════════════════════════════════════════════════════════════
# PROJECT BUILDER
# ═══════════════════════════════════════════════════════════════════════════════════

@app.route('/project/build', methods=['POST'])
@require_ultra
async def build_project():
    """Build a project autonomously"""
    data = request.get_json() or {}
    description = data.get('description', '')
    
    if not description:
        return error_response("Description required")
    
    try:
        result = await ultra_system.project_builder.build_project(description)
        return success(result)
    except Exception as e:
        logger.error(f"Build error: {e}")
        return error_response(str(e))

# ═══════════════════════════════════════════════════════════════════════════════════
# META INTELLIGENCE
# ═══════════════════════════════════════════════════════════════════════════════════

@app.route('/meta/think', methods=['POST'])
@require_ultra
def meta_think():
    """Think about a situation"""
    data = request.get_json() or {}
    situation = data.get('situation', '')
    
    if not situation:
        return error_response("Situation required")
    
    thought = ultra_system.meta_intelligence.think(situation)
    return success(thought.to_dict() if hasattr(thought, 'to_dict') else {
        "id": thought.id,
        "content": thought.content,
        "confidence": thought.confidence,
        "reasoning": thought.selected_reasoning
    })

@app.route('/meta/reflect', methods=['GET'])
@require_ultra
def meta_reflect():
    """Self-reflection"""
    reflection = ultra_system.meta_intelligence.reflect()
    return success(reflection)

@app.route('/meta/learn', methods=['POST'])
@require_ultra
def meta_learn():
    """Learn from experience"""
    data = request.get_json() or {}
    
    from ultra.core import Experience
    experience = Experience(
        id=data.get('id', str(datetime.now().timestamp())),
        situation=data.get('situation', ''),
        action=data.get('action', ''),
        outcome=data.get('outcome'),
        success=data.get('success', True),
        timestamp=datetime.now(),
        context=data.get('context', {})
    )
    
    ultra_system.meta_intelligence.learn_from_experience(experience)
    return success({"learned": True})

@app.route('/meta/recommendation', methods=['GET'])
@require_ultra
def meta_recommendation():
    """Get self-improvement recommendation"""
    rec = ultra_system.meta_intelligence.get_recommendation()
    return success({"recommendation": rec})

# ═══════════════════════════════════════════════════════════════════════════════════
# LEARNING
# ═══════════════════════════════════════════════════════════════════════════════════

@app.route('/learning/status', methods=['GET'])
@require_ultra
def learning_status():
    """Get learning status"""
    return success(ultra_system.learning_loop.get_learning_status())

@app.route('/learning/recommendation', methods=['GET'])
@require_ultra
def learning_recommendation():
    """Get learning recommendation"""
    return success({"recommendation": ultra_system.learning_loop.get_recommendation()})

# ═══════════════════════════════════════════════════════════════════════════════════
# FRONTEND
# ═══════════════════════════════════════════════════════════════════════════════════

@app.route('/')
def index():
    """Serve Ultra dashboard"""
    return render_template('ultra.html')

# ═══════════════════════════════════════════════════════════════════════════════════
# MAIN
# ═══════════════════════════════════════════════════════════════════════════════════

def main():
    """Start the server"""
    port = int(os.getenv('PORT', 5000))
    host = os.getenv('HOST', 'localhost')
    
    print("=" * 60)
    print("  02 ULTRA - Level 5 Cognitive Autonomous AI System")
    print("  Think. Plan. Learn. Evolve. Execute. Improve.")
    print("=" * 60)
    
    print(f"\n  Server: http://{host}:{port}")
    print(f"  Dashboard: http://{host}:{port}/")
    print(f"\n  Level 5 Features:")
    print(f"    [+] Meta-Intelligence")
    print(f"    [+] Recursive Agents")
    print(f"    [+] World Model")
    print(f"    [+] Goal Evolution")
    print(f"    [+] Project Builder")
    print(f"    [+] Learning Loop")
    print(f"\n{'='*60}\n")
    
    app.run(host=host, port=port, debug=False, threaded=True)

if __name__ == "__main__":
    main()
