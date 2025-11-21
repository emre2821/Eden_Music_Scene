"""
Emotional Timeline Engine
Manages emotional progression and adaptive playback timing
"""

import asyncio
import uuid
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field
from enum import Enum
import structlog
import numpy as np
from scipy import interpolate

logger = structlog.get_logger(__name__)


class TimelineMode(Enum):
    """Modes of emotional timeline progression"""
    LINEAR = "linear"
    CURVED = "curved"
    ADAPTIVE = "adaptive"
    RESPONSIVE = "responsive"
    CUSTOM = "custom"


class EmotionalArcType(Enum):
    """Types of emotional arcs"""
    ASCENDING = "ascending"
    DESCENDING = "descending"
    PEAKED = "peaked"
    VALLEY = "valley"
    WAVE = "wave"
    STABLE = "stable"


@dataclass
class EmotionalWaypoint:
    """Waypoint in emotional timeline"""
    timestamp: float  # Position in timeline (0.0 to 1.0)
    valence: float  # Pleasantness (-1.0 to 1.0)
    arousal: float  # Energy level (0.0 to 1.0)
    dominance: float  # Control (0.0 to 1.0)
    intensity: float  # Emotional intensity (0.0 to 1.0)
    duration: float = 0.0  # Duration at this state
    transition_curve: str = "smooth"  # Transition curve type


@dataclass
class TimelineSegment:
    """Segment of emotional timeline"""
    id: str
    start_time: float
    end_time: float
    start_emotion: Dict[str, float]
    end_emotion: Dict[str, float]
    curve_type: str = "linear"
    adaptive_parameters: Dict[str, Any] = field(default_factory=dict)


@dataclass
class EmotionalTimelineState:
    """Current state of emotional timeline"""
    current_position: float = 0.0
    current_emotion: Dict[str, float] = field(default_factory=lambda: {"valence": 0.5, "arousal": 0.5, "dominance": 0.5, "intensity": 0.5})
    target_emotion: Dict[str, float] = field(default_factory=lambda: {"valence": 0.5, "arousal": 0.5, "dominance": 0.5, "intensity": 0.5})
    progression_rate: float = 1.0
    adaptive_mode: bool = True
    last_update: datetime = field(default_factory=datetime.utcnow)


