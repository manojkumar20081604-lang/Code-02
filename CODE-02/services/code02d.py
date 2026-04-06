#!/usr/bin/env python3
"""
============================================================
CODE-02 LINUX DAEMON SERVICE
============================================================
Background service for continuous Code-02 operation
"""

import os
import sys
import signal
import time
import socket
import json
import logging
import argparse
from pathlib import Path

# Setup paths
SCRIPT_DIR = Path(__file__).parent.absolute()
sys.path.insert(0, str(SCRIPT_DIR))

# Configuration
DAEMON_NAME = "code02"
DAEMON_VERSION = "2.0.0"
SOCKET_PATH = f"/tmp/code02-{os.getuid()}.sock"
PID_FILE = f"/tmp/code02-{os.getuid()}.pid"
LOG_FILE = f"/tmp/code02-{os.getuid()}.log"

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(LOG_FILE),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(DAEMON_NAME)


class Code02Daemon:
    """Code-02 Daemon - Background service"""
    
    def __init__(self):
        self.running = False
        self.socket = None
        self.pid_file = None
        self.code02 = None
    
    def start(self):
        """Start the daemon"""
        logger.info(f"Starting {DAEMON_NAME} v{DAEMON_VERSION}...")
        
        # Check if already running
        if self._is_running():
            logger.error(f"{DAEMON_NAME} is already running")
            return False
        
        # Fork process
        try:
            pid = os.fork()
            if pid > 0:
                # Parent process
                time.sleep(1)
                if self._is_running():
                    logger.info(f"{DAEMON_NAME} started successfully (PID: {pid})")
                    print(f"Code-02 Daemon started (PID: {pid})")
                return True
        except OSError as e:
            logger.error(f"Fork failed: {e}")
            return False
        
        # Child process (daemon)
        os.setsid()
        os.chdir("/")
        os.umask(0)
        
        # Write PID file
        with open(PID_FILE, "w") as f:
            f.write(str(os.getpid()))
        
        # Setup signal handlers
        signal.signal(signal.SIGTERM, self._signal_handler)
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGHUP, self._signal_handler)
        
        # Main loop
        self._main_loop()
        
        return True
    
    def stop(self):
        """Stop the daemon"""
        logger.info(f"Stopping {DAEMON_NAME}...")
        
        if not self._is_running():
            logger.error(f"{DAEMON_NAME} is not running")
            return False
        
        # Read PID
        try:
            with open(PID_FILE, "r") as f:
                pid = int(f.read().strip())
            
            # Send signal
            os.kill(pid, signal.SIGTERM)
            
            # Wait for shutdown
            for i in range(10):
                if not self._is_running():
                    break
                time.sleep(0.5)
            
            # Clean up
            if os.path.exists(PID_FILE):
                os.remove(PID_FILE)
            if os.path.exists(SOCKET_PATH):
                os.remove(SOCKET_PATH)
            
            logger.info(f"{DAEMON_NAME} stopped")
            print(f"Code-02 Daemon stopped")
            return True
            
        except Exception as e:
            logger.error(f"Failed to stop daemon: {e}")
            return False
    
    def restart(self):
        """Restart the daemon"""
        self.stop()
        time.sleep(1)
        return self.start()
    
    def status(self):
        """Check daemon status"""
        if self._is_running():
            try:
                with open(PID_FILE, "r") as f:
                    pid = f.read().strip()
                print(f"{DAEMON_NAME} is running (PID: {pid})")
                return True
            except:
                pass
        
        print(f"{DAEMON_NAME} is not running")
        return False
    
    def _is_running(self) -> bool:
        """Check if daemon is running"""
        if not os.path.exists(PID_FILE):
            return False
        
        try:
            with open(PID_FILE, "r") as f:
                pid = int(f.read().strip())
            
            # Check if process exists
            os.kill(pid, 0)
            return True
        except:
            return False
    
    def _signal_handler(self, signum, frame):
        """Handle signals"""
        logger.info(f"Received signal {signum}")
        self.running = False
    
    def _main_loop(self):
        """Main daemon loop"""
        self.running = True
        
        # Initialize Code-02
        try:
            from core.main import get_code02_os
            import asyncio
            
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            
            self.code02 = get_code02_os()
            loop.run_until_complete(self.code02.initialize())
            
            logger.info("Code-02 OS initialized")
            
        except Exception as e:
            logger.error(f"Failed to initialize Code-02: {e}")
            return
        
        # Create Unix socket
        if os.path.exists(SOCKET_PATH):
            os.remove(SOCKET_PATH)
        
        self.socket = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        self.socket.bind(SOCKET_PATH)
        self.socket.settimeout(1.0)
        
        # Main loop
        while self.running:
            try:
                self.socket.listen(1)
                
                try:
                    conn, _ = self.socket.accept()
                    self._handle_connection(conn)
                except socket.timeout:
                    continue
                    
            except Exception as e:
                logger.error(f"Socket error: {e}")
                break
        
        # Cleanup
        self._cleanup()
    
    def _handle_connection(self, conn):
        """Handle client connection"""
        try:
            data = conn.recv(4096)
            
            if not data:
                return
            
            request = json.loads(data.decode())
            command = request.get("command")
            args = request.get("args", {})
            
            # Process command
            if command == "status":
                response = self.code02.get_system_status()
            elif command == "process":
                import asyncio
                response = asyncio.get_event_loop().run_until_complete(
                    self.code02.process(args.get("message", ""))
                )
            elif command == "execute":
                import asyncio
                response = asyncio.get_event_loop().run_until_complete(
                    self.code02.execute_task(args.get("task", ""))
                )
            elif command == "think":
                import asyncio
                response = asyncio.get_event_loop().run_until_complete(
                    self.code02.think(args.get("problem", ""))
                )
            else:
                response = {"error": f"Unknown command: {command}"}
            
            conn.send(json.dumps(response).encode())
            
        except Exception as e:
            error = json.dumps({"error": str(e)})
            conn.send(error.encode())
        finally:
            conn.close()
    
    def _cleanup(self):
        """Cleanup resources"""
        logger.info("Cleaning up...")
        
        if self.code02:
            try:
                import asyncio
                loop = asyncio.get_event_loop()
                loop.run_until_complete(self.code02.shutdown())
            except:
                pass
        
        if self.socket:
            self.socket.close()
        
        if os.path.exists(PID_FILE):
            os.remove(PID_FILE)
        
        if os.path.exists(SOCKET_PATH):
            os.remove(SOCKET_PATH)
        
        logger.info("Cleanup complete")


