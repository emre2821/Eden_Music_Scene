"""
Mood Router - Emotional Pathfinding Engine
Routes musical selections based on emotional intelligence and user journey
"""

import asyncio
import numpy as np
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime
import structlog

from ..ethical_framework import EthicalAI

logger = structlog.get_logger(__name__)


class EmotionalArc(Enum):
    """Types of emotional journeys"""
    ASCENDING = "ascending"  # Building energy and positivity
    DESCENDING = "descending"  # Deepening into contemplative states
    WAVY = "wavy"  # Rhythmic emotional oscillation
    STABLE = "stable"  # Maintaining consistent emotional state
    RESOLUTION = "resolution"  # Moving toward peace/clarity
    TRANSFORMATION = "transformation"  # Major emotional shift


class TransitionStyle(Enum):
    """How emotions transition between tracks"""
    SMOOTH = "smooth"  # Gradual, barely perceptible changes
    STEPWISE = "stepwise"  # Clear but gentle transitions
    CONTRAST = "contrast"  # Deliberate emotional contrasts
    BRIDGE = "bridge"  # Using transitional elements
    SURPRISE = "surprise"  # Unexpected but meaningful jumps


@dataclass
class EmotionalPoint:
    """Represents an emotional state in time"""
    timestamp: float  # Position in playlist (0.0 to 1.0)
    valence: float  # Pleasantness (-1.0 to 1.0)
    arousal: float  # Energy level (0.0 to 1.0)
    dominance: float  # Control/feeling of power (0.0 to 1.0)
    depth: float  # Emotional complexity/depth (0.0 to 1.0)
    resonance: float  # How much it resonates with user (0.0 to 1.0)
    
    def distance_to(self, other: 'EmotionalPoint') -> float:
        """Calculate emotional distance to another point"""
        return np.sqrt(
            (self.valence - other.valence) ** 2 +
            (self.arousal - other.arousal) ** 2 +
            (self.dominance - other.dominance) ** 2 +
            (self.depth - other.depth) ** 2
        )


@dataclass
class MoodRoute:
    """Complete emotional journey route"""
    start_point: EmotionalPoint
    end_point: EmotionalPoint
    waypoints: List[EmotionalPoint] = field(default_factory=list)
    arc_type: EmotionalArc = EmotionalArc.STABLE
    transition_style: TransitionStyle = TransitionStyle.SMOOTH
    total_duration: float = 0.0  # in minutes
    estimated_impact: float = 0.0  # Expected emotional resonance (0.0 to 1.0)
    
    def add_waypoint(self, point: EmotionalPoint):
        """Add a waypoint to the route"""
        self.waypoints.append(point)
        self.waypoints.sort(key=lambda p: p.timestamp)
    
    def get_emotional_at(self, timestamp: float) -> EmotionalPoint:
        """Get emotional state at specific timestamp using interpolation"""
        if not self.waypoints:
            return self.start_point
        
        # Find surrounding waypoints
        before = self.start_point
        after = None
        
        for waypoint in self.waypoints:
            if waypoint.timestamp <= timestamp:
                before = waypoint
            else:
                after = waypoint
                break
        
        if after is None:
            after = self.end_point
        
        # Linear interpolation
        if before.timestamp == after.timestamp:
            return before
        
        t = (timestamp - before.timestamp) / (after.timestamp - before.timestamp)
        
        return EmotionalPoint(
            timestamp=timestamp,
            valence=before.valence + t * (after.valence - before.valence),
            arousal=before.arousal + t * (after.arousal - before.arousal),
            dominance=before.dominance + t * (after.dominance - before.dominance),
            depth=before.depth + t * (after.depth - before.depth),
            resonance=before.resonance + t * (after.resonance - before.resonance)
        )


