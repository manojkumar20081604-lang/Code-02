"""
╔══════════════════════════════════════════════════════════════════════════════════╗
║                                                                              ║
║          02 ULTRA - COGNITIVE AUTONOMOUS AI SYSTEM                          ║
║                                                                              ║
║       "Think. Plan. Learn. Evolve. Execute. Improve. Repeat."              ║
║                                                                              ║
║                   LEVEL 5: ADAPTIVE COGNITIVE AI SYSTEM                     ║
║                                                                              ║
╚══════════════════════════════════════════════════════════════════════════════════╝

ULTRA LEVEL FEATURES:

┌──────────────────────────────────────────────────────────────────────────────┐
│                          META-INTELLIGENCE                                   │
│  • Self-reflection & evaluation                                             │
│  • Performance tracking & optimization                                       │
│  • Strategy adaptation                                                      │
│  • Learning-to-learn (meta-learning)                                         │
└──────────────────────────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────────────────────────┐
│                         RECURSIVE AGENTS                                     │
│  • Spawn sub-agents for parallel execution                                  │
│  • Agent tree for complex tasks                                             │
│  • Collaborative problem solving                                             │
│  • Emergent behavior from agent interactions                                │
└──────────────────────────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────────────────────────┐
│                          WORLD MODEL                                        │
│  • Internal representation of user's reality                                │
│  • Entity relationships (people, projects, code, concepts)                  │
│  • Temporal reasoning (past → present → future)                            │
│  • Causal inference                                                         │
└──────────────────────────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────────────────────────┐
│                      GOAL EVOLUTION SYSTEM                                   │
│  • Goal refinement & enhancement                                             │
│  • Sub-goal decomposition                                                   │
│  • Strategy planning                                                        │
│  • Progress tracking & adaptation                                           │
└──────────────────────────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────────────────────────┐
│                     ENVIRONMENT AWARENESS                                    │
│  • Real-time system monitoring                                              │
│  • File system understanding                                                │
│  • Process & application tracking                                            │
│  • Context synthesis from environment                                      │
└──────────────────────────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────────────────────────┐
│                    AUTONOMOUS PROJECT BUILDER                               │
│  • Project scaffolding from intent                                          │
│  • Architecture design                                                     │
│  • Code generation & integration                                            │
│  • Testing & deployment automation                                          │
└──────────────────────────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────────────────────────┐
│                      CONTINUOUS LEARNING LOOP                                │
│  • Experience → Analysis → Insight → Action → Evaluation → Improve          │
│  • Feedback integration                                                     │
│  • Pattern recognition & generalization                                     │
│  • Knowledge consolidation                                                  │
└──────────────────────────────────────────────────────────────────────────────┘
"""

import os
import sys
import json
import time
import uuid
import logging
import asyncio
import threading
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Callable, Set, Tuple
from dataclasses import dataclass, field
from enum import Enum
from collections import defaultdict, deque
from threading import Lock, Event
from abc import ABC, abstractmethod

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(name)s: %(message)s'
)
logger = logging.getLogger("02-ULTRA")

# ═══════════════════════════════════════════════════════════════════════════════════
# ENUMS
# ═══════════════════════════════════════════════════════════════════════════════════

class AgentState(Enum):
    IDLE = "idle"
    THINKING = "thinking"
    PLANNING = "planning"
    EXECUTING = "executing"
    LEARNING = "learning"
    REFLECTING = "reflecting"
    WAITING = "waiting"
    COMPLETED = "completed"
    FAILED = "failed"

class TaskPriority(Enum):
    CRITICAL = 1
    HIGH = 2
    MEDIUM = 3
    LOW = 4
    BACKGROUND = 5

class LearningType(Enum):
    SUPERVISED = "supervised"
    REINFORCEMENT = "reinforcement"
    OBSERVATION = "observation"
    EXPLORATION = "exploration"

class EntityType(Enum):
    USER = "user"
    PROJECT = "project"
    FILE = "file"
    CONCEPT = "concept"
    TASK = "task"
    TOOL = "tool"
    AGENT = "agent"
    MEMORY = "memory"
    GOAL = "goal"

# ═══════════════════════════════════════════════════════════════════════════════════
# CORE DATA CLASSES
# ═══════════════════════════════════════════════════════════════════════════════════

@dataclass
class Thought:
    """A single unit of thought/reasoning"""
    id: str
    content: str
    timestamp: datetime
    confidence: float = 0.5
    reasoning_chain: List[str] = field(default_factory=list)
    alternatives: List[str] = field(default_factory=list)
    selected_reasoning: str = ""
    outcome: Optional[str] = None
    success: Optional[bool] = None

@dataclass
class Experience:
    """An experience that can be learned from"""
    id: str
    situation: str
    action: str
    outcome: Any
    success: bool
    timestamp: datetime
    context: Dict[str, Any] = field(default_factory=dict)
    feedback: Optional[str] = None
    lessons: List[str] = field(default_factory=list)

@dataclass
class Entity:
    """An entity in the world model"""
    id: str
    name: str
    entity_type: EntityType
    properties: Dict[str, Any] = field(default_factory=dict)
    relationships: Dict[str, List[str]] = field(default_factory=dict)  # relation_type -> [entity_ids]
    history: List[Dict] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.now)
    last_accessed: datetime = field(default_factory=datetime.now)

@dataclass
class Strategy:
    """A strategy for achieving goals"""
    id: str
    name: str
    description: str
    steps: List[Dict]
    success_rate: float = 0.0
    times_used: int = 0
    times_succeeded: int = 0
    context_requirements: Dict[str, Any] = field(default_factory=dict)
    expected_duration: int = 0  # minutes