class Code02Client:
    """Client for communicating with Code-02 daemon"""
    
    def __init__(self):
        self.socket_path = SOCKET_PATH
    
    def send_command(self, command: str, args: Dict = None) -> Dict:
        """Send command to daemon"""
        try:
            client = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
            client.connect(self.socket_path)
            
            request = json.dumps({
                "command": command,
                "args": args or {}
            })
            client.send(request.encode())
            
            response = client.recv(8192)
            return json.loads(response.decode())
            
        except Exception as e:
            return {"error": str(e)}
        finally:
            client.close()
    
    def status(self) -> Dict:
        """Get daemon status"""
        return self.send_command("status")
    
    def process(self, message: str) -> Dict:
        """Process message"""
        return self.send_command("process", {"message": message})
    
    def execute(self, task: str) -> Dict:
        """Execute task"""
        return self.send_command("execute", {"task": task})
    
    def think(self, problem: str) -> Dict:
        """Deep thinking"""
        return self.send_command("think", {"problem": problem})


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description="Code-02 AI OS Daemon")
    parser.add_argument("action", choices=["start", "stop", "restart", "status"],
                       help="Action to perform")
    
    args = parser.parse_args()
    
    daemon = Code02Daemon()
    
    if args.action == "start":
        daemon.start()
    elif args.action == "stop":
        daemon.stop()
    elif args.action == "restart":
        daemon.restart()
    elif args.action == "status":
        daemon.status()


if __name__ == "__main__":
    main()
