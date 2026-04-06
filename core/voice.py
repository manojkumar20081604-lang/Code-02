"""
02 v1 - Voice Engine
Speech Recognition and Text-to-Speech integration
"""

import os
import json
import logging
from typing import Dict, List, Optional, Callable, Any
from dataclasses import dataclass
from enum import Enum

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("02-Voice")

class VoiceState(Enum):
    IDLE = "idle"
    LISTENING = "listening"
    PROCESSING = "processing"
    SPEAKING = "speaking"

@dataclass
class VoiceConfig:
    language: str = "en-US"
    rate: float = 1.0
    pitch: float = 1.0
    volume: float = 1.0
    voice: Optional[str] = None
    continuous: bool = True
    interim_results: bool = True

class VoiceEngine:
    """
    Voice Engine - Handles speech recognition and synthesis.
    
    For browser environment, uses Web Speech API.
    For Python environment, provides a mock/stub for integration.
    """
    
    def __init__(self, config: VoiceConfig = None):
        self.config = config or VoiceConfig()
        self.state = VoiceState.IDLE
        self.recognition = None
        self.synthesis = None
        self.is_available = False
        
        # Callbacks
        self.on_transcript: Optional[Callable] = None
        self.on_interim: Optional[Callable] = None
        self.on_start: Optional[Callable] = None
        self.on_end: Optional[Callable] = None
        self.on_error: Optional[Callable] = None
        
        logger.info("Voice Engine initialized")
    
    def check_availability(self) -> bool:
        """Check if voice features are available"""
        # In browser, this would check window.SpeechRecognition
        # For server-side, return False
        self.is_available = False
        return False
    
    def init_browser_recognition(self):
        """Initialize browser-based speech recognition"""
        try:
            # This is called from frontend JavaScript
            self.recognition = {
                "continuous": self.config.continuous,
                "interimResults": self.config.interim_results,
                "lang": self.config.language
            }
            self.is_available = True
            logger.info("Browser speech recognition ready")
        except Exception as e:
            logger.error(f"Failed to init recognition: {e}")
    
    def get_voices(self) -> List[Dict]:
        """Get available TTS voices"""
        # Browser voices would be fetched here
        return [
            {"name": "Google US English", "lang": "en-US", "default": True},
            {"name": "Microsoft David", "lang": "en-US", "default": False},
            {"name": "Microsoft Zira", "lang": "en-US", "default": False},
        ]
    
    def speak(self, text: str, voice_name: str = None) -> bool:
        """Speak text using TTS"""
        if not text:
            return False
        
        self.state = VoiceState.SPEAKING
        logger.info(f"Speaking: {text[:50]}...")
        
        # This is handled by frontend JavaScript
        # Server just logs the intent
        return True
    
    def stop_speaking(self):
        """Stop current speech"""
        self.state = VoiceState.IDLE
        logger.info("Speech stopped")
    
    def start_listening(self) -> bool:
        """Start speech recognition"""
        if self.state == VoiceState.LISTENING:
            return False
        
        self.state = VoiceState.LISTENING
        logger.info("Started listening")
        return True
    
    def stop_listening(self) -> bool:
        """Stop speech recognition"""
        if self.state != VoiceState.LISTENING:
            return False
        
        self.state = VoiceState.IDLE
        logger.info("Stopped listening")
        return True
    
    def toggle_listening(self) -> bool:
        """Toggle listening state"""
        if self.state == VoiceState.LISTENING:
            return self.stop_listening()
        return self.start_listening()


class VoiceCommandParser:
    """
    Voice Command Parser - Parses voice input into structured commands.
    """
    
    def __init__(self):
        self.wake_words = ["zero two", "02", "jarvis", "hey assistant"]
        self.commands = {}
        
    def register_command(self, pattern: str, handler: Callable):
        """Register a voice command pattern"""
        self.commands[pattern] = handler
    
    def parse(self, text: str) -> Dict:
        """Parse voice input into command and args"""
        text_lower = text.lower().strip()
        
        # Check for wake word
        wake_detected = None
        for wake in self.wake_words:
            if wake in text_lower:
                wake_detected = wake
                # Remove wake word
                text_lower = text_lower.replace(wake, "").strip()
                break
        
        if not wake_detected:
            return {
                "valid": False,
                "reason": "No wake word detected"
            }
        
        # Parse command
        words = text_lower.split()
        if not words:
            return {"valid": True, "command": "status", "args": []}
        
        # Common commands
        command_map = {
            "hello": "greet",
            "hi": "greet",
            "help": "help",
            "status": "status",
            "stop": "stop",
            "listen": "listen",
            "speak": "speak",
            "remember": "remember",
            "what": "query",
            "how": "query",
            "why": "query",
            "write": "code",
            "code": "code",
            "run": "execute",
            "execute": "execute",
            "analyze": "analyze",
            "search": "search",
            "find": "search",
        }
        
        cmd = words[0]
        command = command_map.get(cmd, "unknown")
        args = words[1:] if len(words) > 1 else []
        
        return {
            "valid": True,
            "wake_word": wake_detected,
            "command": command,
            "args": args,
            "raw": text
        }
    
    def format_response(self, response: str) -> str:
        """Format response for voice output"""
        # Remove markdown formatting
        response = response.replace("**", "").replace("*", "")
        response = response.replace("#", "").replace("- ", "")
        
        # Limit length for TTS
        if len(response) > 500:
            response = response[:500] + "..."
        
        return response