class EmotionalTimelineEngine:
    """
    Emotional Timeline Engine
    
    Manages the progression of emotional states during playback,
    providing adaptive timing and emotional arc management.
    """
    
    def __init__(self):
        self.active_timelines: Dict[str, EmotionalTimelineState] = {}
        self.waypoint_cache: Dict[str, List[EmotionalWaypoint]] = {}
        self.segment_cache: Dict[str, List[TimelineSegment]] = {}
        
        # Default timeline parameters
        self.default_progression_rate = 1.0
        self.adaptation_sensitivity = 0.3
        self.smoothing_factor = 0.8
        
        logger.info("EmotionalTimelineEngine initialized")
    
    async def create_timeline(self,
                            session_id: str,
                            total_duration: float,
                            mode: TimelineMode = TimelineMode.ADAPTIVE,
                            initial_emotion: Optional[Dict[str, float]] = None,
                            target_emotion: Optional[Dict[str, float]] = None,
                            waypoints: Optional[List[EmotionalWaypoint]] = None) -> str:
        """
        Create a new emotional timeline
        
        Args:
            session_id: Associated playback session
            total_duration: Total timeline duration
            mode: Timeline progression mode
            initial_emotion: Starting emotional state
            target_emotion: Target emotional state
            waypoints: Key emotional waypoints
        
        Returns:
            Timeline ID
        """
        try:
            timeline_id = str(uuid.uuid4())
            
            # Create initial state
            initial_state = EmotionalTimelineState(
                current_position=0.0,
                current_emotion=initial_emotion or {"valence": 0.5, "arousal": 0.5, "dominance": 0.5, "intensity": 0.5},
                target_emotion=target_emotion or {"valence": 0.6, "arousal": 0.6, "dominance": 0.6, "intensity": 0.6},
                progression_rate=self.default_progression_rate,
                adaptive_mode=(mode == TimelineMode.ADAPTIVE or mode == TimelineMode.RESPONSIVE)
            )
            
            self.active_timelines[timeline_id] = initial_state
            
            # Store waypoints if provided
            if waypoints:
                self.waypoint_cache[timeline_id] = waypoints
            
            # Generate default waypoints if not provided
            else:
                default_waypoints = await self._generate_default_waypoints(
                    total_duration, initial_state.current_emotion, initial_state.target_emotion
                )
                self.waypoint_cache[timeline_id] = default_waypoints
            
            # Create timeline segments
            segments = await self._create_timeline_segments(
                timeline_id, total_duration, mode
            )
            self.segment_cache[timeline_id] = segments
            
            logger.info(f"Created emotional timeline {timeline_id}", extra={
                "session_id": session_id,
                "mode": mode.value,
                "duration": total_duration,
                "waypoints": len(waypoints) if waypoints else len(default_waypoints)
            })
            
            return timeline_id
            
        except Exception as e:
            logger.error(f"Error creating timeline: {e}")
            raise
    
    async def advance_timeline(self, timeline_id: str, time_delta: float, user_feedback: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Advance timeline by time delta with optional user feedback
        
        Args:
            timeline_id: Timeline ID
            time_delta: Time to advance (seconds)
            user_feedback: Optional user feedback for adaptation
        
        Returns:
            Current timeline state
        """
        try:
            timeline = self.active_timelines.get(timeline_id)
            if not timeline:
                raise ValueError(f"Timeline {timeline_id} not found")
            
            # Apply user feedback if provided
            if user_feedback and timeline.adaptive_mode:
                await self._apply_user_feedback(timeline, user_feedback)
            
            # Calculate new position
            time_delta *= timeline.progression_rate
            timeline.current_position += time_delta
            
            # Update current emotion based on position
            new_emotion = await self._calculate_emotion_at_position(timeline_id, timeline.current_position)
            
            # Apply smoothing to avoid jarring changes
            timeline.current_emotion = self._smooth_emotion_transition(
                timeline.current_emotion, new_emotion
            )
            
            timeline.last_update = datetime.utcnow()
            
            return {
                "timeline_id": timeline_id,
                "current_position": timeline.current_position,
                "current_emotion": timeline.current_emotion,
                "target_emotion": timeline.target_emotion,
                "progression_rate": timeline.progression_rate,
                "adaptive_mode": timeline.adaptive_mode
            }
            
        except Exception as e:
            logger.error(f"Error advancing timeline: {e}")
            raise
    
    async def adapt_timeline(self, timeline_id: str, adaptation_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Adapt timeline based on real-time feedback
        
        Args:
            timeline_id: Timeline ID
            adaptation_data: Data for adaptation
        
        Returns:
            Updated timeline state
        """
        try:
            timeline = self.active_timelines.get(timeline_id)
            if not timeline:
                raise ValueError(f"Timeline {timeline_id} not found")
            
            # Adapt target emotion
            if "new_target_emotion" in adaptation_data:
                timeline.target_emotion = adaptation_data["new_target_emotion"]
            
            # Adapt progression rate
            if "progression_adjustment" in adaptation_data:
                adjustment = adaptation_data["progression_adjustment"]
                timeline.progression_rate = max(0.1, min(3.0, timeline.progression_rate + adjustment))
            
            # Add new waypoints if provided
            if "new_waypoints" in adaptation_data:
                new_waypoints = adaptation_data["new_waypoints"]
                if timeline_id in self.waypoint_cache:
                    self.waypoint_cache[timeline_id].extend(new_waypoints)
                    # Re-sort by timestamp
                    self.waypoint_cache[timeline_id].sort(key=lambda w: w.timestamp)
            
            # Recalculate segments if waypoints changed
            if "new_waypoints" in adaptation_data:
                segments = await self._create_timeline_segments(
                    timeline_id, None, TimelineMode.ADAPTIVE
                )
                self.segment_cache[timeline_id] = segments
            
            logger.info(f"Adapted timeline {timeline_id}", extra=adaptation_data)
            
            return {
                "timeline_id": timeline_id,
                "adaptation_applied": True,
                "current_state": {
                    "current_position": timeline.current_position,
                    "current_emotion": timeline.current_emotion,
                    "target_emotion": timeline.target_emotion,
                    "progression_rate": timeline.progression_rate
                }
            }
            
        except Exception as e:
            logger.error(f"Error adapting timeline: {e}")
            raise
    
    async def get_timeline_state(self, timeline_id: str) -> Dict[str, Any]:
        """Get current timeline state"""
        try:
            timeline = self.active_timelines.get(timeline_id)
            if not timeline:
                raise ValueError(f"Timeline {timeline_id} not found")
            
            # Calculate emotional arc type
            arc_type = await self._determine_emotional_arc(timeline)
            
            # Calculate progression metrics
            progression_metrics = await self._calculate_progression_metrics(timeline_id)
            
            return {
                "timeline_id": timeline_id,
                "current_position": timeline.current_position,
                "current_emotion": timeline.current_emotion,
                "target_emotion": timeline.target_emotion,
                "progression_rate": timeline.progression_rate,
                "adaptive_mode": timeline.adaptive_mode,
                "emotional_arc_type": arc_type.value,
                "progression_metrics": progression_metrics,
                "last_update": timeline.last_update.isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error getting timeline state: {e}")
            raise
    
    async def get_emotional_journey(self, timeline_id: str) -> Dict[str, Any]:
        """Get complete emotional journey data"""
        try:
            timeline = self.active_timelines.get(timeline_id)
            if not timeline:
                raise ValueError(f"Timeline {timeline_id} not found")
            
            waypoints = self.waypoint_cache.get(timeline_id, [])
            segments = self.segment_cache.get(timeline_id, [])
            
            # Generate journey visualization data
            journey_data = await self._generate_journey_data(timeline_id)
            
            return {
                "timeline_id": timeline_id,
                "waypoints": [
                    {
                        "timestamp": w.timestamp,
                        "valence": w.valence,
                        "arousal": w.arousal,
                        "dominance": w.dominance,
                        "intensity": w.intensity,
                        "duration": w.duration,
                        "transition_curve": w.transition_curve
                    }
                    for w in waypoints
                ],
                "segments": [
                    {
                        "id": s.id,
                        "start_time": s.start_time,
                        "end_time": s.end_time,
                        "start_emotion": s.start_emotion,
                        "end_emotion": s.end_emotion,
                        "curve_type": s.curve_type
                    }
                    for s in segments
                ],
                "journey_data": journey_data,
                "current_state": {
                    "position": timeline.current_position,
                    "emotion": timeline.current_emotion
                }
            }
            
        except Exception as e:
            logger.error(f"Error getting emotional journey: {e}")
            raise
    
    async def cleanup_timeline(self, timeline_id: str):
        """Clean up timeline resources"""
        try:
            if timeline_id in self.active_timelines:
                del self.active_timelines[timeline_id]
            
            if timeline_id in self.waypoint_cache:
                del self.waypoint_cache[timeline_id]
            
            if timeline_id in self.segment_cache:
                del self.segment_cache[timeline_id]
            
            logger.info(f"Cleaned up timeline {timeline_id}")
            
        except Exception as e:
            logger.error(f"Error cleaning up timeline {timeline_id}: {e}")
    
    async def _generate_default_waypoints(self, total_duration: float, 
                                        initial_emotion: Dict[str, float], 
                                        target_emotion: Dict[str, float]) -> List[EmotionalWaypoint]:
        """Generate default emotional waypoints"""
        waypoints = []
        
        # Start waypoint
        waypoints.append(EmotionalWaypoint(
            timestamp=0.0,
            valence=initial_emotion.get("valence", 0.5),
            arousal=initial_emotion.get("arousal", 0.5),
            dominance=initial_emotion.get("dominance", 0.5),
            intensity=initial_emotion.get("intensity", 0.5),
            duration=0.0,
            transition_curve="smooth"
        ))
        
        # Middle waypoint (emotional peak or valley)
        middle_emotion = {
            "valence": (initial_emotion.get("valence", 0.5) + target_emotion.get("valence", 0.6)) / 2 + 0.1,
            "arousal": max(initial_emotion.get("arousal", 0.5), target_emotion.get("arousal", 0.6)) + 0.1,
            "dominance": (initial_emotion.get("dominance", 0.5) + target_emotion.get("dominance", 0.6)) / 2,
            "intensity": 0.8
        }
        
        waypoints.append(EmotionalWaypoint(
            timestamp=0.5,
            valence=middle_emotion["valence"],
            arousal=middle_emotion["arousal"],
            dominance=middle_emotion["dominance"],
            intensity=middle_emotion["intensity"],
            duration=total_duration * 0.2,
            transition_curve="curved"
        ))
        
        # End waypoint
        waypoints.append(EmotionalWaypoint(
            timestamp=1.0,
            valence=target_emotion.get("valence", 0.6),
            arousal=target_emotion.get("arousal", 0.6),
            dominance=target_emotion.get("dominance", 0.6),
            intensity=target_emotion.get("intensity", 0.6),
            duration=0.0,
            transition_curve="smooth"
        ))
        
        return waypoints
    
    async def _create_timeline_segments(self, timeline_id: str, total_duration: float, mode: TimelineMode) -> List[TimelineSegment]:
        """Create timeline segments from waypoints"""
        waypoints = self.waypoint_cache.get(timeline_id, [])
        segments = []
        
        if len(waypoints) < 2:
            # Create simple linear segment
            timeline = self.active_timelines[timeline_id]
            segment = TimelineSegment(
                id=str(uuid.uuid4()),
                start_time=0.0,
                end_time=total_duration or 3600.0,  # Default 1 hour
                start_emotion=timeline.current_emotion,
                end_emotion=timeline.target_emotion,
                curve_type="linear"
            )
            segments.append(segment)
        else:
            # Create segments between waypoints
            for i in range(len(waypoints) - 1):
                start_wp = waypoints[i]
                end_wp = waypoints[i + 1]
                
                segment = TimelineSegment(
                    id=str(uuid.uuid4()),
                    start_time=start_wp.timestamp * (total_duration or 3600.0),
                    end_time=end_wp.timestamp * (total_duration or 3600.0),
                    start_emotion={
                        "valence": start_wp.valence,
                        "arousal": start_wp.arousal,
                        "dominance": start_wp.dominance,
                        "intensity": start_wp.intensity
                    },
                    end_emotion={
                        "valence": end_wp.valence,
                        "arousal": end_wp.arousal,
                        "dominance": end_wp.dominance,
                        "intensity": end_wp.intensity
                    },
                    curve_type=end_wp.transition_curve
                )
                segments.append(segment)
        
        return segments
    
    async def _calculate_emotion_at_position(self, timeline_id: str, position: float) -> Dict[str, float]:
        """Calculate emotion at specific timeline position"""
        segments = self.segment_cache.get(timeline_id, [])
        
        if not segments:
            return {"valence": 0.5, "arousal": 0.5, "dominance": 0.5, "intensity": 0.5}
        
        # Find relevant segment
        for segment in segments:
            if segment.start_time <= position <= segment.end_time:
                # Calculate position within segment
                segment_position = (position - segment.start_time) / (segment.end_time - segment.start_time)
                
                # Interpolate emotion based on curve type
                if segment.curve_type == "linear":
                    return self._linear_interpolate(segment.start_emotion, segment.end_emotion, segment_position)
                elif segment.curve_type == "curved":
                    return self._curved_interpolate(segment.start_emotion, segment.end_emotion, segment_position)
                else:
                    return self._smooth_interpolate(segment.start_emotion, segment.end_emotion, segment_position)
        
        # Return last segment emotion if position beyond segments
        return segments[-1].end_emotion
    
    def _linear_interpolate(self, start: Dict[str, float], end: Dict[str, float], t: float) -> Dict[str, float]:
        """Linear interpolation between emotional states"""
        return {
            "valence": start["valence"] + t * (end["valence"] - start["valence"]),
            "arousal": start["arousal"] + t * (end["arousal"] - start["arousal"]),
            "dominance": start["dominance"] + t * (end["dominance"] - start["dominance"]),
            "intensity": start["intensity"] + t * (end["intensity"] - start["intensity"])
        }
    
    def _curved_interpolate(self, start: Dict[str, float], end: Dict[str, float], t: float) -> Dict[str, float]:
        """Curved interpolation using ease-in-out curve"""
        # Ease-in-out curve
        if t < 0.5:
            t = 2 * t * t
        else:
            t = 1 - 2 * (1 - t) * (1 - t)
        
        return self._linear_interpolate(start, end, t)
    
    def _smooth_interpolate(self, start: Dict[str, float], end: Dict[str, float], t: float) -> Dict[str, float]:
        """Smooth interpolation using cubic curve"""
        # Cubic ease curve
        t = t * t * (3 - 2 * t)
        return self._linear_interpolate(start, end, t)
    
    def _smooth_emotion_transition(self, current: Dict[str, float], target: Dict[str, float]) -> Dict[str, float]:
        """Apply smoothing to emotion transition"""
        return {
            "valence": current["valence"] * self.smoothing_factor + target["valence"] * (1 - self.smoothing_factor),
            "arousal": current["arousal"] * self.smoothing_factor + target["arousal"] * (1 - self.smoothing_factor),
            "dominance": current["dominance"] * self.smoothing_factor + target["dominance"] * (1 - self.smoothing_factor),
            "intensity": current["intensity"] * self.smoothing_factor + target["intensity"] * (1 - self.smoothing_factor)
        }
    
    async def _apply_user_feedback(self, timeline: EmotionalTimelineState, feedback: Dict[str, Any]):
        """Apply user feedback to adapt timeline"""
        # Adjust progression rate based on engagement
        if "engagement_level" in feedback:
            engagement = feedback["engagement_level"]
            if engagement > 0.7:
                timeline.progression_rate = min(2.0, timeline.progression_rate * 1.1)
            elif engagement < 0.3:
                timeline.progression_rate = max(0.5, timeline.progression_rate * 0.9)
        
        # Adjust target emotion based on user response
        if "emotional_response" in feedback:
            response = feedback["emotional_response"]
            for emotion_key in ["valence", "arousal", "dominance"]:
                if emotion_key in response:
                    current_target = timeline.target_emotion.get(emotion_key, 0.5)
                    adjustment = (response[emotion_key] - current_target) * self.adaptation_sensitivity
                    timeline.target_emotion[emotion_key] = max(0.0, min(1.0, current_target + adjustment))
    
    async def _determine_emotional_arc(self, timeline: EmotionalTimelineState) -> EmotionalArcType:
        """Determine the type of emotional arc"""
        current_valence = timeline.current_emotion.get("valence", 0.5)
        target_valence = timeline.target_emotion.get("valence", 0.6)
        
        current_arousal = timeline.current_emotion.get("arousal", 0.5)
        target_arousal = timeline.target_emotion.get("arousal", 0.6)
        
        valence_change = target_valence - current_valence
        arousal_change = target_arousal - current_arousal
        
        if valence_change > 0.3 and arousal_change > 0.2:
            return EmotionalArcType.ASCENDING
        elif valence_change < -0.3 and arousal_change < -0.2:
            return EmotionalArcType.DESCENDING
        elif abs(valence_change) < 0.1 and abs(arousal_change) < 0.1:
            return EmotionalArcType.STABLE
        else:
            return EmotionalArcType.WAVE
    
    async def _calculate_progression_metrics(self, timeline_id: str) -> Dict[str, Any]:
        """Calculate progression metrics for timeline"""
        timeline = self.active_timelines[timeline_id]
        waypoints = self.waypoint_cache.get(timeline_id, [])
        
        return {
            "progress_percentage": min(100.0, timeline.current_position * 100),
            "total_waypoints": len(waypoints),
            "waypoints_reached": len([w for w in waypoints if w.timestamp <= timeline.current_position]),
            "average_progression_rate": timeline.progression_rate,
            "time_since_last_update": (datetime.utcnow() - timeline.last_update).total_seconds()
        }
    
    async def _generate_journey_data(self, timeline_id: str) -> Dict[str, Any]:
        """Generate data for journey visualization"""
        timeline = self.active_timelines[timeline_id]
        waypoints = self.waypoint_cache.get(timeline_id, [])
        
        # Generate sample points for smooth curve
        sample_points = np.linspace(0, 1, 100)
        
        valence_curve = []
        arousal_curve = []
        dominance_curve = []
        intensity_curve = []
        
        for point in sample_points:
            emotion = await self._calculate_emotion_at_position(timeline_id, point)
            valence_curve.append(emotion["valence"])
            arousal_curve.append(emotion["arousal"])
            dominance_curve.append(emotion["dominance"])
            intensity_curve.append(emotion["intensity"])
        
        return {
            "sample_points": sample_points.tolist(),
            "valence_curve": valence_curve,
            "arousal_curve": arousal_curve,
            "dominance_curve": dominance_curve,
            "intensity_curve": intensity_curve,
            "waypoint_positions": [w.timestamp for w in waypoints],
            "current_position": timeline.current_position
        }