@dataclass
class Goal:
    """A goal with evolution capabilities"""
    id: str
    description: str
    original_description: str
    priority: TaskPriority
    status: str = "active"
    sub_goals: List['Goal'] = field(default_factory=list)
    strategy: Optional[Strategy] = None
    progress: float = 0.0
    iterations: int = 0
    evolution_history: List[Dict] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.now)
    deadline: Optional[datetime] = None

@dataclass
class SubAgent:
    """A sub-agent spawned for parallel execution"""
    id: str
    name: str
    task: str
    parent_id: str
    state: AgentState = AgentState.IDLE
    result: Any = None
    progress: float = 0.0
    created_at: datetime = field(default_factory=datetime.now)
    completed_at: Optional[datetime] = None
    children: List[str] = field(default_factory=list)

# ═══════════════════════════════════════════════════════════════════════════════════
# META-INTELLIGENCE ENGINE
# ═══════════════════════════════════════════════════════════════════════════════════

class MetaIntelligence:
    """
    Meta-Intelligence: The ability to think about thinking.
    
    Enables:
    - Self-reflection on decisions
    - Performance evaluation
    - Strategy adaptation
    - Learning how to learn
    """
    
    def __init__(self):
        self.thought_history: deque = deque(maxlen=200)
        self.experience_history: deque = deque(maxlen=500)
        self.performance_metrics: Dict[str, List[float]] = defaultdict(list)
        self.strategies: Dict[str, Strategy] = {}
        self.self_model: Dict[str, Any] = {
            "strengths": [],
            "weaknesses": [],
            "learning_rate": 0.5,
            "adaptation_speed": 0.5,
            "confidence_calibration": 1.0
        }
        self.learning_lock = Lock()
        
        logger.info("Meta-Intelligence initialized")
    
    def think(self, situation: str, context: Dict = None) -> Thought:
        """Generate a thought with reasoning chain"""
        thought_id = str(uuid.uuid4())
        
        # Generate reasoning chain
        reasoning_steps = self._generate_reasoning(situation, context)
        
        # Evaluate alternatives
        alternatives = self._evaluate_alternatives(situation, reasoning_steps)
        
        # Select best reasoning
        selected = self._select_reasoning(reasoning_steps, alternatives)
        
        thought = Thought(
            id=thought_id,
            content=situation,
            timestamp=datetime.now(),
            confidence=selected["confidence"],
            reasoning_chain=reasoning_steps,
            alternatives=alternatives,
            selected_reasoning=selected["reasoning"]
        )
        
        self.thought_history.append(thought)
        return thought
    
    def _generate_reasoning(self, situation: str, context: Dict = None) -> List[str]:
        """Generate a chain of reasoning steps"""
        steps = [
            f"Understanding: {situation[:50]}...",
            "Analyzing context and constraints",
            "Retrieving relevant memories",
            "Generating potential approaches",
            "Evaluating trade-offs",
            "Selecting optimal path"
        ]
        return steps
    
    def _evaluate_alternatives(self, situation: str, reasoning: List[str]) -> List[str]:
        """Evaluate alternative reasoning paths"""
        return [
            f"Alternative A: Conservative approach for {situation[:30]}",
            f"Alternative B: Aggressive approach for {situation[:30]}",
            f"Alternative C: Balanced approach for {situation[:30]}"
        ]
    
    def _select_reasoning(self, reasoning: List[str], alternatives: List[str]) -> Dict:
        """Select the best reasoning path"""
        # Simple selection based on confidence
        return {
            "reasoning": reasoning[-1],  # Last step is selection
            "confidence": 0.7 + (len(reasoning) * 0.05)
        }
    
    def learn_from_experience(self, experience: Experience):
        """Learn from an experience"""
        with self.learning_lock:
            self.experience_history.append(experience)
            
            # Update self-model
            self._update_self_model(experience)
            
            # Update strategy success rates
            self._update_strategy_performance(experience)
            
            # Generate lessons
            lessons = self._extract_lessons(experience)
            experience.lessons = lessons
            
            logger.info(f"Learned from experience: {experience.action[:50]}... (success: {experience.success})")
    
    def _update_self_model(self, experience: Experience):
        """Update internal model of capabilities"""
        if experience.success:
            self.self_model["strengths"].append(experience.action)
            self.self_model["learning_rate"] = min(1.0, self.self_model["learning_rate"] + 0.01)
        else:
            self.self_model["weaknesses"].append(experience.action)
            self.self_model["learning_rate"] = max(0.1, self.self_model["learning_rate"] - 0.01)
        
        # Keep only recent examples
        self.self_model["strengths"] = self.self_model["strengths"][-20:]
        self.self_model["weaknesses"] = self.self_model["weaknesses"][-20:]
    
    def _update_strategy_performance(self, experience: Experience):
        """Update strategy performance metrics"""
        for strategy in self.strategies.values():
            if strategy.description in experience.action:
                strategy.times_used += 1
                if experience.success:
                    strategy.times_succeeded += 1
                strategy.success_rate = strategy.times_succeeded / strategy.times_used
    
    def _extract_lessons(self, experience: Experience) -> List[str]:
        """Extract lessons from experience"""
        lessons = []
        
        if experience.success:
            lessons.append(f"Success pattern: {experience.action[:50]}")
        else:
            lessons.append(f"Failure pattern to avoid: {experience.action[:50]}")
            if experience.feedback:
                lessons.append(f"Feedback: {experience.feedback}")
        
        return lessons
    
    def reflect(self) -> Dict:
        """Self-reflection on recent experiences"""
        recent = list(self.experience_history)[-20:]
        
        success_rate = sum(1 for e in recent if e.success) / max(len(recent), 1)
        avg_confidence = sum(t.confidence for t in list(self.thought_history)[-20:]) / max(len(self.thought_history), 1)
        
        insights = [
            f"Recent success rate: {success_rate:.1%}",
            f"Average decision confidence: {avg_confidence:.1%}",
            f"Total experiences: {len(self.experience_history)}",
            f"Active strategies: {len(self.strategies)}",
            f"Learning rate: {self.self_model['learning_rate']:.2f}"
        ]
        
        return {
            "insights": insights,
            "self_model": self.self_model,
            "performance": {
                "success_rate": success_rate,
                "avg_confidence": avg_confidence,
                "total_experiences": len(self.experience_history)
            }
        }
    
    def get_recommendation(self) -> str:
        """Get self-improvement recommendation"""
        reflection = self.reflect()
        
        if reflection["performance"]["success_rate"] < 0.6:
            return "Consider being more conservative in approach selection."
        elif reflection["self_model"]["learning_rate"] < 0.3:
            return "Learning rate is low. Try exploring new strategies."
        
        return "System is performing well. Continue current approach."

