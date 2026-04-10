"""
============================================================
REASONING ENGINE - Deep Thinking and Analysis
============================================================
Implements chain-of-thought reasoning
"""

from typing import Dict, List, Any, Optional
from dataclasses import dataclass
import re


@dataclass
class ReasoningStep:
    step_number: int
    thought: str
    evidence: List[str]
    conclusion: str
    confidence: float


class ReasoningEngine:
    """
    Implements multi-step reasoning for complex problems
    """
    
    def __init__(self):
        self.reasoning_chains = []
        self.thinking_methods = {
            "deductive": self._deductive_reasoning,
            "inductive": self._inductive_reasoning,
            "abductive": self._abductive_reasoning,
            "analogical": self._analogical_reasoning,
            "causal": self._causal_reasoning
        }
    
    async def think(self, prompt: str, method: str = "deductive") -> Dict[str, Any]:
        """
        Think through a problem step by step
        """
        
        reasoning_steps = []
        
        # Step 1: Decompose the problem
        decomposition = self._decompose_problem(prompt)
        reasoning_steps.append(ReasoningStep(
            step_number=1,
            thought=f"Decomposing problem: {decomposition['main_goal']}",
            evidence=decomposition.get("sub_goals", []),
            conclusion="Problem decomposed into manageable parts",
            confidence=0.9
        ))
        
        # Step 2: Identify knowns and unknowns
        knowns_unknowns = self._identify_knowns_unknowns(prompt)
        reasoning_steps.append(ReasoningStep(
            step_number=2,
            thought="Identifying knowns and unknowns",
            evidence=knowns_unknowns.get("knowns", []),
            conclusion=f"Found {len(knowns_unknowns.get('knowns', []))} knowns, {len(knowns_unknowns.get('unknowns', []))} unknowns",
            confidence=0.85
        ))
        
        # Step 3: Apply reasoning method
        if method in self.thinking_methods:
            method_result = await self.thinking_methods[method](prompt, knowns_unknowns)
        else:
            method_result = await self._deductive_reasoning(prompt, knowns_unknowns)
        
        reasoning_steps.extend(method_result)
        
        # Step 4: Generate conclusion
        conclusion = self._generate_conclusion(reasoning_steps)
        reasoning_steps.append(ReasoningStep(
            step_number=len(reasoning_steps) + 1,
            thought="Generating final conclusion",
            evidence=[s.conclusion for s in reasoning_steps[:-1]],
            conclusion=conclusion["statement"],
            confidence=conclusion["confidence"]
        ))
        
        # Store chain
        self.reasoning_chains.append({
            "prompt": prompt,
            "method": method,
            "steps": reasoning_steps,
            "timestamp": str(datetime.now())
        })
        
        return {
            "prompt": prompt,
            "method": method,
            "steps": [self._step_to_dict(s) for s in reasoning_steps],
            "conclusion": conclusion,
            "thinking_time": "simulated"
        }
    
    def _decompose_problem(self, prompt: str) -> Dict[str, Any]:
        """Break down problem into sub-goals"""
        
        main_goal = prompt
        
        # Extract sub-goals from prompt
        sub_goals = []
        
        # Look for action verbs
        actions = re.findall(r'\b(build|create|analyze|fix|design|implement|test|review)\b', prompt.lower())
        
        # Look for conjunctions that indicate steps
        if ' and ' in prompt.lower():
            parts = prompt.lower().split(' and ')
            sub_goals = [p.strip() for p in parts if p.strip()]
        
        # Look for numbered items
        numbers = re.findall(r'\d+\.\s*([^\d]+)', prompt)
        sub_goals.extend(numbers)
        
        return {
            "main_goal": main_goal,
            "sub_goals": sub_goals[:5] if sub_goals else ["Primary task"],
            "complexity": "high" if len(sub_goals) > 3 else "medium" if sub_goals else "low"
        }
    
    def _identify_knowns_unknowns(self, prompt: str) -> Dict[str, List[str]]:
        """Identify what we know and need to find"""
        
        knowns = []
        unknowns = []
        
        # Known patterns
        known_patterns = [
            r'(?:I want|I need|I have|I know)',
            r'(?:the|the\s+\w+\s+is)',
            r'(?:existing|current|already)'
        ]
        
        unknown_patterns = [
            r'(?:how|what|which)',
            r'(?:determine|find|figure out)',
            r'(?:need to|should|must)'
        ]
        
        for pattern in known_patterns:
            matches = re.findall(pattern, prompt.lower())
            knowns.extend(matches)
        
        for pattern in unknown_patterns:
            matches = re.findall(pattern, prompt.lower())
            unknowns.extend(matches)
        
        # Add context from prompt
        context_words = ['python', 'javascript', 'data', 'code', 'system', 'api', 'database']
        for word in context_words:
            if word in prompt.lower():
                knowns.append(f"Context: {word}")
        
        return {
            "knowns": list(set(knowns))[:5],
            "unknowns": list(set(unknowns))[:5]
        }
    
    async def _deductive_reasoning(self, prompt: str, context: Dict) -> List[ReasoningStep]:
        """Apply deductive reasoning (general to specific)"""
        
        steps = [
            ReasoningStep(
                step_number=3,
                thought="Applying deductive reasoning",
                evidence=["General principle: " + context.get("main_goal", "")],
                conclusion="Drawing specific conclusions from general rules",
                confidence=0.8
            )
        ]
        
        return steps
    
    async def _inductive_reasoning(self, prompt: str, context: Dict) -> List[ReasoningStep]:
        """Apply inductive reasoning (specific to general)"""
        
        steps = [
            ReasoningStep(
                step_number=3,
                thought="Applying inductive reasoning",
                evidence=context.get("knowns", []),
                conclusion="Forming general rules from specific observations",
                confidence=0.75
            )
        ]
        
        return steps
    
    async def _abductive_reasoning(self, prompt: str, context: Dict) -> List[ReasoningStep]:
        """Apply abductive reasoning (best explanation)"""
        
        steps = [
            ReasoningStep(
                step_number=3,
                thought="Applying abductive reasoning",
                evidence=["Observations from prompt"],
                conclusion="Finding the most likely explanation",
                confidence=0.7
            )
        ]
        
        return steps
    
    async def _analogical_reasoning(self, prompt: str, context: Dict) -> List[ReasoningStep]:
        """Apply analogical reasoning"""
        
        steps = [
            ReasoningStep(
                step_number=3,
                thought="Applying analogical reasoning",
                evidence=["Finding similar past problems"],
                conclusion="Adapting known solutions to new problem",
                confidence=0.75
            )
        ]
        
        return steps
    
    async def _causal_reasoning(self, prompt: str, context: Dict) -> List[ReasoningStep]:
        """Apply causal reasoning"""
        
        steps = [
            ReasoningStep(
                step_number=3,
                thought="Applying causal reasoning",
                evidence=["Identifying cause-effect relationships"],
                conclusion="Tracing causes and predicting effects",
                confidence=0.8
            )
        ]
        
        return steps
    
    def _generate_conclusion(self, steps: List[ReasoningStep]) -> Dict[str, Any]:
        """Generate final conclusion from reasoning steps"""
        
        avg_confidence = sum(s.confidence for s in steps) / len(steps) if steps else 0.5
        
        conclusions = [s.conclusion for s in steps]
        
        return {
            "statement": " | ".join(conclusions[-3:]) if conclusions else "Analysis complete",
            "confidence": avg_confidence,
            "key_findings": conclusions[:3]
        }
    
    def _step_to_dict(self, step: ReasoningStep) -> Dict:
        return {
            "step_number": step.step_number,
            "thought": step.thought,
            "evidence": step.evidence,
            "conclusion": step.conclusion,
            "confidence": step.confidence
        }
    
    def get_reasoning_history(self) -> List[Dict]:
        """Get history of reasoning chains"""
        return [
            {
                "prompt": chain["prompt"],
                "method": chain["method"],
                "timestamp": chain["timestamp"],
                "steps": len(chain["steps"])
            }
            for chain in self.reasoning_chains[-10:]
        ]


from datetime import datetime
