"""
============================================================
LLM BRAIN - AI Reasoning Engine
============================================================
Local or API-based LLM integration for intelligent reasoning
"""

import asyncio
import json
import os
from typing import Dict, List, Any, Optional, Callable
from dataclasses import dataclass
from enum import Enum
import aiohttp


class LLMProvider(Enum):
    OLLAMA = "ollama"
    OPENAI = "openai"
    ANTHROPIC = "anthropic"
    LOCAL = "local"
    NONE = "none"


@dataclass
class LLMResponse:
    text: str
    model: str
    provider: str
    tokens_used: int
    finish_reason: str
    latency_ms: float
    error: Optional[str] = None


@dataclass
class ConversationMessage:
    role: str  # system, user, assistant
    content: str
    timestamp: float


class LLMBrain:
    """
    LLM-based AI Brain
    - Supports Ollama (local), OpenAI, Anthropic, or mock mode
    - Context window management
    - Streaming responses
    - Tool use / function calling
    """
    
    def __init__(
        self,
        provider: str = "ollama",
        model: str = "llama3.2",
        api_base: str = "http://localhost:11434",
        api_key: str = None,
        max_context: int = 4096
    ):
        self.provider = LLMProvider(provider.lower())
        self.model = model
        self.api_base = api_base
        self.api_key = api_key
        self.max_context = max_context
        
        # Conversation history
        self.conversation: List[ConversationMessage] = []
        self.max_history = 50
        
        # System prompt
        self.system_prompt = self._get_default_system_prompt()
        
        # Callbacks
        self.on_token: Optional[Callable] = None
        self.on_complete: Optional[Callable] = None
    
    def _get_default_system_prompt(self) -> str:
        """Get default system prompt for Code-02"""
        return """You are CODE: 02, an advanced autonomous AI system.

Your capabilities:
- Execute Linux commands and manage the system
- Write, debug, and explain code in any language
- Analyze data and create visualizations
- Search the internet for information
- Manage files, processes, and applications
- Think step-by-step to solve complex problems

When given a task:
1. Understand the goal
2. Break it into actionable steps
3. Execute each step
4. Verify the results
5. Report back with findings

You have access to tools for:
- Command execution
- File operations
- Package installation
- Web search
- Code execution

Be helpful, precise, and proactive. If something fails, try alternative approaches."""
    
    async def initialize(self) -> bool:
        """Initialize LLM connection"""
        
        if self.provider == LLMProvider.OLLAMA:
            return await self._check_ollama()
        elif self.provider == LLMProvider.OPENAI:
            return await self._check_openai()
        elif self.provider == LLMProvider.ANTHROPIC:
            return await self._check_anthropic()
        else:
            # Mock mode - always available
            return True
    
    async def _check_ollama(self) -> bool:
        """Check if Ollama is available"""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(f"{self.api_base}/api/tags", timeout=5) as resp:
                    return resp.status == 200
        except:
            return False
    
    async def _check_openai(self) -> bool:
        """Check if OpenAI API is available"""
        return bool(self.api_key)
    
    async def _check_anthropic(self) -> bool:
        """Check if Anthropic API is available"""
        return bool(self.api_key)
    
    async def generate(
        self,
        prompt: str,
        system: str = None,
        temperature: float = 0.7,
        max_tokens: int = 2048,
        stream: bool = False
    ) -> LLMResponse:
        """Generate response from LLM"""
        
        import time
        start_time = time.time()
        
        if self.provider == LLMProvider.OLLAMA:
            return await self._generate_ollama(prompt, system, temperature, max_tokens, stream, start_time)
        elif self.provider == LLMProvider.OPENAI:
            return await self._generate_openai(prompt, system, temperature, max_tokens, start_time)
        elif self.provider == LLMProvider.ANTHROPIC:
            return await self._generate_anthropic(prompt, system, temperature, max_tokens, start_time)
        else:
            return await self._generate_mock(prompt, start_time)
    
    async def _generate_ollama(
        self, 
        prompt: str, 
        system: str,
        temperature: float,
        max_tokens: int,
        stream: bool,
        start_time: float
    ) -> LLMResponse:
        """Generate using Ollama"""
        
        try:
            messages = []
            if system or self.system_prompt:
                messages.append({"role": "system", "content": system or self.system_prompt})
            messages.append({"role": "user", "content": prompt})
            
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{self.api_base}/api/chat",
                    json={
                        "model": self.model,
                        "messages": messages,
                        "stream": stream,
                        "options": {
                            "temperature": temperature,
                            "num_predict": max_tokens
                        }
                    },
                    timeout=aiohttp.ClientTimeout(total=120)
                ) as resp:
                    if resp.status != 200:
                        error = await resp.text()
                        return LLMResponse(
                            text="",
                            model=self.model,
                            provider=self.provider.value,
                            tokens_used=0,
                            finish_reason="error",
                            latency_ms=(time.time() - start_time) * 1000,
                            error=f"Ollama error: {error}"
                        )
                    
                    data = await resp.json()
                    text = data.get("message", {}).get("content", "")
                    
                    return LLMResponse(
                        text=text,
                        model=self.model,
                        provider=self.provider.value,
                        tokens_used=data.get("eval_count", len(text.split())),
                        finish_reason=data.get("done_reason", "stop"),
                        latency_ms=(time.time() - start_time) * 1000
                    )
                    
        except Exception as e:
            return LLMResponse(
                text="",
                model=self.model,
                provider=self.provider.value,
                tokens_used=0,
                finish_reason="error",
                latency_ms=(time.time() - start_time) * 1000,
                error=str(e)
            )
    
    async def _generate_openai(
        self,
        prompt: str,
        system: str,
        temperature: float,
        max_tokens: int,
        start_time: float
    ) -> LLMResponse:
        """Generate using OpenAI API"""
        
        try:
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            
            messages = []
            if system or self.system_prompt:
                messages.append({"role": "system", "content": system or self.system_prompt})
            messages.append({"role": "user", "content": prompt})
            
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    "https://api.openai.com/v1/chat/completions",
                    headers=headers,
                    json={
                        "model": self.model,
                        "messages": messages,
                        "temperature": temperature,
                        "max_tokens": max_tokens
                    },
                    timeout=aiohttp.ClientTimeout(total=60)
                ) as resp:
                    data = await resp.json()
                    
                    if "error" in data:
                        return LLMResponse(
                            text="",
                            model=self.model,
                            provider=self.provider.value,
                            tokens_used=0,
                            finish_reason="error",
                            latency_ms=(time.time() - start_time) * 1000,
                            error=data["error"].get("message", "Unknown error")
                        )
                    
                    return LLMResponse(
                        text=data["choices"][0]["message"]["content"],
                        model=self.model,
                        provider=self.provider.value,
                        tokens_used=data.get("usage", {}).get("total_tokens", 0),
                        finish_reason=data["choices"][0].get("finish_reason", "stop"),
                        latency_ms=(time.time() - start_time) * 1000
                    )
                    
        except Exception as e:
            return LLMResponse(
                text="",
                model=self.model,
                provider=self.provider.value,
                tokens_used=0,
                finish_reason="error",
                latency_ms=(time.time() - start_time) * 1000,
                error=str(e)
            )
    
    async def _generate_anthropic(
        self,
        prompt: str,
        system: str,
        temperature: float,
        max_tokens: int,
        start_time: float
    ) -> LLMResponse:
        """Generate using Anthropic API"""
        
        try:
            headers = {
                "x-api-key": self.api_key,
                "anthropic-version": "2023-06-01",
                "Content-Type": "application/json"
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    "https://api.anthropic.com/v1/messages",
                    headers=headers,
                    json={
                        "model": self.model,
                        "messages": [{"role": "user", "content": prompt}],
                        "system": system or self.system_prompt,
                        "temperature": temperature,
                        "max_tokens": max_tokens
                    },
                    timeout=aiohttp.ClientTimeout(total=60)
                ) as resp:
                    data = await resp.json()
                    
                    if "error" in data:
                        return LLMResponse(
                            text="",
                            model=self.model,
                            provider=self.provider.value,
                            tokens_used=0,
                            finish_reason="error",
                            latency_ms=(time.time() - start_time) * 1000,
                            error=data["error"].get("message", "Unknown error")
                        )
                    
                    return LLMResponse(
                        text=data["content"][0]["text"],
                        model=self.model,
                        provider=self.provider.value,
                        tokens_used=data.get("usage", {}).get("input_tokens", 0) + data["usage"].get("output_tokens", 0),
                        finish_reason=data["stop_reason"],
                        latency_ms=(time.time() - start_time) * 1000
                    )
                    
        except Exception as e:
            return LLMResponse(
                text="",
                model=self.model,
                provider=self.provider.value,
                tokens_used=0,
                finish_reason="error",
                latency_ms=(time.time() - start_time) * 1000,
                error=str(e)
            )
    
    async def _generate_mock(self, prompt: str, start_time: float) -> LLMResponse:
        """Mock response for testing without LLM"""
        
        # Simulate thinking
        await asyncio.sleep(0.1)
        
        responses = [
            f"I've analyzed your request: '{prompt[:50]}...'\n\n"
            f"As CODE: 02, I can help you with this task.\n"
            f"Would you like me to execute this step by step?",
            
            f"Understood. I'll process '{prompt[:30]}...' and break it down.\n\n"
            f"This requires multiple steps. Should I proceed with execution?",
            
            f"Processing request...\n\n"
            f"I've identified the best approach for this task.\n"
            f"Ready to execute when you confirm."
        ]
        
        import time
        import random
        text = responses[int(time.time()) % len(responses)]
        
        return LLMResponse(
            text=text,
            model="mock",
            provider="mock",
            tokens_used=len(text.split()),
            finish_reason="stop",
            latency_ms=(time.time() - start_time) * 1000
        )
    
    def add_to_history(self, role: str, content: str):
        """Add message to conversation history"""
        self.conversation.append(ConversationMessage(
            role=role,
            content=content,
            timestamp=asyncio.get_event_loop().time()
        ))
        
        # Trim history if too long
        if len(self.conversation) > self.max_history:
            self.conversation = self.conversation[-self.max_history:]
    
    def clear_history(self):
        """Clear conversation history"""
        self.conversation = []
    
    def get_history(self) -> List[Dict]:
        """Get conversation history"""
        return [
            {"role": msg.role, "content": msg.content}
            for msg in self.conversation
        ]
    
    async def think(
        self,
        problem: str,
        method: str = "chain_of_thought"
    ) -> Dict[str, Any]:
        """Deep thinking about a problem"""
        
        if method == "chain_of_thought":
            prompt = f"""Think through this problem step by step:

Problem: {problem}

Show your reasoning process:
1. What is the goal?
2. What information do I have?
3. What are the possible approaches?
4. What is the best path forward?
5. What could go wrong?

Provide a clear analysis."""
        else:
            prompt = f"Analyze this problem deeply: {problem}"
        
        response = await self.generate(prompt, temperature=0.5)
        
        return {
            "problem": problem,
            "method": method,
            "reasoning": response.text,
            "model": response.model,
            "latency_ms": response.latency_ms
        }
    
    async def execute_plan(self, goal: str, steps: List[str]) -> Dict[str, Any]:
        """Execute a multi-step plan with LLM guidance"""
        
        results = []
        
        for i, step in enumerate(steps):
            prompt = f"""Goal: {goal}

Current Step ({i+1}/{len(steps)}): {step}

Execute this step and report the result. Include any errors encountered."""
            
            response = await self.generate(prompt)
            results.append({
                "step": i + 1,
                "task": step,
                "result": response.text,
                "success": response.error is None
            })
        
        return {
            "goal": goal,
            "total_steps": len(steps),
            "completed_steps": len([r for r in results if r["success"]]),
            "results": results
        }


# Factory function
def create_llm_brain(provider: str = "auto", **kwargs) -> LLMBrain:
    """Create appropriate LLM brain based on availability"""
    
    if provider == "auto":
        # Try to detect best available provider
        try:
            import subprocess
            result = subprocess.run(
                "curl -s http://localhost:11434/api/tags",
                shell=True,
                capture_output=True,
                timeout=5
            )
            if result.returncode == 0:
                provider = "ollama"
            else:
                provider = "mock"
        except:
            provider = "mock"
    
    return LLMBrain(provider=provider, **kwargs)


# Singleton
_llm_brain: Optional[LLMBrain] = None

def get_llm_brain() -> LLMBrain:
    global _llm_brain
    if _llm_brain is None:
        _llm_brain = create_llm_brain()
    return _llm_brain