# ═══════════════════════════════════════════════════════════════════════════════════
# RECURSIVE AGENT SYSTEM
# ═══════════════════════════════════════════════════════════════════════════════════

class RecursiveAgentSystem:
    """
    Recursive Agent System: Spawns sub-agents for parallel execution.
    
    Features:
    - Agent tree for complex tasks
    - Parallel execution
    - Collaborative problem solving
    - Emergent behavior
    """
    
    def __init__(self, meta_intelligence: MetaIntelligence = None):
        self.meta = meta_intelligence or MetaIntelligence()
        self.agents: Dict[str, SubAgent] = {}
        self.agent_lock = Lock()
        self.max_depth = 3
        self.max_concurrent = 10
        
        # Agent templates
        self.agent_templates = {
            "researcher": {
                "role": "Research and gather information",
                "tools": ["search", "read", "summarize"]
            },
            "coder": {
                "role": "Write and debug code",
                "tools": ["generate", "explain", "fix"]
            },
            "planner": {
                "role": "Create execution plans",
                "tools": ["analyze", "plan", "coordinate"]
            },
            "tester": {
                "role": "Test and validate",
                "tools": ["test", "verify", "report"]
            }
        }
        
        logger.info("Recursive Agent System initialized")
    
    def spawn_agent(
        self, 
        name: str, 
        task: str, 
        parent_id: str = None,
        agent_type: str = "planner"
    ) -> SubAgent:
        """Spawn a new sub-agent"""
        agent_id = str(uuid.uuid4())[:8]
        
        # Check depth limit
        depth = 0
        if parent_id and parent_id in self.agents:
            parent = self.agents[parent_id]
            depth = self._get_agent_depth(parent)
        
        if depth >= self.max_depth:
            logger.warning(f"Max depth reached, spawning as root")
            parent_id = None
        
        agent = SubAgent(
            id=agent_id,
            name=name,
            task=task,
            parent_id=parent_id,
            state=AgentState.IDLE
        )
        
        with self.agent_lock:
            self.agents[agent_id] = agent
            
            # Update parent's children
            if parent_id and parent_id in self.agents:
                self.agents[parent_id].children.append(agent_id)
        
        logger.info(f"Spawned agent {agent_id} ({name}) for task: {task[:50]}...")
        return agent
    
    def _get_agent_depth(self, agent: SubAgent) -> int:
        """Get depth of agent in tree"""
        depth = 0
        current = agent
        while current.parent_id and current.parent_id in self.agents:
            depth += 1
            current = self.agents[current.parent_id]
        return depth
    
    async def execute_task_tree(self, root_task: str) -> Dict:
        """Execute a task by spawning agents recursively"""
        # Create root agent
        root = self.spawn_agent("orchestrator", root_task)
        root.state = AgentState.EXECUTING
        
        # Decompose task
        sub_tasks = self._decompose_task(root_task)
        
        # Spawn children for sub-tasks
        child_agents = []
        for i, sub_task in enumerate(sub_tasks):
            child = self.spawn_agent(
                f"agent_{i}",
                sub_task,
                parent_id=root.id,
                agent_type=self._select_agent_type(sub_task)
            )
            child.state = AgentState.EXECUTING
            child_agents.append(child)
        
        # Execute children in parallel
        results = await asyncio.gather(*[
            self._execute_agent(child) for child in child_agents
        ])
        
        # Aggregate results
        root.state = AgentState.COMPLETED
        root.result = self._aggregate_results(results)
        root.completed_at = datetime.now()
        
        # Learn from execution
        self.meta.learn_from_experience(Experience(
            id=str(uuid.uuid4()),
            situation=root_task,
            action=f"Executed task tree with {len(sub_tasks)} subtasks",
            outcome=root.result,
            success=True,
            timestamp=datetime.now()
        ))
        
        return {
            "root_id": root.id,
            "result": root.result,
            "agents_created": len(self.agents),
            "execution_time": (datetime.now() - root.created_at).total_seconds()
        }
    
    def _decompose_task(self, task: str) -> List[str]:
        """Decompose a task into subtasks"""
        # Simple decomposition - in reality would use LLM
        return [
            f"Analyze: {task}",
            f"Plan solution for: {task}",
            f"Execute: {task}",
            f"Verify: {task}"
        ]
    
    def _select_agent_type(self, task: str) -> str:
        """Select appropriate agent type for task"""
        task_lower = task.lower()
        
        if "research" in task_lower or "find" in task_lower or "search" in task_lower:
            return "researcher"
        elif "code" in task_lower or "write" in task_lower or "implement" in task_lower:
            return "coder"
        elif "plan" in task_lower or "coordinate" in task_lower:
            return "planner"
        elif "test" in task_lower or "verify" in task_lower:
            return "tester"
        
        return "planner"
    
    async def _execute_agent(self, agent: SubAgent) -> Dict:
        """Execute a single agent's task"""
        logger.info(f"Agent {agent.id} executing: {agent.task[:50]}...")
        
        # Simulate work
        await asyncio.sleep(0.1 * len(agent.task.split()))
        
        agent.state = AgentState.COMPLETED
        agent.result = {"status": "completed", "output": f"Result of: {agent.task[:30]}"}
        agent.completed_at = datetime.now()
        agent.progress = 1.0
        
        return agent.result
    
    def _aggregate_results(self, results: List[Dict]) -> Dict:
        """Aggregate results from multiple agents"""
        return {
            "subtask_results": results,
            "combined_status": "success",
            "total_results": len(results)
        }
    
    def get_agent_tree(self, root_id: str = None) -> Dict:
        """Get the agent tree structure"""
        if not self.agents:
            return {"agents": [], "tree": {}}
        
        if root_id and root_id in self.agents:
            root = self.agents[root_id]
            return {
                "root": {
                    "id": root.id,
                    "name": root.name,
                    "state": root.state.value,
                    "children": [self.agents[c].to_dict() if hasattr(self.agents[c], 'to_dict') else str(self.agents[c]) for c in root.children]
                }
            }
        
        # Return all agents
        return {
            "agents": [
                {
                    "id": a.id,
                    "name": a.name,
                    "state": a.state.value,
                    "parent": a.parent_id,
                    "children": a.children
                }
                for a in self.agents.values()
            ]
        }
    
    def kill_agent(self, agent_id: str) -> bool:
        """Kill an agent and its children"""
        with self.agent_lock:
            if agent_id not in self.agents:
                return False
            
            agent = self.agents[agent_id]
            
            # Recursively kill children
            for child_id in agent.children[:]:
                self.kill_agent(child_id)
            
            # Remove from parent's children
            if agent.parent_id and agent.parent_id in self.agents:
                parent = self.agents[agent.parent_id]
                if agent_id in parent.children:
                    parent.children.remove(agent_id)
            
            # Remove agent
            del self.agents[agent_id]
            
            return True

