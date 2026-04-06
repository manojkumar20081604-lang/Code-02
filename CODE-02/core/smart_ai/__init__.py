"""
============================================================
UNIFIED INTELLIGENT MAIN LOOP
============================================================
Integrates: Cybersecurity + DataScience + Automation + Installer
Smart decision flow: Input → Classify → Security Check → Route → Execute
"""

import asyncio
import logging
import sys
import os
from datetime import datetime
from typing import Dict, Any, Optional, Callable, List
from dataclasses import dataclass
import json

# Setup paths
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from core.platform import detect, get_os
from core.automation import get_automation, SafetyLevel, BaseAutomation
from core.installer import get_installer, BaseInstaller
from core.cybersecurity import get_security, CybersecurityModule, ThreatLevel
from core.datascience import get_router, get_classifier, get_collector

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(name)s: %(message)s'
)
logger = logging.getLogger("SmartAI")


class SmartAI:
    """
    Smart AI System with:
    - ML-based intent classification
    - Security checks
    - Auto-installation
    - Intelligent routing
    - Data collection for learning
    """
    
    def __init__(self):
        self.name = "CODE-02"
        self.version = "3.0"
        self.running = False
        self.start_time = datetime.now()
        
        # OS Detection
        self.os_info = get_os()
        
        # Initialize modules
        self.automation = get_automation(SafetyLevel.SAFE)
        self.installer = get_installer()
        self.security = get_security()
        self.router = get_router()
        self.classifier = get_classifier()
        self.collector = get_collector()
        
        # Context
        self.context: Dict[str, Any] = {}
        self.conversation_history: List[Dict] = []
        self.system_logs: List[Dict] = []
        
        logger.info(f"{self.name} v{self.version} initialized")
        logger.info(f"Platform: {self.os_info}")
    
    def _log(self, level: str, source: str, message: str):
        """Log system event"""
        entry = {
            "timestamp": datetime.now().isoformat(),
            "level": level,
            "source": source,
            "message": message
        }
        self.system_logs.append(entry)
        if len(self.system_logs) > 500:
            self.system_logs = self.system_logs[-500:]
    
    # ================================================================
    # SMART PROCESSING PIPELINE
    # ================================================================
    
    async def process(self, user_input: str) -> Dict[str, Any]:
        """
        Smart processing pipeline:
        1. Classify intent (ML-based)
        2. Security check
        3. Extract entities
        4. Route to module
        5. Execute action
        6. Collect data
        """
        
        self._log("INFO", "Pipeline", f"Processing: {user_input[:50]}...")
        
        # Step 1: Classify intent
        routing = self.router.route(user_input)
        intent = routing['intent']
        confidence = routing['confidence']
        entities = routing['entities']
        
        self._log("INFO", "Classifier", f"Intent: {intent} (confidence: {confidence:.2f})")
        
        # Step 2: Security check
        security_result = await self._security_check(user_input, routing)
        
        if not security_result['safe']:
            self._log("WARNING", "Security", f"Threat detected: {security_result['threat_level']}")
            return {
                "success": False,
                "error": f"Security blocked: {security_result['message']}",
                "intent": intent,
                "security": security_result
            }
        
        # Step 3: Auto-install if needed
        if intent == 'install' and 'packages' in entities:
            await self._auto_install(entities['packages'])
        
        # Step 4: Execute based on routing
        result = await self._execute(routing, entities)
        
        # Step 5: Collect data
        self.collector.log_interaction(
            user_input, intent, confidence, entities, result
        )
        
        return result
    
    async def _security_check(self, user_input: str, routing: Dict) -> Dict[str, Any]:
        """Perform security checks"""
        
        intent = routing['intent']
        entities = routing['entities']
        
        # Check command safety
        if intent == 'command':
            cmd = routing['entities'].get('command', user_input)
            cmd_check = self.security.check_command_safety(cmd)
            
            if cmd_check.threat_level in [ThreatLevel.HIGH, ThreatLevel.CRITICAL]:
                return {
                    "safe": False,
                    "threat_level": cmd_check.threat_level.value,
                    "message": cmd_check.recommendation,
                    "indicators": cmd_check.indicators
                }
        
        # Check URL safety
        if 'url' in entities:
            url_check = self.security.check_url_safety(entities['url'])
            
            if not url_check['safe']:
                return {
                    "safe": False,
                    "threat_level": url_check['threat_level'],
                    "message": url_check['recommendation'],
                    "indicators": url_check['indicators']
                }
        
        # Check for security scan intent (on local network only)
        if intent == 'security_scan':
            if 'ip' in entities:
                ip = entities['ip']
                # Block external IPs
                if not ip.startswith(('192.168', '10.', '172.')):
                    return {
                        "safe": False,
                        "threat_level": "high",
                        "message": "External IP scanning blocked. Only local network allowed.",
                        "indicators": ["External IP address"]
                    }
        
        return {"safe": True, "threat_level": "safe"}
    
    async def _auto_install(self, packages: List[str]) -> Dict[str, Any]:
        """Auto-install missing packages"""
        
        results = []
        
        for package in packages:
            self._log("INFO", "Installer", f"Auto-installing: {package}")
            result = self.installer.install(package)
            results.append({
                "package": package,
                "success": result.success,
                "manager": result.manager
            })
        
        return {"install_results": results}
    
    async def _execute(self, routing: Dict, entities: Dict) -> Dict[str, Any]:
        """Execute action based on routing"""
        
        intent = routing['intent']
        module = routing['module']
        
        if module == 'automation':
            return await self._handle_automation(intent, entities)
        elif module == 'installer':
            return await self._handle_install(intent, entities)
        elif module == 'security':
            return await self._handle_security(intent, entities)
        elif module == 'brain':
            return await self._handle_brain(intent, entities)
        else:
            return await self._handle_chat(intent, entities)
    
    async def _handle_automation(self, intent: str, entities: Dict) -> Dict[str, Any]:
        """Handle automation commands"""
        
        # Execute command
        if intent == 'command':
            cmd = entities.get('command', self.context.get('last_input', ''))
            result = self.automation.execute(cmd)
            
            return {
                "success": result.success,
                "output": result.stdout,
                "error": result.stderr if not result.success else None,
                "module": "automation",
                "exit_code": result.exit_code
            }
        
        # Network operations
        if intent == 'network':
            if 'url' in entities:
                result = self.automation.execute(f"curl -I {entities['url']}")
                return {
                    "success": result.success,
                    "output": result.stdout,
                    "module": "automation"
                }
        
        return {
            "success": True,
            "output": "Automation complete",
            "module": "automation"
        }
    
    async def _handle_install(self, intent: str, entities: Dict) -> Dict[str, Any]:
        """Handle package installation"""
        
        packages = entities.get('packages', [])
        
        if not packages:
            return {
                "success": False,
                "error": "No package specified",
                "module": "installer"
            }
        
        results = []
        for package in packages:
            result = self.installer.install(package)
            results.append({
                "package": package,
                "success": result.success,
                "manager": result.manager
            })
        
        all_success = all(r['success'] for r in results)
        
        return {
            "success": all_success,
            "results": results,
            "module": "installer"
        }
    
    async def _handle_security(self, intent: str, entities: Dict) -> Dict[str, Any]:
        """Handle security operations"""
        
        results = {}
        
        # Port scan
        if 'ip' in entities and 'port' in entities:
            result = self.security.scan_port(entities['ip'], entities['port'])
            results['port_scan'] = {
                "port": result.port,
                "status": result.status,
                "service": result.service,
                "threat_level": result.threat_level.value
            }
        elif 'ip' in entities:
            scan_results = self.security.scan_common_ports(entities['ip'])
            results['port_scan'] = {
                "total_scanned": len(scan_results),
                "open_ports": [
                    {"port": r.port, "service": r.service}
                    for r in scan_results if r.status == "open"
                ]
            }
        
        # URL check
        if 'url' in entities:
            results['url_check'] = self.security.check_url_safety(entities['url'])
        
        return {
            "success": True,
            "results": results,
            "module": "security"
        }
    
    async def _handle_brain(self, intent: str, entities: Dict) -> Dict[str, Any]:
        """Handle brain/intelligence operations"""
        
        if intent == 'think':
            problem = self.context.get('last_input', 'No problem specified')
            reasoning = self._simple_reasoning(problem)
            return {
                "success": True,
                "output": reasoning,
                "module": "brain"
            }
        
        if intent == 'help':
            return {
                "success": True,
                "output": self._get_help_text(),
                "module": "brain"
            }
        
        return await self._handle_chat(intent, entities)
    
    async def _handle_chat(self, intent: str, entities: Dict) -> Dict[str, Any]:
        """Handle general chat"""
        
        responses = [
            "I understand. How can I help you accomplish this task?",
            "Got it! Let me help you with that.",
            "I'm here to assist. What would you like to do?",
            "Understood. Ready to help!"
        ]
        
        import time
        response = responses[int(time.time()) % len(responses)]
        
        return {
            "success": True,
            "output": response,
            "module": "brain"
        }
    
    # ================================================================
    # HELPER METHODS
    # ================================================================
    
    def _simple_reasoning(self, problem: str) -> str:
        """Simple reasoning (placeholder for LLM)"""
        
        return f"""
Analysis: "{problem}"

Step 1: Understanding
- Breaking down the problem into components

Step 2: Analysis
- Identifying key factors and relationships

Step 3: Reasoning
- Drawing logical conclusions

Step 4: Recommendation
- Suggested approach based on analysis

Note: Connect an LLM (Ollama/OpenAI) for advanced reasoning.
"""
    
    def _get_help_text(self) -> str:
        """Get help text"""
        return """
CODE-02 Smart AI Commands:
=========================

AUTOMATION:
  <shell command>        Execute a shell command
  ls, cd, cat, grep      Standard Linux commands

INSTALLATION:
  install <package>       Install a package
  pip install flask      Install Python package
  npm install react      Install Node package

SECURITY:
  scan <ip>              Scan IP for open ports
  check <url>           Check URL for threats
  security <command>    Security operations

SYSTEM:
  status                Show system status
  sysinfo               System information

INTELLIGENCE:
  think <problem>       Deep analysis
  help                  Show this help
"""
    
    def get_status(self) -> Dict[str, Any]:
        """Get system status"""
        return {
            "name": self.name,
            "version": self.version,
            "platform": str(self.os_info),
            "uptime_seconds": (datetime.now() - self.start_time).total_seconds(),
            "security": {
                "threats_detected": len(self.security.threat_log),
                "scans_performed": len(self.security.scan_history)
            },
            "ml": self.router.get_statistics()
        }
    
    # ================================================================
    # MAIN LOOP
    # ================================================================
    
    async def run(self):
        """Main execution loop"""
        
        self.running = True
        
        print("=" * 60)
        print(f"  {self.name} v{self.version} - Smart AI System")
        print("=" * 60)
        print(f"  Platform: {self.os_info}")
        print(f"  ML Classifier: Active")
        print(f"  Security Module: Active")
        print("=" * 60)
        print()
        print("Type 'help' for commands, 'exit' to quit")
        print()
        
        self._log("INFO", "System", f"{self.name} started")
        
        while self.running:
            try:
                # Get input
                user_input = input(f"{self.name}> ").strip()
                
                if not user_input or user_input.lower() in ["exit", "quit", "bye"]:
                    break
                
                if not user_input.strip():
                    continue
                
                # Special commands
                if user_input.lower() == "help":
                    print(self._get_help_text())
                    continue
                
                if user_input.lower() == "status":
                    print(json.dumps(self.get_status(), indent=2))
                    continue
                
                # Process
                result = await self.process(user_input)
                
                # Output
                if result.get("success"):
                    if result.get("output"):
                        print(result["output"])
                    if result.get("results"):
                        print(json.dumps(result["results"], indent=2))
                else:
                    error = result.get("error", "Unknown error")
                    print(f"Error: {error}")
                    
                    # Show security info if blocked
                    if "security" in result:
                        sec = result["security"]
                        if "indicators" in sec:
                            print(f"Threat indicators: {', '.join(sec['indicators'])}")
                
            except KeyboardInterrupt:
                print("\n(Use 'exit' to quit)")
                continue
            except EOFError:
                break
            except Exception as e:
                self._log("ERROR", "MainLoop", str(e))
                print(f"Error: {e}")
        
        self._log("INFO", "System", f"{self.name} stopped")
        self.running = False


async def main():
    """Entry point"""
    ai = SmartAI()
    await ai.run()


if __name__ == "__main__":
    asyncio.run(main())