class VoiceServer:
    """
    Voice Server - Flask server for voice integration.
    Can be called from frontend for advanced voice features.
    """
    
    def __init__(self, voice_engine: VoiceEngine):
        self.engine = voice_engine
        self.parser = VoiceCommandParser()
    
    def get_routes(self):
        """Get Flask routes for voice endpoints"""
        from flask import Flask, request, jsonify
        
        app = Flask(__name__)
        
        @app.route('/voice/status', methods=['GET'])
        def status():
            return jsonify({
                "available": self.engine.is_available,
                "state": self.engine.state.value,
                "voices": self.engine.get_voices()
            })
        
        @app.route('/voice/config', methods=['POST'])
        def configure():
            data = request.get_json() or {}
            self.engine.config = VoiceConfig(**data)
            return jsonify({"success": True})
        
        @app.route('/voice/voices', methods=['GET'])
        def voices():
            return jsonify({"voices": self.engine.get_voices()})
        
        @app.route('/voice/parse', methods=['POST'])
        def parse():
            data = request.get_json() or {}
            text = data.get('text', '')
            result = self.parser.parse(text)
            return jsonify(result)
        
        return app


# Frontend JavaScript integration
VOICE_FRONTEND_JS = """
// 02 Voice Integration for Browser

class Voice02 {
    constructor(config = {}) {
        this.config = {
            language: config.language || 'en-US',
            continuous: config.continuous !== false,
            interimResults: config.interimResults !== false,
            wakeWords: config.wakeWords || ['zero two', '02', 'jarvis'],
            onTranscript: config.onTranscript || (() => {}),
            onInterim: config.onInterim || (() => {}),
            onStart: config.onStart || (() => {}),
            onEnd: config.onEnd || (() => {}),
            onError: config.onError || (() => {})
        };
        
        this.recognition = null;
        this.synthesis = window.speechSynthesis;
        this.isListening = false;
        this.wakeWordDetected = false;
        
        this.initRecognition();
    }
    
    initRecognition() {
        const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
        if (!SpeechRecognition) {
            console.warn('Speech recognition not supported');
            return;
        }
        
        this.recognition = new SpeechRecognition();
        this.recognition.continuous = this.config.continuous;
        this.recognition.interimResults = this.config.interimResults;
        this.recognition.lang = this.config.language;
        
        this.recognition.onstart = () => {
            this.isListening = true;
            this.config.onStart();
        };
        
        this.recognition.onresult = (event) => {
            let final = '';
            let interim = '';
            
            for (let i = event.resultIndex; i < event.results.length; i++) {
                const transcript = event.results[i][0].transcript;
                if (event.results[i].isFinal) {
                    final += transcript;
                } else {
                    interim += transcript;
                }
            }
            
            if (final) {
                // Check for wake word
                const hasWake = this.config.wakeWords.some(
                    wake => final.toLowerCase().includes(wake)
                );
                
                if (hasWake) {
                    this.wakeWordDetected = true;
                    const command = this.extractCommand(final);
                    this.config.onTranscript(command);
                }
            }
            
            if (interim) {
                this.config.onInterim(interim);
            }
        };
        
        this.recognition.onend = () => {
            this.isListening = false;
            this.config.onEnd();
            
            // Restart if continuous mode
            if (this.config.continuous && this.isListening) {
                this.start();
            }
        };
        
        this.recognition.onerror = (event) => {
            this.config.onError(event.error);
        };
    }
    
    extractCommand(text) {
        const lower = text.toLowerCase();
        for (const wake of this.config.wakeWords) {
            if (lower.includes(wake)) {
                return lower.split(wake)[1].trim();
            }
        }
        return text;
    }
    
    start() {
        if (this.recognition && !this.isListening) {
            this.recognition.start();
        }
    }
    
    stop() {
        if (this.recognition && this.isListening) {
            this.recognition.stop();
        }
    }
    
    toggle() {
        if (this.isListening) {
            this.stop();
        } else {
            this.start();
        }
    }
    
    speak(text, options = {}) {
        return new Promise((resolve, reject) => {
            const utterance = new SpeechSynthesisUtterance(text);
            
            utterance.rate = options.rate || 1.0;
            utterance.pitch = options.pitch || 1.0;
            utterance.volume = options.volume || 1.0;
            
            // Find preferred voice
            if (options.voice) {
                const voice = this.synthesis.getVoices().find(
                    v => v.name.includes(options.voice)
                );
                if (voice) utterance.voice = voice;
            }
            
            utterance.onend = resolve;
            utterance.onerror = reject;
            
            this.synthesis.speak(utterance);
        });
    }
    
    stopSpeaking() {
        this.synthesis.cancel();
    }
    
    getVoices() {
        return this.synthesis.getVoices();
    }
}

// Export for use
if (typeof module !== 'undefined' && module.exports) {
    module.exports = Voice02;
}
"""

__all__ = ['VoiceEngine', 'VoiceConfig', 'VoiceState', 'VoiceCommandParser', 'VoiceServer', 'VOICE_FRONTEND_JS']