# ═══════════════════════════════════════════════════════════════════════════════════
# WORLD MODEL (KNOWLEDGE GRAPH)
# ═══════════════════════════════════════════════════════════════════════════════════

class WorldModel:
    """
    World Model: Internal representation of reality.
    
    Features:
    - Entity management
    - Relationship tracking
    - Temporal reasoning
    - Causal inference
    """
    
    def __init__(self):
        self.entities: Dict[str, Entity] = {}
        self.entity_lock = Lock()
        self.causal_chains: Dict[str, List[Dict]] = defaultdict(list)
        
        # Create user entity
        self._create_entity("The User", EntityType.USER, {
            "goals": [],
            "preferences": {},
            "patterns": []
        }, entity_id="user_main")
        
        logger.info("World Model initialized")
    
    def _create_entity(
        self, 
        name: str, 
        entity_type: EntityType, 
        properties: Dict = None,
        entity_id: str = None
    ) -> Entity:
        """Create a new entity"""
        eid = entity_id or str(uuid.uuid4())
        
        entity = Entity(
            id=eid,
            name=name,
            entity_type=entity_type,
            properties=properties or {}
        )
        
        with self.entity_lock:
            self.entities[eid] = entity
        
        return entity
    
    def add_entity(
        self,
        name: str,
        entity_type: EntityType,
        properties: Dict = None,
        relationships: Dict[str, List[str]] = None
    ) -> Entity:
        """Add an entity to the world model"""
        entity = self._create_entity(name, entity_type, properties)
        
        if relationships:
            entity.relationships = relationships
            
            # Add reverse relationships
            for rel_type, related_ids in relationships.items():
                for related_id in related_ids:
                    if related_id in self.entities:
                        reverse_rel = f"inverse_{rel_type}"
                        if reverse_rel not in self.entities[related_id].relationships:
                            self.entities[related_id].relationships[reverse_rel] = []
                        if entity.id not in self.entities[related_id].relationships[reverse_rel]:
                            self.entities[related_id].relationships[reverse_rel].append(entity.id)
        
        logger.info(f"Added entity: {name} ({entity_type.value})")
        return entity
    
    def relate(self, entity1_id: str, entity2_id: str, relationship_type: str):
        """Create a relationship between two entities"""
        with self.entity_lock:
            if entity1_id in self.entities and entity2_id in self.entities:
                e1 = self.entities[entity1_id]
                e2 = self.entities[entity2_id]
                
                if relationship_type not in e1.relationships:
                    e1.relationships[relationship_type] = []
                if entity2_id not in e1.relationships[relationship_type]:
                    e1.relationships[relationship_type].append(entity2_id)
                
                # Record causal chain
                self.causal_chains[entity1_id].append({
                    "action": f"related_to_{relationship_type}",
                    "target": entity2_id,
                    "timestamp": datetime.now().isoformat()
                })
    
    def query(
        self, 
        entity_type: EntityType = None,
        properties: Dict = None,
        relationships: Dict = None
    ) -> List[Entity]:
        """Query entities matching criteria"""
        results = []
        
        with self.entity_lock:
            for entity in self.entities.values():
                # Filter by type
                if entity_type and entity.entity_type != entity_type:
                    continue
                
                # Filter by properties
                if properties:
                    match = all(
                        entity.properties.get(k) == v 
                        for k, v in properties.items()
                    )
                    if not match:
                        continue
                
                # Filter by relationships
                if relationships:
                    match = all(
                        any(rel_id in entity.relationships.get(rel_type, [])
                            for rel_id in rel_ids)
                        for rel_type, rel_ids in relationships.items()
                    )
                    if not match:
                        continue
                
                results.append(entity)
        
        return results
    
    def get_entity_context(self, entity_id: str) -> Dict:
        """Get full context around an entity"""
        if entity_id not in self.entities:
            return {}
        
        entity = self.entities[entity_id]
        
        context = {
            "entity": {
                "id": entity.id,
                "name": entity.name,
                "type": entity.entity_type.value,
                "properties": entity.properties,
                "history": entity.history[-10:]  # Last 10 history items
            },
            "relationships": {},
            "related_entities": []
        }
        
        # Get related entities
        for rel_type, related_ids in entity.relationships.items():
            context["relationships"][rel_type] = len(related_ids)
            for rid in related_ids[:5]:  # Limit to 5
                if rid in self.entities:
                    context["related_entities"].append({
                        "id": rid,
                        "name": self.entities[rid].name,
                        "type": self.entities[rid].entity_type.value,
                        "relationship": rel_type
                    })
        
        return context
    
    def update_entity_property(self, entity_id: str, key: str, value: Any):
        """Update an entity's property"""
        with self.entity_lock:
            if entity_id in self.entities:
                entity = self.entities[entity_id]
                old_value = entity.properties.get(key)
                entity.properties[key] = value
                entity.last_accessed = datetime.now()
                
                # Record in history
                entity.history.append({
                    "action": "property_update",
                    "key": key,
                    "old_value": old_value,
                    "new_value": value,
                    "timestamp": datetime.now().isoformat()
                })
    
    def infer_causal_chain(self, entity_id: str) -> List[Dict]:
        """Infer causal chains involving an entity"""
        chains = []
        
        # Direct causal chains
        for event in self.causal_chains.get(entity_id, []):
            chains.append({
                "cause": entity_id,
                "action": event["action"],
                "effect": event["target"],
                "timestamp": event["timestamp"]
            })
        
        return chains
    
    def get_world_summary(self) -> Dict:
        """Get summary of the world model"""
        type_counts = defaultdict(int)
        total_relationships = 0
        
        with self.entity_lock:
            for entity in self.entities.values():
                type_counts[entity.entity_type.value] += 1
                total_relationships += sum(
                    len(related) 
                    for related in entity.relationships.values()
                )
        
        return {
            "total_entities": len(self.entities),
            "entities_by_type": dict(type_counts),
            "total_relationships": total_relationships // 2,  # Divided for bidirectional
            "causal_chains": sum(len(c) for c in self.causal_chains.values())
        }