class MoodRouter:
    """
    Emotional pathfinding engine that creates meaningful musical journeys
    """
    
    def __init__(self):
        self.ethical_ai = EthicalAI()
        self.route_cache = {}
        self.user_preferences = {}
        self.emotional_models = self._initialize_emotional_models()
    
    def _initialize_emotional_models(self) -> Dict[str, Any]:
        """Initialize emotional analysis models"""
        return {
            "valence_arousal_model": self._load_valence_arousal_model(),
            "genre_emotion_map": self._load_genre_emotion_map(),
            "tempo_energy_model": self._load_tempo_energy_model()
        }
    
    def _load_valence_arousal_model(self):
        """Load valence-arousal emotional model"""
        # This would typically load a trained ML model
        # For now, return a simple rule-based approach
        return {
            "major_key_boost": 0.3,
            "tempo_arousal_factor": 0.4,
            "harmonic_complexity_factor": 0.2
        }
    
    def _load_genre_emotion_map(self) -> Dict[str, EmotionalPoint]:
        """Map genres to typical emotional characteristics"""
        return {
            "ambient": EmotionalPoint(0, 0.6, 0.3, 0.4, 0.8, 0.7),
            "classical": EmotionalPoint(0, 0.5, 0.4, 0.6, 0.9, 0.8),
            "electronic": EmotionalPoint(0, 0.7, 0.8, 0.7, 0.6, 0.8),
            "jazz": EmotionalPoint(0, 0.6, 0.5, 0.8, 0.8, 0.7),
            "metal": EmotionalPoint(0, 0.3, 0.9, 0.8, 0.7, 0.9),
            "pop": EmotionalPoint(0, 0.8, 0.7, 0.6, 0.4, 0.8),
            "rock": EmotionalPoint(0, 0.6, 0.8, 0.7, 0.6, 0.8),
            "folk": EmotionalPoint(0, 0.6, 0.4, 0.5, 0.7, 0.6),
            "blues": EmotionalPoint(0, 0.3, 0.4, 0.5, 0.8, 0.7),
            "soul": EmotionalPoint(0, 0.7, 0.6, 0.7, 0.8, 0.9)
        }
    
    def _load_tempo_energy_model(self):
        """Load tempo-to-energy mapping model"""
        return {
            "low_tempo": (0, 90),  # BPM
            "medium_tempo": (90, 140),
            "high_tempo": (140, 200),
            "energy_mapping": {
                "low_tempo": 0.3,
                "medium_tempo": 0.6,
                "high_tempo": 0.9
            }
        }
    
    async def create_emotional_route(self,
                                   user_emotion: Dict[str, float],
                                   target_emotion: Optional[Dict[str, float]],
                                   duration_minutes: float,
                                   preferences: Dict[str, Any]) -> MoodRoute:
        """
        Create an emotional route based on user input and preferences
        
        Args:
            user_emotion: Current emotional state (valence, arousal, dominance)
            target_emotion: Desired emotional state (optional)
            duration_minutes: Total playlist duration
            preferences: User preferences and constraints
        
        Returns:
            MoodRoute object defining the emotional journey
        """
        try:
            # Validate ethical compliance
            is_permitted, violations = await self.ethical_ai.evaluate_action(
                "create_emotional_route", {
                    "user_emotion": user_emotion,
                    "target_emotion": target_emotion,
                    "preferences": preferences
                }
            )
            
            if not is_permitted:
                logger.warning("Ethical violations in emotional routing request", extra={"violations": violations})
                # Create a neutral, safe route
                return await self._create_safe_route(duration_minutes)
            
            # Create start point from current emotion
            start_point = EmotionalPoint(
                timestamp=0.0,
                valence=user_emotion.get("valence", 0.5),
                arousal=user_emotion.get("arousal", 0.5),
                dominance=user_emotion.get("dominance", 0.5),
                depth=user_emotion.get("depth", 0.5),
                resonance=user_emotion.get("resonance", 0.7)
            )
            
            # Determine end point
            if target_emotion:
                end_point = EmotionalPoint(
                    timestamp=1.0,
                    valence=target_emotion.get("valence", 0.6),
                    arousal=target_emotion.get("arousal", 0.6),
                    dominance=target_emotion.get("dominance", 0.6),
                    depth=target_emotion.get("depth", 0.6),
                    resonance=target_emotion.get("resonance", 0.8)
                )
            else:
                # Create a meaningful journey without explicit target
                end_point = await self._generate_meaningful_endpoint(start_point, preferences)
            
            # Determine emotional arc type
            arc_type = await self._determine_arc_type(start_point, end_point, preferences)
            
            # Create waypoints along the journey
            waypoints = await self._create_waypoints(start_point, end_point, arc_type, preferences)
            
            # Determine transition style
            transition_style = await self._determine_transition_style(preferences)
            
            # Calculate estimated impact
            estimated_impact = await self._calculate_estimated_impact(start_point, end_point, waypoints)
            
            route = MoodRoute(
                start_point=start_point,
                end_point=end_point,
                waypoints=waypoints,
                arc_type=arc_type,
                transition_style=transition_style,
                total_duration=duration_minutes,
                estimated_impact=estimated_impact
            )
            
            logger.info("Emotional route created", extra={
                "arc_type": arc_type.value,
                "waypoints": len(waypoints),
                "duration": duration_minutes,
                "impact": estimated_impact
            })
            
            return route
            
        except Exception as e:
            logger.error(f"Error creating emotional route: {e}")
            return await self._create_safe_route(duration_minutes)
    
    async def _create_safe_route(self, duration_minutes: float) -> MoodRoute:
        """Create a safe, neutral emotional route"""
        start_point = EmotionalPoint(0.0, 0.6, 0.5, 0.6, 0.5, 0.7)
        end_point = EmotionalPoint(1.0, 0.6, 0.5, 0.6, 0.5, 0.7)
        
        return MoodRoute(
            start_point=start_point,
            end_point=end_point,
            waypoints=[],
            arc_type=EmotionalArc.STABLE,
            transition_style=TransitionStyle.SMOOTH,
            total_duration=duration_minutes,
            estimated_impact=0.5
        )
    
    async def _generate_meaningful_endpoint(self, start_point: EmotionalPoint, preferences: Dict[str, Any]) -> EmotionalPoint:
        """Generate a meaningful endpoint for the emotional journey"""
        # Consider user preferences and current state
        journey_type = preferences.get("journey_type", "exploratory")
        
        if journey_type == "energizing":
            # Increase arousal and valence
            return EmotionalPoint(
                timestamp=1.0,
                valence=min(0.9, start_point.valence + 0.2),
                arousal=min(0.9, start_point.arousal + 0.3),
                dominance=max(0.6, start_point.dominance + 0.1),
                depth=start_point.depth,
                resonance=min(0.9, start_point.resonance + 0.1)
            )
        elif journey_type == "calming":
            # Decrease arousal, maintain or slightly increase valence
            return EmotionalPoint(
                timestamp=1.0,
                valence=max(0.6, start_point.valence + 0.1),
                arousal=max(0.2, start_point.arousal - 0.3),
                dominance=max(0.4, start_point.dominance - 0.1),
                depth=max(0.6, start_point.depth + 0.1),
                resonance=max(0.8, start_point.resonance + 0.1)
            )
        elif journey_type == "exploratory":
            # Create contrast while maintaining coherence
            return EmotionalPoint(
                timestamp=1.0,
                valence=0.7 if start_point.valence < 0.5 else 0.4,
                arousal=0.6 if start_point.arousal < 0.5 else 0.4,
                dominance=0.6,
                depth=max(0.7, start_point.depth + 0.2),
                resonance=max(0.8, start_point.resonance + 0.1)
            )
        else:
            # Default: slight improvement in emotional state
            return EmotionalPoint(
                timestamp=1.0,
                valence=min(0.8, start_point.valence + 0.1),
                arousal=start_point.arousal,
                dominance=start_point.dominance,
                depth=max(0.6, start_point.depth + 0.1),
                resonance=max(0.8, start_point.resonance + 0.1)
            )
    
    async def _determine_arc_type(self, start_point: EmotionalPoint, end_point: EmotionalPoint, preferences: Dict[str, Any]) -> EmotionalArc:
        """Determine the emotional arc type based on start/end points and preferences"""
        valence_diff = end_point.valence - start_point.valence
        arousal_diff = end_point.arousal - start_point.arousal
        
        # Check for explicit preference
        preferred_arc = preferences.get("emotional_arc")
        if preferred_arc:
            try:
                return EmotionalArc(preferred_arc)
            except ValueError:
                pass
        
        # Determine based on emotional changes
        if valence_diff > 0.3 and arousal_diff > 0.2:
            return EmotionalArc.ASCENDING
        elif valence_diff < -0.3 and arousal_diff < -0.2:
            return EmotionalArc.DESCENDING
        elif abs(valence_diff) < 0.1 and abs(arousal_diff) < 0.1:
            return EmotionalArc.STABLE
        elif valence_diff > 0.3 or arousal_diff > 0.3:
            return EmotionalArc.RESOLUTION
        else:
            return EmotionalArc.WAVY
    
    async def _create_waypoints(self, start_point: EmotionalPoint, end_point: EmotionalPoint, 
                              arc_type: EmotionalArc, preferences: Dict[str, Any]) -> List[EmotionalPoint]:
        """Create intermediate waypoints for the emotional journey"""
        waypoints = []
        num_waypoints = preferences.get("complexity", 3)  # Number of waypoints
        
        for i in range(1, num_waypoints + 1):
            timestamp = i / (num_waypoints + 1)
            
            if arc_type == EmotionalArc.ASCENDING:
                # Gradual increase
                progress = timestamp
                valence = start_point.valence + progress * (end_point.valence - start_point.valence)
                arousal = start_point.arousal + progress * (end_point.arousal - start_point.arousal)
                
            elif arc_type == EmotionalArc.DESCENDING:
                # Gradual decrease
                progress = timestamp
                valence = start_point.valence + progress * (end_point.valence - start_point.valence)
                arousal = start_point.arousal + progress * (end_point.arousal - start_point.arousal)
                
            elif arc_type == EmotionalArc.WAVY:
                # Oscillating path
                progress = timestamp
                wave_offset = 0.1 * np.sin(progress * 4 * np.pi)
                valence = start_point.valence + progress * (end_point.valence - start_point.valence) + wave_offset
                arousal = start_point.arousal + progress * (end_point.arousal - start_point.arousal) + wave_offset
                
            else:  # STABLE or RESOLUTION
                # Steady progression
                progress = timestamp
                valence = start_point.valence + progress * (end_point.valence - start_point.valence)
                arousal = start_point.arousal + progress * (end_point.arousal - start_point.arousal)
            
            # Ensure values stay within bounds
            valence = max(-1.0, min(1.0, valence))
            arousal = max(0.0, min(1.0, arousal))
            dominance = max(0.0, min(1.0, start_point.dominance + progress * (end_point.dominance - start_point.dominance)))
            depth = max(0.0, min(1.0, start_point.depth + progress * (end_point.depth - start_point.depth)))
            resonance = max(0.0, min(1.0, start_point.resonance + progress * (end_point.resonance - start_point.resonance)))
            
            waypoint = EmotionalPoint(
                timestamp=timestamp,
                valence=valence,
                arousal=arousal,
                dominance=dominance,
                depth=depth,
                resonance=resonance
            )
            waypoints.append(waypoint)
        
        return waypoints
    
    async def _determine_transition_style(self, preferences: Dict[str, Any]) -> TransitionStyle:
        """Determine the transition style based on preferences"""
        preferred_style = preferences.get("transition_style")
        if preferred_style:
            try:
                return TransitionStyle(preferred_style)
            except ValueError:
                pass
        
        # Default based on user experience level
        experience_level = preferences.get("experience_level", "intermediate")
        if experience_level == "beginner":
            return TransitionStyle.SMOOTH
        elif experience_level == "advanced":
            return TransitionStyle.CONTRAST
        else:
            return TransitionStyle.STEPWISE
    
    async def _calculate_estimated_impact(self, start_point: EmotionalPoint, end_point: EmotionalPoint, waypoints: List[EmotionalPoint]) -> float:
        """Calculate the estimated emotional impact of the route"""
        if not waypoints:
            return 0.5
        
        # Calculate total emotional distance traveled
        total_distance = start_point.distance_to(waypoints[0]) if waypoints else 0
        for i in range(len(waypoints) - 1):
            total_distance += waypoints[i].distance_to(waypoints[i + 1])
        if waypoints:
            total_distance += waypoints[-1].distance_to(end_point)
        
        # Normalize by number of waypoints
        avg_distance = total_distance / (len(waypoints) + 1)
        
        # Factor in resonance levels
        avg_resonance = np.mean([p.resonance for p in [start_point, end_point] + waypoints])
        
        # Calculate impact score (0.0 to 1.0)
        impact = min(1.0, (avg_distance * 0.6 + avg_resonance * 0.4))
        
        return impact
    
    async def route_to_tracks(self, route: MoodRoute, available_tracks: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Convert emotional route to actual track selections
        
        Args:
            route: The emotional route to follow
            available_tracks: List of tracks with emotional metadata
        
        Returns:
            Ordered list of selected tracks
        """
        selected_tracks = []
        
        # Calculate track positions based on route waypoints
        total_tracks = len(available_tracks)
        if total_tracks == 0:
            return []
        
        # Sort tracks by emotional characteristics
        track_positions = []
        for i, track in enumerate(available_tracks):
            # Calculate track's position in emotional journey (0.0 to 1.0)
            position = i / max(1, total_tracks - 1)
            
            # Get target emotional state for this position
            target_emotion = route.get_emotional_at(position)
            
            # Calculate track's emotional characteristics
            track_emotion = self._extract_track_emotion(track)
            
            # Calculate fitness score
            fitness = self._calculate_track_fitness(track_emotion, target_emotion, route.transition_style)
            
            track_positions.append({
                "track": track,
                "position": position,
                "fitness": fitness,
                "target_emotion": target_emotion,
                "track_emotion": track_emotion
            })
        
        # Sort by fitness and select best tracks
        track_positions.sort(key=lambda x: x["fitness"], reverse=True)
        
        # Create final playlist maintaining emotional progression
        selected_tracks = self._create_emotionally_coherent_playlist(track_positions, route)
        
        return selected_tracks
    
    def _extract_track_emotion(self, track: Dict[str, Any]) -> EmotionalPoint:
        """Extract emotional characteristics from track metadata"""
        return EmotionalPoint(
            timestamp=0.0,  # Will be set later
            valence=track.get("valence", 0.5),
            arousal=track.get("energy", 0.5),
            dominance=track.get("dominance", 0.5),
            depth=track.get("depth", 0.5),
            resonance=track.get("popularity", 0.5)  # Use popularity as resonance proxy
        )
    
    def _calculate_track_fitness(self, track_emotion: EmotionalPoint, target_emotion: EmotionalPoint, 
                               transition_style: TransitionStyle) -> float:
        """Calculate how well a track fits a target emotional state"""
        base_distance = track_emotion.distance_to(target_emotion)
        
        # Adjust based on transition style
        if transition_style == TransitionStyle.SMOOTH:
            # Prefer closer matches
            fitness = 1.0 / (1.0 + base_distance)
        elif transition_style == TransitionStyle.CONTRAST:
            # Prefer some distance but not too much
            optimal_distance = 0.3
            distance_diff = abs(base_distance - optimal_distance)
            fitness = 1.0 / (1.0 + distance_diff)
        else:  # STEPWISE
            # Moderate distance preferred
            optimal_distance = 0.2
            distance_diff = abs(base_distance - optimal_distance)
            fitness = 1.0 / (1.0 + distance_diff)
        
        return fitness
    
    def _create_emotionally_coherent_playlist(self, track_positions: List[Dict], route: MoodRoute) -> List[Dict[str, Any]]:
        """Create a playlist that maintains emotional coherence"""
        # This is a simplified version - in practice would use more sophisticated algorithms
        playlist = []
        
        # Select top tracks while maintaining emotional progression
        used_positions = set()
        
        for target_position in [i * 0.1 for i in range(11)]:  # 0.0 to 1.0 in 0.1 increments
            # Find best track for this position
            best_track = None
            best_fitness = -1
            
            for track_data in track_positions:
                if track_data["position"] in used_positions:
                    continue
                
                position_diff = abs(track_data["position"] - target_position)
                if position_diff < 0.15:  # Within 15% of target position
                    fitness = track_data["fitness"] * (1 - position_diff)  # Penalize position mismatch
                    if fitness > best_fitness:
                        best_fitness = fitness
                        best_track = track_data
            
            if best_track:
                playlist.append(best_track["track"])
                used_positions.add(best_track["position"])
        
        return playlist