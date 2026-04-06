"""
============================================================
LEARNING LOOP - Continuous Improvement System
============================================================
Evaluates performance and improves decision-making
"""

import json
import os
from typing import Dict, Any, List
from datetime import datetime
from dataclasses import dataclass
import logging

logger = logging.getLogger("LearningLoop")


@dataclass
class Feedback:
    goal_id: str
    score: float  # 0-1
    feedback_type: str  # success, failure, improvement
    comment: str
    timestamp: datetime


class LearningLoop:
    """
    Continuous learning system that:
    - Evaluates execution outcomes
    - Stores successful strategies
    - Identifies patterns for improvement
    - Adapts to user preferences
    """
    
    def __init__(self, data_dir: str = "data/logs"):
        self.data_dir = data_dir
        self.feedback_history: List[Feedback] = []
        self.performance_metrics = {
            "total_executions": 0,
            "successful_executions": 0,
            "failed_executions": 0,
            "average_score": 0.0
        }
        
        self._load_metrics()
    
    async def record_execution(self, goal: Any, results: List[Any]) -> None:
        """Record execution for learning"""
        
        self.performance_metrics["total_executions"] += 1
        
        # Determine success
        success = all(r.get("success", False) for r in results if isinstance(r, dict))
        
        if success:
            self.performance_metrics["successful_executions"] += 1
        else:
            self.performance_metrics["failed_executions"] += 1
        
        # Calculate score
        success_rate = self.performance_metrics["successful_executions"] / self.performance_metrics["total_executions"]
        self.performance_metrics["average_score"] = success_rate
        
        # Store feedback
        feedback = Feedback(
            goal_id=goal.id,
            score=success_rate,
            feedback_type="success" if success else "failure",
            comment=f"Goal '{goal.description[:50]}' completed",
            timestamp=datetime.now()
        )
        
        self.feedback_history.append(feedback)
        
        # Save metrics
        self._save_metrics()
        
        logger.info(f"Recorded execution: {goal.id} - {'Success' if success else 'Failed'}")
    
    async def record_feedback(self, goal_id: str, score: float, comment: str = "") -> None:
        """Record user feedback"""
        
        feedback = Feedback(
            goal_id=goal_id,
            score=score,
            feedback_type="feedback",
            comment=comment,
            timestamp=datetime.now()
        )
        
        self.feedback_history.append(feedback)
        
        # Update metrics
        self.performance_metrics["average_score"] = (
            self.performance_metrics["average_score"] + score
        ) / 2
        
        self._save_metrics()
    
    def get_performance_report(self) -> Dict[str, Any]:
        """Get performance analysis report"""
        
        recent_feedback = self.feedback_history[-20:]
        
        return {
            "metrics": self.performance_metrics,
            "success_rate": (
                self.performance_metrics["successful_executions"] / 
                max(1, self.performance_metrics["total_executions"])
            ),
            "recent_trend": self._calculate_trend(),
            "total_feedback": len(self.feedback_history),
            "recommendations": self._generate_recommendations()
        }
    
    def _calculate_trend(self) -> str:
        """Calculate performance trend"""
        
        if len(self.feedback_history) < 5:
            return "insufficient_data"
        
        recent = [f.score for f in self.feedback_history[-5:]]
        older = [f.score for f in self.feedback_history[-10:-5]] if len(self.feedback_history) >= 10 else recent
        
        recent_avg = sum(recent) / len(recent)
        older_avg = sum(older) / len(older)
        
        if recent_avg > older_avg + 0.1:
            return "improving"
        elif recent_avg < older_avg - 0.1:
            return "declining"
        else:
            return "stable"
    
    def _generate_recommendations(self) -> List[str]:
        """Generate improvement recommendations"""
        
        recommendations = []
        
        success_rate = (
            self.performance_metrics["successful_executions"] / 
            max(1, self.performance_metrics["total_executions"])
        )
        
        if success_rate < 0.7:
            recommendations.append("Success rate is below 70%. Consider reviewing error patterns.")
        
        if self.performance_metrics["total_executions"] < 10:
            recommendations.append("System is still learning. More interactions will improve accuracy.")
        
        if recommendations:
            return recommendations
        
        return ["Performance is good. Continue using to improve."]
    
    def get_learning_insights(self) -> Dict[str, Any]:
        """Get insights from learning data"""
        
        if not self.feedback_history:
            return {"insights": ["No learning data yet"], "patterns": []}
        
        # Analyze patterns
        patterns = {
            "common_failures": [],
            "strengths": [],
            "areas_for_improvement": []
        }
        
        # Find common failures
        failure_types = {}
        for fb in self.feedback_history:
            if fb.score < 0.5:
                failure_types[fb.feedback_type] = failure_types.get(fb.feedback_type, 0) + 1
        
        patterns["common_failures"] = [
            {"type": k, "count": v} 
            for k, v in sorted(failure_types.items(), key=lambda x: x[1], reverse=True)[:5]
        ]
        
        # Calculate strengths
        if self.performance_metrics["successful_executions"] > 5:
            patterns["strengths"].append("Consistent successful executions")
        
        return {
            "insights": [
                f"Total executions: {self.performance_metrics['total_executions']}",
                f"Success rate: {success_rate:.1%}",
                f"Performance trend: {self._calculate_trend()}"
            ],
            "patterns": patterns,
            "timestamp": datetime.now().isoformat()
        }
    
    def _load_metrics(self) -> None:
        """Load metrics from disk"""
        metrics_file = os.path.join(self.data_dir, "metrics.json")
        
        if os.path.exists(metrics_file):
            try:
                with open(metrics_file, 'r') as f:
                    data = json.load(f)
                    self.performance_metrics = data.get("metrics", self.performance_metrics)
            except Exception as e:
                logger.error(f"Error loading metrics: {e}")
    
    def _save_metrics(self) -> None:
        """Save metrics to disk"""
        os.makedirs(self.data_dir, exist_ok=True)
        metrics_file = os.path.join(self.data_dir, "metrics.json")
        
        data = {
            "metrics": self.performance_metrics,
            "last_updated": datetime.now().isoformat()
        }
        
        with open(metrics_file, 'w') as f:
            json.dump(data, f, indent=2)