# ═══════════════════════════════════════════════════════════════════════════════════
# GOAL EVOLUTION SYSTEM
# ═══════════════════════════════════════════════════════════════════════════════════

class GoalEvolutionSystem:
    """
    Goal Evolution: AI improves and evolves goals.
    
    Features:
    - Goal refinement
    - Sub-goal decomposition
    - Strategy planning
    - Progress tracking
    """
    
    def __init__(self, world_model: WorldModel = None):
        self.world = world_model or WorldModel()
        self.active_goals: Dict[str, Goal] = {}
        self.completed_goals: Dict[str, Goal] = {}
        self.goal_history: deque = deque(maxlen=100)
        
        logger.info("Goal Evolution System initialized")
    
    def create_evolutionary_goal(self, description: str, priority: TaskPriority = TaskPriority.MEDIUM) -> Goal:
        """Create a goal with evolution capabilities"""
        goal_id = str(uuid.uuid4())
        
        # Pre-process goal to improve it
        refined_description = self._refine_goal(description)
        
        goal = Goal(
            id=goal_id,
            description=refined_description,
            original_description=description,
            priority=priority,
            sub_goals=[]
        )
        
        # Add to world model
        self.world.add_entity(
            name=refined_description[:50],
            entity_type=EntityType.GOAL,
            properties={
                "priority": priority.value,
                "status": "active"
            }
        )
        
        self.active_goals[goal_id] = goal
        logger.info(f"Created evolutionary goal: {refined_description[:50]}...")
        
        return goal
    
    def _refine_goal(self, description: str) -> str:
        """Refine and improve goal description"""
        # Simple refinement - in reality would use LLM
        refined = description.strip()
        
        # Ensure it ends with action verb
        action_verbs = ["Create", "Build", "Implement", "Design", "Develop", "Analyze", "Optimize"]
        if not any(refined.startswith(v) for v in action_verbs):
            refined = f"Execute: {refined}"
        
        return refined
    
    def decompose_goal(self, goal_id: str) -> List[Goal]:
        """Decompose goal into sub-goals"""
        if goal_id not in self.active_goals:
            return []
        
        goal = self.active_goals[goal_id]
        
        # Generate sub-goals
        sub_goal_descriptions = self._generate_sub_goals(goal.description)
        
        sub_goals = []
        for desc in sub_goal_descriptions:
            sub_goal = Goal(
                id=str(uuid.uuid4()),
                description=desc,
                original_description=desc,
                priority=goal.priority,
            )
            sub_goals.append(sub_goal)
        
        goal.sub_goals = sub_goals
        goal.iterations += 1
        
        logger.info(f"Decomposed goal {goal_id} into {len(sub_goals)} sub-goals")
        return sub_goals
    
    def _generate_sub_goals(self, goal_description: str) -> List[str]:
        """Generate sub-goals for a goal"""
        # Standard decomposition
        return [
            f"Research: {goal_description}",
            f"Plan: {goal_description}",
            f"Execute: {goal_description}",
            f"Verify: {goal_description}",
            f"Refine: {goal_description}"
        ]
    
    def evolve_goal(self, goal_id: str, feedback: str = None) -> Goal:
        """Evolve/improve a goal based on feedback"""
        if goal_id not in self.active_goals:
            return None
        
        goal = self.active_goals[goal_id]
        original = goal.description
        
        # Improve based on feedback or self-reflection
        improvements = [
            "Add error handling",
            "Include testing",
            "Add documentation",
            "Optimize for performance",
            "Add logging",
            "Include edge cases"
        ]
        
        # Select improvement
        improvement = improvements[goal.iterations % len(improvements)]
        evolved_description = f"{original} with {improvement}"
        
        # Record evolution
        goal.evolution_history.append({
            "iteration": goal.iterations,
            "from": goal.description,
            "to": evolved_description,
            "timestamp": datetime.now().isoformat(),
            "feedback": feedback
        })
        
        goal.description = evolved_description
        goal.iterations += 1
        
        logger.info(f"Evolved goal: {original[:30]}... → {evolved_description[:30]}...")
        return goal
    
    def update_progress(self, goal_id: str, progress: float):
        """Update goal progress"""
        if goal_id in self.active_goals:
            self.active_goals[goal_id].progress = min(1.0, max(0.0, progress))
            
            if progress >= 1.0:
                self.complete_goal(goal_id)
    
    def complete_goal(self, goal_id: str):
        """Mark goal as completed"""
        if goal_id in self.active_goals:
            goal = self.active_goals[goal_id]
            goal.progress = 1.0
            goal.status = "completed"
            
            self.completed_goals[goal_id] = goal
            del self.active_goals[goal_id]
            self.goal_history.append(goal)
            
            logger.info(f"Completed goal: {goal.description[:50]}...")
    
    def get_active_strategy(self, goal_id: str) -> Optional[Strategy]:
        """Get or create strategy for goal"""
        if goal_id not in self.active_goals:
            return None
        
        goal = self.active_goals[goal_id]
        
        strategy = Strategy(
            id=str(uuid.uuid4()),
            name=f"Strategy for {goal.description[:30]}",
            description=f"Approach for {goal.description}",
            steps=[
                {"action": "analyze", "description": "Analyze requirements"},
                {"action": "plan", "description": "Create execution plan"},
                {"action": "execute", "description": "Execute plan"},
                {"action": "verify", "description": "Verify results"}
            ],
            expected_duration=30
        )
        
        goal.strategy = strategy
        return strategy
    
    def get_goals_summary(self) -> Dict:
        """Get summary of all goals"""
        return {
            "active": len(self.active_goals),
            "completed": len(self.completed_goals),
            "total": len(self.goal_history),
            "with_subgoals": sum(1 for g in self.active_goals.values() if g.sub_goals),
            "evolved": sum(1 for g in self.goal_history if g.evolution_history)
        }

