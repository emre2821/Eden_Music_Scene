"""
Adaptive Controls & Feedback Processing Engine
Real-time processing of user feedback for adaptive playback control
"""

import asyncio
import uuid
from datetime import datetime
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field
from enum import Enum
import structlog
import numpy as np
from collections import deque

from ..ethical_framework import EthicalAI

logger = structlog.get_logger(__name__)


class FeedbackType(Enum):
    """Types of user feedback"""
    EMOTIONAL_RESPONSE = "emotional_response"
    SATISFACTION_RATING = "satisfaction_rating"
    SKIP_ACTION = "skip_action"
    VOLUME_ADJUSTMENT = "volume_adjustment"
    REPLAY_REQUEST = "replay_request"
    PAUSE_ACTION = "pause_action"
    HEARTBEAT = "heartbeat"
    CUSTOM = "custom"


class AdaptationStrategy(Enum):
    """Strategies for adapting to feedback"""
    IMMEDIATE = "immediate"
    GRADUAL = "gradual"
    CONSERVATIVE = "conservative"
    AGGRESSIVE = "aggressive"
    CONTEXTUAL = "contextual"


@dataclass
class FeedbackEvent:
    """User feedback event"""
    id: str
    timestamp: datetime
    type: FeedbackType
    session_id: str
    track_id: str
    playback_position: float
    data: Dict[str, Any]
    confidence: float = 1.0
    context: Dict[str, Any] = field(default_factory=dict)


@dataclass
class AdaptationRule:
    """Rule for adapting to feedback"""
    id: str
    feedback_type: FeedbackType
    conditions: Dict[str, Any]
    actions: List[Dict[str, Any]]
    priority: int = 0
    cooldown_period: float = 0.0  # seconds
    last_triggered: Optional[datetime] = None


@dataclass
class UserPreferenceProfile:
    """User's playback preferences and learned patterns"""
    user_id: str
    emotional_sensitivity: float = 0.7
    volume_preference: float = 0.8
    tempo_preference: float = 1.0
    crossfade_preference: float = 0.5
    genre_preferences: Dict[str, float] = field(default_factory=dict)
    time_preferences: Dict[str, float] = field(default_factory=dict)
    learned_patterns: List[Dict[str, Any]] = field(default_factory=list)
    last_updated: datetime = field(default_factory=datetime.utcnow)


