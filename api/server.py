"""
============================================================
API SERVER - Flask REST API
============================================================
REST API for CODE: 02 system
"""

import asyncio
from flask import Flask, request, jsonify
from flask_cors import CORS
import logging

app = Flask(__name__)
CORS(app)
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("API")


@app.route('/api/chat', methods=['POST'])
def chat():
    """Main chat endpoint - process user input"""
    data = request.get_json()
    user_input = data.get('message', '')
    
    if not user_input:
        return jsonify({"error": "No message provided"}), 400
    
    # Get CODE: 02 instance
    from core import get_code02
    code02 = get_code02()
    
    # Process in async context
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    result = loop.run_until_complete(code02.process(user_input))
    
    return jsonify(result)


@app.route('/api/think', methods=['POST'])
def think():
    """Reasoning endpoint"""
    data = request.get_json()
    prompt = data.get('prompt', '')
    method = data.get('method', 'deductive')
    
    from core import get_code02
    code02 = get_code02()
    
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    result = loop.run_until_complete(code02.think(prompt, method))
    
    return jsonify(result)


@app.route('/api/status', methods=['GET'])
def status():
    """Get system status"""
    from core import get_code02
    code02 = get_code02()
    
    return jsonify(code02.get_status())


@app.route('/api/memory', methods=['GET'])
def get_memory():
    """Get memory state"""
    from core import get_code02
    code02 = get_code02()
    
    return jsonify({
        "short_term": code02.short_term.to_dict(),
        "long_term_size": len(code02.long_term.interactions)
    })


@app.route('/api/execute', methods=['POST'])
def execute():
    """Execute terminal command"""
    data = request.get_json()
    command = data.get('command', '')
    
    from core.action import ActionExecutor
    executor = ActionExecutor()
    
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    result = loop.run_until_complete(executor.execute_command(command))
    
    return jsonify({
        "success": result.success,
        "output": result.output,
        "error": result.error,
        "exit_code": result.exit_code,
        "duration": result.duration
    })


@app.route('/api/files', methods=['GET', 'POST', 'DELETE'])
def files():
    """File operations"""
    from core.action import ActionExecutor
    executor = ActionExecutor()
    
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    
    if request.method == 'GET':
        path = request.args.get('path', '.')
        result = loop.run_until_complete(executor.list_directory(path))
        return jsonify({
            "success": result.success,
            "output": result.output,
            "error": result.error
        })
    
    elif request.method == 'POST':
        data = request.get_json()
        file_path = data.get('path', '')
        content = data.get('content', '')
        result = loop.run_until_complete(executor.write_file(file_path, content))
        return jsonify({
            "success": result.success,
            "output": result.output,
            "error": result.error
        })
    
    elif request.method == 'DELETE':
        data = request.get_json()
        file_path = data.get('path', '')
        result = loop.run_until_complete(executor.delete_file(file_path))
        return jsonify({
            "success": result.success,
            "output": result.output,
            "error": result.error
        })


@app.route('/api/tools', methods=['GET'])
def get_tools():
    """Get available tools"""
    from core.tools import ToolRegistry
    registry = ToolRegistry()
    
    tools = registry.get_all_tools()
    categories = registry.get_categories()
    
    return jsonify({
        "tools": {
            name: {
                "description": tool.description,
                "category": tool.category
            }
            for name, tool in tools.items()
        },
        "categories": categories
    })


@app.route('/api/agents', methods=['GET'])
def get_agents():
    """Get agent system status"""
    from core.agents import create_agent_system
    
    # Create/get orchestrator
    if not hasattr(app, 'agent_system'):
        app.agent_system = create_agent_system()
    
    return jsonify(app.agent_system.get_status())


@app.route('/api/voice/speak', methods=['POST'])
def voice_speak():
    """Text-to-speech endpoint"""
    data = request.get_json()
    text = data.get('text', '')
    
    from core.voice import VoiceEngine
    voice = VoiceEngine()
    
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    success = loop.run_until_complete(voice.speak(text))
    
    return jsonify({"success": success})


@app.route('/api/voice/listen', methods=['POST'])
def voice_listen():
    """Speech recognition endpoint"""
    from core.voice import VoiceEngine
    voice = VoiceEngine()
    
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    text = loop.run_until_complete(voice.listen())
    
    return jsonify({"text": text, "success": text is not None})


@app.route('/api/performance', methods=['GET'])
def performance():
    """Get learning/performance report"""
    from core import get_code02
    code02 = get_code02()
    
    return jsonify(code02.learning.get_performance_report())


@app.route('/api/history', methods=['GET'])
def history():
    """Get interaction history"""
    from core import get_code02
    code02 = get_code02()
    
    return jsonify({
        "recent": code02.long_term.get_recent_interactions(10)
    })


def run_server(host='0.0.0.0', port=5000):
    """Run the API server"""
    app.run(host=host, port=port, debug=True, threaded=True)


if __name__ == '__main__':
    run_server()