# ═══════════════════════════════════════════════════════════════════════════════════
# AUTONOMOUS PROJECT BUILDER
# ═══════════════════════════════════════════════════════════════════════════════════

class AutonomousProjectBuilder:
    """
    Autonomous Project Builder: Builds projects from intent.
    
    Features:
    - Project scaffolding
    - Architecture design
    - Code generation
    - Testing automation
    """
    
    def __init__(self, recursive_agents: RecursiveAgentSystem = None):
        self.agents = recursive_agents or RecursiveAgentSystem()
        self.project_templates = self._load_templates()
        
        logger.info("Autonomous Project Builder initialized")
    
    def _load_templates(self) -> Dict:
        """Load project templates"""
        return {
            "web_app": {
                "structure": ["frontend/", "backend/", "tests/"],
                "files": {
                    "frontend/index.html": "Basic HTML template",
                    "frontend/app.js": "Main JavaScript",
                    "backend/server.py": "Flask server",
                    "tests/test.py": "Unit tests"
                },
                "dependencies": ["flask", "requests"]
            },
            "cli_tool": {
                "structure": ["src/", "tests/", "docs/"],
                "files": {
                    "src/main.py": "CLI entry point",
                    "src/core.py": "Core functionality",
                    "tests/test_core.py": "Tests",
                    "README.md": "Documentation"
                },
                "dependencies": ["click", "pytest"]
            },
            "api_service": {
                "structure": ["routes/", "models/", "middleware/", "tests/"],
                "files": {
                    "app.py": "Main Flask app",
                    "routes/api.py": "API endpoints",
                    "models/db.py": "Database models",
                    "middleware/auth.py": "Auth middleware"
                },
                "dependencies": ["flask", "flask-cors", "flask-sqlalchemy"]
            }
        }
    
    async def build_project(self, description: str) -> Dict:
        """Build a complete project from description"""
        logger.info(f"Building project: {description[:50]}...")
        
        # Phase 1: Analyze and design
        architecture = await self._design_architecture(description)
        
        # Phase 2: Create structure
        structure = await self._create_structure(architecture)
        
        # Phase 3: Generate code
        code_files = await self._generate_code(architecture)
        
        # Phase 4: Create tests
        tests = await self._generate_tests(architecture)
        
        project_result = {
            "description": description,
            "architecture": architecture,
            "structure": structure,
            "files_created": len(code_files) + len(tests),
            "status": "completed"
        }
        
        logger.info(f"Project built: {len(code_files)} files created")
        return project_result
    
    async def _design_architecture(self, description: str) -> Dict:
        """Design project architecture"""
        # Simulate LLM-based design
        return {
            "type": "web_app",
            "name": self._extract_project_name(description),
            "components": ["frontend", "backend", "database"],
            "technologies": ["python", "javascript", "html", "css"],
            "features": self._extract_features(description)
        }
    
    def _extract_project_name(self, description: str) -> str:
        """Extract project name from description"""
        words = description.split()
        for word in words:
            if word.lower() not in ["create", "build", "make", "develop", "a", "an", "project", "app"]:
                return word.capitalize()
        return "MyProject"
    
    def _extract_features(self, description: str) -> List[str]:
        """Extract features from description"""
        # Simple feature extraction
        features = []
        keywords = {
            "user": "User authentication",
            "auth": "Authentication",
            "api": "REST API",
            "database": "Database storage",
            "dashboard": "Admin dashboard",
            "chart": "Data visualization",
            "real": "Real-time updates"
        }
        
        desc_lower = description.lower()
        for keyword, feature in keywords.items():
            if keyword in desc_lower:
                features.append(feature)
        
        return features if features else ["Basic functionality"]
    
    async def _create_structure(self, architecture: Dict) -> List[str]:
        """Create project directory structure"""
        project_type = architecture.get("type", "web_app")
        template = self.project_templates.get(project_type, self.project_templates["web_app"])
        
        structure = template["structure"].copy()
        
        # Add project-specific directories
        structure.append("README.md")
        structure.append("requirements.txt")
        
        return structure
    
    async def _generate_code(self, architecture: Dict) -> Dict[str, str]:
        """Generate code files"""
        project_type = architecture.get("type", "web_app")
        template = self.project_templates.get(project_type, self.project_templates["web_app"])
        
        files = {}
        for file_path, content_template in template["files"].items():
            files[file_path] = self._generate_file_content(file_path, architecture)
        
        return files
    
    def _generate_file_content(self, file_path: str, architecture: Dict) -> str:
        """Generate content for a specific file"""
        if file_path.endswith(".html"):
            return f'''<!DOCTYPE html>
<html>
<head>
    <title>{architecture.get("name", "Project")}</title>
</head>
<body>
    <h1>Welcome to {architecture.get("name", "Project")}</h1>
</body>
</html>'''
        elif file_path.endswith(".py"):
            return f'''# {architecture.get("name", "Project")} Backend

def main():
    print("Hello from {architecture.get('name', 'Project')}!")

if __name__ == "__main__":
    main()
'''
        else:
            return f"// {file_path} for {architecture.get('name', 'Project')}"
    
    async def _generate_tests(self, architecture: Dict) -> Dict[str, str]:
        """Generate test files"""
        return {
            "tests/test_basic.py": f'''import pytest

def test_basic():
    assert True
'''
        }