class FeedbackProcessor:
    """
    Real-time feedback processing and adaptation engine
    
    Processes user feedback and applies adaptive changes to playback
    while maintaining ethical standards and user autonomy.
    """
    
    def __init__(self):
        self.feedback_queue: asyncio.Queue = asyncio.Queue()
        self.processed_feedback: Dict[str, deque] = {}
        self.adaptation_rules: List[AdaptationRule] = []
        self.user_profiles: Dict[str, UserPreferenceProfile] = {}
        self.ethical_ai = EthicalAI()
        
        # Processing parameters
        self.max_feedback_history = 1000
        self.processing_batch_size = 10
        self.processing_interval = 0.1  # seconds
        
        # Initialize default adaptation rules
        self._initialize_default_rules()
        
        # Start background processing
        asyncio.create_task(self._feedback_processing_loop())
        
        logger.info("FeedbackProcessor initialized")
    
    async def submit_feedback(self, feedback_data: Dict[str, Any]) -> str:
        """
        Submit user feedback for processing
        
        Args:
            feedback_data: Feedback information
        
        Returns:
            Feedback event ID
        """
        try:
            # Validate ethical compliance
            is_permitted, violations = await self.ethical_ai.evaluate_action(
                "submit_feedback", feedback_data
            )
            
            if not is_permitted:
                logger.warning("Ethical violations in feedback submission")
                raise ValueError("Feedback submission not permitted due to ethical constraints")
            
            # Create feedback event
            feedback_event = FeedbackEvent(
                id=str(uuid.uuid4()),
                timestamp=datetime.utcnow(),
                type=FeedbackType(feedback_data.get("type", "custom")),
                session_id=feedback_data.get("session_id", ""),
                track_id=feedback_data.get("track_id", ""),
                playback_position=feedback_data.get("playback_position", 0.0),
                data=feedback_data.get("data", {}),
                confidence=feedback_data.get("confidence", 1.0),
                context=feedback_data.get("context", {})
            )
            
            # Add to processing queue
            await self.feedback_queue.put(feedback_event)
            
            # Store in history
            if feedback_event.session_id not in self.processed_feedback:
                self.processed_feedback[feedback_event.session_id] = deque(maxlen=self.max_feedback_history)
            
            self.processed_feedback[feedback_event.session_id].append(feedback_event)
            
            logger.debug(f"Submitted feedback event {feedback_event.id}")
            
            return feedback_event.id
            
        except Exception as e:
            logger.error(f"Error submitting feedback: {e}")
            raise
    
    async def process_feedback_batch(self, feedback_events: List[FeedbackEvent]) -> List[Dict[str, Any]]:
        """
        Process a batch of feedback events
        
        Args:
            feedback_events: List of feedback events to process
        
        Returns:
            List of adaptation actions to take
        """
        adaptations = []
        
        try:
            # Group feedback by session
            sessions_feedback = {}
            for event in feedback_events:
                if event.session_id not in sessions_feedback:
                    sessions_feedback[event.session_id] = []
                sessions_feedback[event.session_id].append(event)
            
            # Process each session's feedback
            for session_id, session_feedback in sessions_feedback.items():
                session_adaptations = await self._process_session_feedback(session_id, session_feedback)
                adaptations.extend(session_adaptations)
            
            # Learn from feedback patterns
            await self._learn_from_feedback(feedback_events)
            
            return adaptations
            
        except Exception as e:
            logger.error(f"Error processing feedback batch: {e}")
            return []
    
    async def get_user_profile(self, user_id: str) -> UserPreferenceProfile:
        """Get or create user preference profile"""
        if user_id not in self.user_profiles:
            self.user_profiles[user_id] = UserPreferenceProfile(user_id=user_id)
        
        return self.user_profiles[user_id]
    
    async def update_user_profile(self, user_id: str, updates: Dict[str, Any]) -> Dict[str, Any]:
        """Update user preference profile"""
        try:
            profile = await self.get_user_profile(user_id)
            
            # Update basic preferences
            for key in ["emotional_sensitivity", "volume_preference", "tempo_preference", "crossfade_preference"]:
                if key in updates:
                    setattr(profile, key, max(0.0, min(1.0, updates[key])))
            
            # Update genre preferences
            if "genre_preferences" in updates:
                profile.genre_preferences.update(updates["genre_preferences"])
            
            # Update time preferences
            if "time_preferences" in updates:
                profile.time_preferences.update(updates["time_preferences"])
            
            profile.last_updated = datetime.utcnow()
            
            return {
                "user_id": user_id,
                "updated_fields": list(updates.keys()),
                "last_updated": profile.last_updated.isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error updating user profile: {e}")
            raise
    
    async def get_feedback_analytics(self, session_id: str, time_window: Optional[timedelta] = None) -> Dict[str, Any]:
        """Get analytics for feedback in a session"""
        try:
            feedback_history = self.processed_feedback.get(session_id, [])
            
            if time_window:
                cutoff_time = datetime.utcnow() - time_window
                recent_feedback = [f for f in feedback_history if f.timestamp > cutoff_time]
            else:
                recent_feedback = list(feedback_history)
            
            if not recent_feedback:
                return {
                    "session_id": session_id,
                    "feedback_count": 0,
                    "message": "No feedback found for session"
                }
            
            # Analyze feedback patterns
            feedback_by_type = {}
            satisfaction_scores = []
            engagement_levels = []
            
            for feedback in recent_feedback:
                # Group by type
                feedback_type = feedback.type.value
                if feedback_type not in feedback_by_type:
                    feedback_by_type[feedback_type] = []
                feedback_by_type[feedback_type].append(feedback)
                
                # Extract satisfaction scores
                if feedback.type == FeedbackType.SATISFACTION_RATING:
                    satisfaction_scores.append(feedback.data.get("rating", 0.5))
                
                # Extract engagement levels
                if feedback.type == FeedbackType.HEARTBEAT:
                    engagement_levels.append(feedback.data.get("engagement", 0.5))
            
            # Calculate analytics
            analytics = {
                "session_id": session_id,
                "total_feedback": len(recent_feedback),
                "feedback_by_type": {k: len(v) for k, v in feedback_by_type.items()},
                "time_range": {
                    "start": min(f.timestamp for f in recent_feedback).isoformat(),
                    "end": max(f.timestamp for f in recent_feedback).isoformat()
                },
                "feedback_intensity": np.mean([f.confidence for f in recent_feedback])
            }
            
            if satisfaction_scores:
                analytics["satisfaction_metrics"] = {
                    "average": np.mean(satisfaction_scores),
                    "trend": self._calculate_trend(satisfaction_scores),
                    "variance": np.var(satisfaction_scores)
                }
            
            if engagement_levels:
                analytics["engagement_metrics"] = {
                    "average": np.mean(engagement_levels),
                    "trend": self._calculate_trend(engagement_levels),
                    "variance": np.var(engagement_levels)
                }
            
            return analytics
            
        except Exception as e:
            logger.error(f"Error getting feedback analytics: {e}")
            return {"error": str(e)}
    
    async def add_adaptation_rule(self, rule_data: Dict[str, Any]) -> str:
        """Add a new adaptation rule"""
        try:
            rule = AdaptationRule(
                id=str(uuid.uuid4()),
                feedback_type=FeedbackType(rule_data["feedback_type"]),
                conditions=rule_data["conditions"],
                actions=rule_data["actions"],
                priority=rule_data.get("priority", 0),
                cooldown_period=rule_data.get("cooldown_period", 0.0)
            )
            
            self.adaptation_rules.append(rule)
            self.adaptation_rules.sort(key=lambda r: r.priority, reverse=True)
            
            logger.info(f"Added adaptation rule {rule.id}")
            return rule.id
            
        except Exception as e:
            logger.error(f"Error adding adaptation rule: {e}")
            raise
    
    async def _feedback_processing_loop(self):
        """Background loop for processing feedback"""
        while True:
            try:
                # Collect feedback events
                feedback_batch = []
                
                # Get events from queue
                for _ in range(self.processing_batch_size):
                    try:
                        event = await asyncio.wait_for(
                            self.feedback_queue.get(), 
                            timeout=self.processing_interval
                        )
                        feedback_batch.append(event)
                    except asyncio.TimeoutError:
                        break
                
                # Process batch if not empty
                if feedback_batch:
                    adaptations = await self.process_feedback_batch(feedback_batch)
                    
                    # Apply adaptations (would be sent to playback engine)
                    for adaptation in adaptations:
                        logger.debug(f"Adaptation to apply: {adaptation}")
                
                # Small delay to prevent busy waiting
                await asyncio.sleep(self.processing_interval)
                
            except Exception as e:
                logger.error(f"Error in feedback processing loop: {e}")
                await asyncio.sleep(1.0)  # Wait before retrying
    
    async def _process_session_feedback(self, session_id: str, feedback_events: List[FeedbackEvent]) -> List[Dict[str, Any]]:
        """Process feedback for a specific session"""
        adaptations = []
        
        # Group feedback by type
        feedback_by_type = {}
        for event in feedback_events:
            if event.type not in feedback_by_type:
                feedback_by_type[event.type] = []
            feedback_by_type[event.type].append(event)
        
        # Apply adaptation rules
        for rule in self.adaptation_rules:
            if rule.feedback_type in feedback_by_type:
                relevant_feedback = feedback_by_type[rule.feedback_type]
                
                # Check if rule conditions are met
                if await self._check_rule_conditions(rule, relevant_feedback):
                    # Check cooldown
                    if (rule.last_triggered is None or 
                        (datetime.utcnow() - rule.last_triggered).total_seconds() > rule.cooldown_period):
                        
                    # Generate adaptations
                    rule_adaptations = await self._generate_rule_adaptations(rule, relevant_feedback)
                    adaptations.extend(rule_adaptations)
                    
                    rule.last_triggered = datetime.utcnow()
        
        return adaptations
    
    async def _check_rule_conditions(self, rule: AdaptationRule, feedback_events: List[FeedbackEvent]) -> bool:
        """Check if rule conditions are met"""
        try:
            conditions = rule.conditions
            
            # Check minimum event count
            if "min_events" in conditions:
                if len(feedback_events) < conditions["min_events"]:
                    return False
            
            # Check average confidence
            if "min_confidence" in conditions:
                avg_confidence = np.mean([e.confidence for e in feedback_events])
                if avg_confidence < conditions["min_confidence"]:
                    return False
            
            # Check specific data conditions
            if "data_conditions" in conditions:
                for condition in conditions["data_conditions"]:
                    if not await self._check_data_condition(condition, feedback_events):
                        return False
            
            return True
            
        except Exception as e:
            logger.error(f"Error checking rule conditions: {e}")
            return False
    
    async def _generate_rule_adaptations(self, rule: AdaptationRule, feedback_events: List[FeedbackEvent]) -> List[Dict[str, Any]]:
        """Generate adaptation actions based on rule"""
        adaptations = []
        
        for action in rule.actions:
            adaptation = {
                "type": action["type"],
                "session_id": feedback_events[0].session_id,
                "track_id": feedback_events[0].track_id,
                "priority": rule.priority,
                "timestamp": datetime.utcnow().isoformat()
            }
            
            # Add action-specific parameters
            if "parameters" in action:
                adaptation["parameters"] = action["parameters"]
            
            # Calculate adaptation magnitude based on feedback intensity
            if "intensity_based" in action and action["intensity_based"]:
                avg_confidence = np.mean([e.confidence for e in feedback_events])
                adaptation["magnitude"] = avg_confidence * action.get("max_magnitude", 1.0)
            
            adaptations.append(adaptation)
        
        return adaptations
    
    async def _learn_from_feedback(self, feedback_events: List[FeedbackEvent]):
        """Learn patterns from feedback for future adaptation"""
        try:
            for event in feedback_events:
                user_id = event.context.get("user_id")
                if not user_id:
                    continue
                
                profile = await self.get_user_profile(user_id)
                
                # Learn from satisfaction ratings
                if event.type == FeedbackType.SATISFACTION_RATING:
                    rating = event.data.get("rating", 0.5)
                    
                    # Adjust emotional sensitivity based on satisfaction
                    if rating > 0.8:
                        profile.emotional_sensitivity = min(1.0, profile.emotional_sensitivity + 0.05)
                    elif rating < 0.3:
                        profile.emotional_sensitivity = max(0.1, profile.emotional_sensitivity - 0.05)
                
                # Learn from volume adjustments
                elif event.type == FeedbackType.VOLUME_ADJUSTMENT:
                    volume_change = event.data.get("volume_change", 0.0)
                    profile.volume_preference = max(0.1, min(1.0, profile.volume_preference + volume_change * 0.1))
                
                # Store learned pattern
                pattern = {
                    "timestamp": event.timestamp.isoformat(),
                    "feedback_type": event.type.value,
                    "context": event.context,
                    "data": event.data
                }
                profile.learned_patterns.append(pattern)
                
                # Keep only recent patterns
                if len(profile.learned_patterns) > 100:
                    profile.learned_patterns = profile.learned_patterns[-100:]
        
        except Exception as e:
            logger.error(f"Error learning from feedback: {e}")
    
    def _initialize_default_rules(self):
        """Initialize default adaptation rules"""
        default_rules = [
            {
                "feedback_type": "skip_action",
                "conditions": {"min_events": 2, "time_window": 30},
                "actions": [
                    {"type": "adjust_tempo", "parameters": {"increase": 0.1}, "intensity_based": True},
                    {"type": "suggest_genre_change", "parameters": {"explore_new": True}}
                ],
                "priority": 10,
                "cooldown_period": 60
            },
            {
                "feedback_type": "satisfaction_rating",
                "conditions": {"min_events": 1, "data_conditions": [{"field": "rating", "operator": "less_than", "value": 0.3}]},
                "actions": [
                    {"type": "reduce_intensity", "parameters": {"factor": 0.8}},
                    {"type": "suggest_mood_shift", "parameters": {"direction": "positive"}}
                ],
                "priority": 8,
                "cooldown_period": 30
            },
            {
                "feedback_type": "volume_adjustment",
                "conditions": {"min_events": 1},
                "actions": [
                    {"type": "adjust_volume", "parameters": {"follow_user": True}, "intensity_based": True}
                ],
                "priority": 5,
                "cooldown_period": 10
            }
        ]
        
        for rule_data in default_rules:
            asyncio.create_task(self.add_adaptation_rule(rule_data))
    
    def _calculate_trend(self, values: List[float]) -> str:
        """Calculate trend in a series of values"""
        if len(values) < 2:
            return "stable"
        
        # Simple linear regression slope
        x = np.arange(len(values))
        slope = np.polyfit(x, values, 1)[0]
        
        if slope > 0.1:
            return "increasing"
        elif slope < -0.1:
            return "decreasing"
        else:
            return "stable"
    
    async def _check_data_condition(self, condition: Dict[str, Any], feedback_events: List[FeedbackEvent]) -> bool:
        """Check if data condition is met across feedback events"""
        try:
            field = condition["field"]
            operator = condition["operator"]
            value = condition["value"]
            
            for event in feedback_events:
                field_value = event.data.get(field)
                if field_value is None:
                    continue
                
                if operator == "greater_than" and field_value > value:
                    return True
                elif operator == "less_than" and field_value < value:
                    return True
                elif operator == "equals" and field_value == value:
                    return True
                elif operator == "in_range" and value[0] <= field_value <= value[1]:
                    return True
            
            return False
            
        except Exception as e:
            logger.error(f"Error checking data condition: {e}")
            return False