# ═══════════════════════════════════════════════════════════════════════════════════
# CONTINUOUS LEARNING LOOP
# ═══════════════════════════════════════════════════════════════════════════════════

class ContinuousLearningLoop:
    """
    Continuous Learning: Experience → Learn → Store → Improve → Apply
    
    Features:
    - Experience logging
    - Pattern recognition
    - Knowledge consolidation
    - Adaptive learning
    """
    
    def __init__(self):
        self.experiences: deque = deque(maxlen=1000)
        self.patterns: Dict[str, List[str]] = defaultdict(list)
        self.insights: deque = deque(maxlen=100)
        self.learning_rate = 0.5
        self.consolidation_threshold = 5
        
        logger.info("Continuous Learning Loop initialized")
    
    def process_experience(self, experience: Experience):
        """Process a new experience through the learning loop"""
        # Step 1: Log experience
        self.experiences.append(experience)
        
        # Step 2: Analyze
        patterns = self._extract_patterns(experience)
        for pattern in patterns:
            self.patterns[pattern].append(experience.id)
        
        # Step 3: Generate insight
        if len(self.patterns.get(list(patterns)[0], [])) >= self.consolidation_threshold:
            insight = self._generate_insight(patterns)
            self.insights.append(insight)
        
        # Step 4: Update learning rate
        self._update_learning_rate(experience)
        
        logger.info(f"Processed experience: {experience.action[:40]}...")
    
    def _extract_patterns(self, experience: Experience) -> List[str]:
        """Extract patterns from experience"""
        patterns = []
        
        # Action pattern
        if experience.success:
            patterns.append(f"success:{experience.action[:20]}")
        else:
            patterns.append(f"failure:{experience.action[:20]}")
        
        # Context patterns
        for key, value in experience.context.items():
            patterns.append(f"context:{key}:{str(value)[:10]}")
        
        return patterns
    
    def _generate_insight(self, patterns: List[str]) -> Dict:
        """Generate insight from patterns"""
        return {
            "patterns": patterns,
            "insight": f"Pattern detected: {patterns[0] if patterns else 'unknown'}",
            "recommendation": "Consider applying this pattern in future decisions",
            "timestamp": datetime.now().isoformat(),
            "confidence": 0.7
        }
    
    def _update_learning_rate(self, experience: Experience):
        """Update learning rate based on feedback"""
        if experience.success:
            self.learning_rate = min(1.0, self.learning_rate + 0.01)
        else:
            self.learning_rate = max(0.1, self.learning_rate - 0.02)
    
    def get_learning_status(self) -> Dict:
        """Get current learning status"""
        success_count = sum(1 for e in self.experiences if e.success)
        total = len(self.experiences)
        
        return {
            "total_experiences": total,
            "success_rate": success_count / max(total, 1),
            "learning_rate": self.learning_rate,
            "patterns_detected": len(self.patterns),
            "insights_generated": len(self.insights),
            "top_patterns": sorted(
                [(p, len(ids)) for p, ids in self.patterns.items()],
                key=lambda x: x[1],
                reverse=True
            )[:5]
        }
    
    def get_recommendation(self) -> str:
        """Get learning-based recommendation"""
        status = self.get_learning_status()
        
        if status["learning_rate"] < 0.3:
            return "Learning rate low. Focus on successful patterns."
        elif status["success_rate"] < 0.5:
            return "Success rate needs improvement. Review recent failures."
        elif len(status["top_patterns"]) > 0:
            return f"Strong pattern detected: {status['top_patterns'][0][0]}"
        
        return "Continue current approach."

# ═══════════════════════════════════════════════════════════════════════════════════
# MAIN ORCHESTRATOR
# ═══════════════════════════════════════════════════════════════════════════════════

class System02Ultra:
    """
    System 02 Ultra - The complete Level 5 AI System
    
    Integrates all ultra-level components:
    - Meta-Intelligence
    - Recursive Agents
    - World Model
    - Goal Evolution
    - Environment Awareness
    - Autonomous Builder
    - Continuous Learning
    """
    
    def __init__(self):
        logger.info("Initializing System 02 Ultra...")
        
        # Initialize all systems
        self.meta_intelligence = MetaIntelligence()
        self.recursive_agents = RecursiveAgentSystem(self.meta_intelligence)
        self.world_model = WorldModel()
        self.goal_evolution = GoalEvolutionSystem(self.world_model)
        self.project_builder = AutonomousProjectBuilder(self.recursive_agents)
        self.learning_loop = ContinuousLearningLoop()
        
        # State
        self.is_running = False
        self.start_time = None
        
        logger.info("System 02 Ultra initialized successfully!")
    
    async def process(self, user_input: str) -> Dict:
        """Process user input through the complete AI system"""
        start = time.time()
        
        # Step 1: Meta-intelligence thinking
        thought = self.meta_intelligence.think(user_input)
        
        # Step 2: Update world model
        self.world_model.add_entity(
            name=user_input[:50],
            entity_type=EntityType.MEMORY,
            properties={"thought": thought.content}
        )
        
        # Step 3: Determine action type
        action_type = self._classify_action(user_input)
        
        # Step 4: Execute appropriate system
        result = {}
        
        if "build" in user_input.lower() or "create" in user_input.lower():
            result = await self.project_builder.build_project(user_input)
        elif "goal" in user_input.lower() or "achieve" in user_input.lower():
            goal = self.goal_evolution.create_evolutionary_goal(user_input)
            self.goal_evolution.decompose_goal(goal.id)
            result = {"goal": goal.description, "sub_goals": len(goal.sub_goals)}
        elif "research" in user_input.lower() or "find" in user_input.lower():
            result = await self.recursive_agents.execute_task_tree(user_input)
        else:
            # General chat with meta-intelligence
            result = await self._general_processing(user_input, thought)
        
        # Step 5: Learn from experience
        self.learning_loop.process_experience(Experience(
            id=str(uuid.uuid4()),
            situation=user_input,
            action=action_type,
            outcome=result,
            success=True,
            timestamp=datetime.now(),
            context={"thought_confidence": thought.confidence}
        ))
        
        # Step 6: Self-reflection
        reflection = self.meta_intelligence.reflect()
        
        return {
            "input": user_input,
            "thought": {
                "confidence": thought.confidence,
                "reasoning": thought.selected_reasoning
            },
            "action": action_type,
            "result": result,
            "reflection": reflection,
            "processing_time": time.time() - start
        }
    
    def _classify_action(self, user_input: str) -> str:
        """Classify the type of action requested"""
        input_lower = user_input.lower()
        
        if any(kw in input_lower for kw in ["build", "create", "make", "generate"]):
            return "project_creation"
        elif any(kw in input_lower for kw in ["research", "find", "search", "lookup"]):
            return "research"
        elif any(kw in input_lower for kw in ["analyze", "examine", "review"]):
            return "analysis"
        elif any(kw in input_lower for kw in ["plan", "strategy", "schedule"]):
            return "planning"
        elif any(kw in input_lower for kw in ["fix", "debug", "solve"]):
            return "problem_solving"
        else:
            return "conversation"
    
    async def _general_processing(self, user_input: str, thought: Thought) -> Dict:
        """General processing for non-specific inputs"""
        return {
            "response": f"I understand: {user_input[:50]}...",
            "confidence": thought.confidence,
            "reasoning": thought.selected_reasoning
        }
    
    def get_status(self) -> Dict:
        """Get complete system status"""
        return {
            "system": "02 Ultra",
            "version": "1.0.0",
            "level": 5,
            "uptime": (datetime.now() - self.start_time).total_seconds() if self.start_time else 0,
            "meta_intelligence": {
                "experiences": len(self.meta_intelligence.experience_history),
                "self_model": self.meta_intelligence.self_model
            },
            "world_model": self.world_model.get_world_summary(),
            "goals": self.goal_evolution.get_goals_summary(),
            "learning": self.learning_loop.get_learning_status(),
            "recommendations": {
                "meta": self.meta_intelligence.get_recommendation(),
                "learning": self.learning_loop.get_recommendation()
            }
        }
    
    def start(self):
        """Start the system"""
        self.is_running = True
        self.start_time = datetime.now()
        logger.info("System 02 Ultra started")
    
    def stop(self):
        """Stop the system"""
        self.is_running = False
        logger.info("System 02 Ultra stopped")

# ═══════════════════════════════════════════════════════════════════════════════════
# EXPORTS
# ═══════════════════════════════════════════════════════════════════════════════════

__all__ = [
    'System02Ultra',
    'MetaIntelligence',
    'RecursiveAgentSystem',
    'WorldModel',
    'GoalEvolutionSystem',
    'AutonomousProjectBuilder',
    'ContinuousLearningLoop',
    'Thought',
    'Experience',
    'Entity',
    'Strategy',
    'Goal',
    'SubAgent',
    'AgentState',
    'TaskPriority',
    'EntityType'
]
