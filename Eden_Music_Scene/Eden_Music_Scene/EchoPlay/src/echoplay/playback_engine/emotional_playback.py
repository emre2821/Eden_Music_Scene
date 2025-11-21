"""
Emotional Playback Engine
Intelligent audio playback with emotional awareness and adaptive control
"""

import asyncio
import uuid
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field
from enum import Enum
import structlog
import numpy as np
import soundfile as sf
import librosa

from ..ethical_framework import EthicalAI

logger = structlog.get_logger(__name__)


class PlaybackState(Enum):
    """Current playback state"""
    STOPPED = "stopped"
    PLAYING = "playing"
    PAUSED = "paused"
    BUFFERING = "buffering"
    TRANSITIONING = "transitioning"


class TransitionType(Enum):
    """Types of transitions between tracks"""
    CROSSFADE = "crossfade"
    FADE_OUT_IN = "fade_out_in"
    HARD_CUT = "hard_cut"
    OVERLAP = "overlap"
    GAP = "gap"


@dataclass
class PlaybackTrack:
    """Track information for playback"""
    id: str
    title: str
    artist: str
    duration: float  # seconds
    audio_data: np.ndarray
    sample_rate: int
    emotional_profile: Dict[str, float]
    playback_position: float = 0.0
    volume: float = 1.0
    fade_in_duration: float = 0.0
    fade_out_duration: float = 0.0


@dataclass
class EmotionalTimeline:
    """Timeline of emotional states during playback"""
    start_time: datetime
    current_position: float = 0.0
    emotional_states: List[Tuple[float, Dict[str, float]]] = field(default_factory=list)
    target_emotions: List[Tuple[float, Dict[str, float]]] = field(default_factory=list)
    adaptive_adjustments: List[Dict[str, Any]] = field(default_factory=list)


@dataclass
class PlaybackSession:
    """Complete playback session"""
    id: str
    playlist: List[PlaybackTrack]
    current_track_index: int = 0
    state: PlaybackState = PlaybackState.STOPPED
    timeline: EmotionalTimeline = field(default_factory=lambda: EmotionalTimeline(start_time=datetime.utcnow()))
    user_preferences: Dict[str, Any] = field(default_factory=dict)
    adaptive_parameters: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.utcnow)
    last_activity: datetime = field(default_factory=datetime.utcnow)


class EmotionalPlaybackEngine:
    """
    Emotional Playback Engine
    
    Provides intelligent audio playback with emotional awareness,
    adaptive controls, and real-time state management.
    """
    
    def __init__(self):
        self.sessions: Dict[str, PlaybackSession] = {}
        self.active_playback_tasks: Dict[str, asyncio.Task] = {}
        self.ethical_ai = EthicalAI()
        
        # Playback parameters
        self.buffer_size = 2048
        self.crossfade_duration = 3.0  # seconds
        self.volume_ramp_time = 0.5  # seconds
        
        # Adaptive parameters
        self.emotional_sensitivity = 0.8
        self.adaptation_rate = 0.1
        self.feedback_influence = 0.3
        
        logger.info("EmotionalPlaybackEngine initialized")
    
    async def create_session(self,
                           playlist_data: List[Dict[str, Any]],
                           user_preferences: Dict[str, Any],
                           user_consent: Dict[str, bool]) -> str:
        """
        Create a new emotional playback session
        
        Args:
            playlist_data: List of track information
            user_preferences: User playback preferences
            user_consent: User consent for processing
        
        Returns:
            Session ID
        """
        try:
            # Validate ethical compliance
            is_permitted, violations = await self.ethical_ai.evaluate_action(
                "create_playback_session", {
                    "playlist_length": len(playlist_data),
                    "preferences": user_preferences,
                    "consent": user_consent
                }
            )
            
            if not is_permitted:
                logger.warning("Ethical violations in session creation")
                raise ValueError("Session creation not permitted due to ethical constraints")
            
            # Create session ID
            session_id = str(uuid.uuid4())
            
            # Convert playlist data to PlaybackTrack objects
            playlist = []
            for track_data in playlist_data:
                track = PlaybackTrack(
                    id=track_data.get("id", str(uuid.uuid4())),
                    title=track_data.get("title", "Unknown Track"),
                    artist=track_data.get("artist", "Unknown Artist"),
                    duration=track_data.get("duration", 180.0),
                    audio_data=track_data.get("audio_data", np.array([])),
                    sample_rate=track_data.get("sample_rate", 44100),
                    emotional_profile=track_data.get("emotional_profile", {}),
                    volume=track_data.get("initial_volume", 1.0),
                    fade_in_duration=track_data.get("fade_in_duration", 0.0),
                    fade_out_duration=track_data.get("fade_out_duration", 0.0)
                )
                playlist.append(track)
            
            # Create adaptive parameters
            adaptive_parameters = {
                "emotional_responsiveness": user_preferences.get("emotional_responsiveness", 0.7),
                "volume_adaptation": user_preferences.get("volume_adaptation", 0.5),
                "tempo_adaptation": user_preferences.get("tempo_adaptation", 0.3),
                "crossfade_preference": user_preferences.get("crossfade_preference", 0.8)
            }
            
            # Create session
            session = PlaybackSession(
                id=session_id,
                playlist=playlist,
                user_preferences=user_preferences,
                adaptive_parameters=adaptive_parameters
            )
            
            self.sessions[session_id] = session
            
            logger.info(f"Created playback session {session_id}", extra={
                "tracks": len(playlist),
                "preferences": user_preferences
            })
            
            return session_id
            
        except Exception as e:
            logger.error(f"Error creating playback session: {e}")
            raise
    
    async def start_playback(self, session_id: str, start_track: int = 0) -> Dict[str, Any]:
        """Start playback in a session"""
        try:
            session = self.sessions.get(session_id)
            if not session:
                raise ValueError(f"Session {session_id} not found")
            
            if session.state == PlaybackState.PLAYING:
                return {"status": "already_playing", "session_id": session_id}
            
            # Update session state
            session.state = PlaybackState.PLAYING
            session.current_track_index = start_track
            session.last_activity = datetime.utcnow()
            
            # Start playback task
            playback_task = asyncio.create_task(self._playback_loop(session_id))
            self.active_playback_tasks[session_id] = playback_task
            
            logger.info(f"Started playback in session {session_id}", extra={
                "start_track": start_track,
                "total_tracks": len(session.playlist)
            })
            
            return {
                "status": "playback_started",
                "session_id": session_id,
                "current_track": session.playlist[start_track].title,
                "total_tracks": len(session.playlist)
            }
            
        except Exception as e:
            logger.error(f"Error starting playback: {e}")
            raise
    
    async def control_playback(self, session_id: str, action: str, **kwargs) -> Dict[str, Any]:
        """Control playback (pause, resume, skip, etc.)"""
        try:
            session = self.sessions.get(session_id)
            if not session:
                raise ValueError(f"Session {session_id} not found")
            
            if action == "pause":
                session.state = PlaybackState.PAUSED
                if session_id in self.active_playback_tasks:
                    self.active_playback_tasks[session_id].cancel()
                    del self.active_playback_tasks[session_id]
                
            elif action == "resume":
                if session.state == PlaybackState.PAUSED:
                    session.state = PlaybackState.PLAYING
                    playback_task = asyncio.create_task(self._playback_loop(session_id))
                    self.active_playback_tasks[session_id] = playback_task
            
            elif action == "skip":
                direction = kwargs.get("direction", "next")
                if direction == "next":
                    session.current_track_index = (session.current_track_index + 1) % len(session.playlist)
                elif direction == "previous":
                    session.current_track_index = (session.current_track_index - 1) % len(session.playlist)
                
                # Restart playback from new track
                if session_id in self.active_playback_tasks:
                    self.active_playback_tasks[session_id].cancel()
                    del self.active_playback_tasks[session_id]
                
                if session.state == PlaybackState.PLAYING:
                    playback_task = asyncio.create_task(self._playback_loop(session_id))
                    self.active_playback_tasks[session_id] = playback_task
            
            elif action == "seek":
                position = kwargs.get("position", 0.0)
                current_track = session.playlist[session.current_track_index]
                current_track.playback_position = max(0.0, min(position, current_track.duration))
            
            elif action == "stop":
                session.state = PlaybackState.STOPPED
                if session_id in self.active_playback_tasks:
                    self.active_playback_tasks[session_id].cancel()
                    del self.active_playback_tasks[session_id]
                
                # Reset positions
                for track in session.playlist:
                    track.playback_position = 0.0
            
            session.last_activity = datetime.utcnow()
            
            return {
                "status": f"{action}_completed",
                "session_id": session_id,
                "current_state": session.state.value,
                "current_track": session.playlist[session.current_track_index].title if session.playlist else None
            }
            
        except Exception as e:
            logger.error(f"Error controlling playback: {e}")
            raise
    
    async def get_playback_state(self, session_id: str) -> Dict[str, Any]:
        """Get current playback state"""
        try:
            session = self.sessions.get(session_id)
            if not session:
                raise ValueError(f"Session {session_id} not found")
            
            current_track = session.playlist[session.current_track_index] if session.playlist else None
            
            return {
                "session_id": session_id,
                "state": session.state.value,
                "current_track": {
                    "id": current_track.id,
                    "title": current_track.title,
                    "artist": current_track.artist,
                    "position": current_track.playback_position,
                    "duration": current_track.duration,
                    "emotional_profile": current_track.emotional_profile
                } if current_track else None,
                "timeline_position": session.timeline.current_position,
                "total_tracks": len(session.playlist),
                "session_duration": (datetime.utcnow() - session.created_at).total_seconds()
            }
            
        except Exception as e:
            logger.error(f"Error getting playback state: {e}")
            raise
    
    async def provide_emotional_feedback(self, session_id: str, feedback: Dict[str, Any]) -> Dict[str, Any]:
        """Provide emotional feedback for adaptive playback"""
        try:
            session = self.sessions.get(session_id)
            if not session:
                raise ValueError(f"Session {session_id} not found")
            
            # Validate ethical compliance
            is_permitted, violations = await self.ethical_ai.evaluate_action(
                "provide_emotional_feedback", {
                    "session_id": session_id,
                    "feedback": feedback
                }
            )
            
            if not is_permitted:
                logger.warning("Ethical violations in feedback provision")
                return {"status": "feedback_not_accepted", "reason": "ethical_constraints"}
            
            # Record feedback in timeline
            feedback_entry = {
                "timestamp": datetime.utcnow(),
                "position": session.timeline.current_position,
                "current_track": session.current_track_index,
                "emotional_response": feedback.get("emotional_response", {}),
                "satisfaction": feedback.get("satisfaction", 0.5),
                "intensity_change": feedback.get("intensity_change", 0.0),
                "notes": feedback.get("notes", "")
            }
            
            session.timeline.adaptive_adjustments.append(feedback_entry)
            
            # Apply adaptive adjustments
            await self._apply_adaptive_adjustments(session, feedback_entry)
            
            logger.info(f"Recorded emotional feedback for session {session_id}")
            
            return {
                "status": "feedback_recorded",
                "session_id": session_id,
                "adjustments_applied": True
            }
            
        except Exception as e:
            logger.error(f"Error processing emotional feedback: {e}")
            raise
    
    async def _playback_loop(self, session_id: str):
        """Main playback loop for a session"""
        try:
            session = self.sessions[session_id]
            
            while session.state == PlaybackState.PLAYING:
                if session.current_track_index >= len(session.playlist):
                    break
                
                current_track = session.playlist[session.current_track_index]
                
                # Play current track
                await self._play_track(session, current_track)
                
                # Move to next track
                session.current_track_index += 1
                
                # Handle transition to next track
                if session.current_track_index < len(session.playlist):
                    await self._handle_track_transition(session)
            
            # Playback finished
            session.state = PlaybackState.STOPPED
            
        except asyncio.CancelledError:
            logger.info(f"Playback loop cancelled for session {session_id}")
        except Exception as e:
            logger.error(f"Error in playback loop for session {session_id}: {e}")
            session.state = PlaybackState.STOPPED
    
    async def _play_track(self, session: PlaybackSession, track: PlaybackTrack):
        """Play a single track"""
        try:
            # Calculate remaining duration
            remaining_duration = track.duration - track.playback_position
            
            # Simulate playback (in real implementation, this would use audio output)
            playback_start = datetime.utcnow()
            
            while (track.playback_position < track.duration and 
                   session.state == PlaybackState.PLAYING):
                
                # Update timeline
                session.timeline.current_position += 0.1  # 100ms increments
                track.playback_position += 0.1
                
                # Update emotional timeline
                await self._update_emotional_timeline(session, track)
                
                # Small delay to simulate real-time playback
                await asyncio.sleep(0.1)
            
            logger.debug(f"Completed playback of track {track.title}")
            
        except Exception as e:
            logger.error(f"Error playing track {track.title}: {e}")
            raise
    
    async def _handle_track_transition(self, session: PlaybackSession):
        """Handle transition between tracks"""
        try:
            current_track = session.playlist[session.current_track_index - 1]
            next_track = session.playlist[session.current_track_index]
            
            # Calculate optimal transition type based on emotional profiles
            transition_type = await self._calculate_optimal_transition(current_track, next_track)
            
            session.state = PlaybackState.TRANSITIONING
            
            if transition_type == TransitionType.CROSSFADE:
                await self._perform_crossfade(session, current_track, next_track)
            elif transition_type == TransitionType.FADE_OUT_IN:
                await self._perform_fade_out_in(session, current_track, next_track)
            
            # Reset positions
            current_track.playback_position = current_track.duration  # Mark as complete
            next_track.playback_position = 0.0
            
            session.state = PlaybackState.PLAYING
            
        except Exception as e:
            logger.error(f"Error in track transition: {e}")
            session.state = PlaybackState.PLAYING  # Continue with hard cut
    
    async def _calculate_optimal_transition(self, current_track: PlaybackTrack, next_track: PlaybackTrack) -> TransitionType:
        """Calculate optimal transition type based on track emotional profiles"""
        # Analyze emotional compatibility
        current_valence = current_track.emotional_profile.get("valence", 0.5)
        next_valence = next_track.emotional_profile.get("valence", 0.5)
        
        current_arousal = current_track.emotional_profile.get("arousal", 0.5)
        next_arousal = next_track.emotional_profile.get("arousal", 0.5)
        
        # Calculate emotional distance
        valence_diff = abs(current_valence - next_valence)
        arousal_diff = abs(current_arousal - next_arousal)
        
        # Determine transition type
        if valence_diff < 0.2 and arousal_diff < 0.2:
            return TransitionType.CROSSFADE
        elif valence_diff > 0.5 or arousal_diff > 0.5:
            return TransitionType.FADE_OUT_IN
        else:
            return TransitionType.OVERLAP
    
    async def _perform_crossfade(self, session: PlaybackSession, current_track: PlaybackTrack, next_track: PlaybackTrack):
        """Perform crossfade transition between tracks"""
        crossfade_duration = self.crossfade_duration
        
        # Fade out current track
        fade_steps = int(crossfade_duration / 0.1)  # 100ms steps
        for step in range(fade_steps):
            if session.state != PlaybackState.TRANSITIONING:
                break
            
            fade_factor = 1.0 - (step / fade_steps)
            current_track.volume = fade_factor
            
            await asyncio.sleep(0.1)
        
        # Fade in next track
        for step in range(fade_steps):
            if session.state != PlaybackState.TRANSITIONING:
                break
            
            fade_factor = step / fade_steps
            next_track.volume = fade_factor
            
            await asyncio.sleep(0.1)
        
        # Reset volumes
        current_track.volume = 1.0
        next_track.volume = 1.0
    
    async def _perform_fade_out_in(self, session: PlaybackSession, current_track: PlaybackTrack, next_track: PlaybackTrack):
        """Perform fade out and fade in transition"""
        # Fade out current track
        fade_steps = int(self.volume_ramp_time / 0.1)
        for step in range(fade_steps):
            if session.state != PlaybackState.TRANSITIONING:
                break
            
            fade_factor = 1.0 - (step / fade_steps)
            current_track.volume = fade_factor
            
            await asyncio.sleep(0.1)
        
        # Brief pause
        await asyncio.sleep(0.5)
        
        # Fade in next track
        for step in range(fade_steps):
            if session.state != PlaybackState.TRANSITIONING:
                break
            
            fade_factor = step / fade_steps
            next_track.volume = fade_factor
            
            await asyncio.sleep(0.1)
        
        # Reset volumes
        current_track.volume = 1.0
        next_track.volume = 1.0
    
    async def _update_emotional_timeline(self, session: PlaybackSession, track: PlaybackTrack):
        """Update emotional timeline during playback"""
        # Record current emotional state
        current_time = session.timeline.current_position
        emotional_state = {
            "valence": track.emotional_profile.get("valence", 0.5),
            "arousal": track.emotional_profile.get("arousal", 0.5),
            "intensity": track.emotional_profile.get("intensity", 0.5) * track.volume
        }
        
        session.timeline.emotional_states.append((current_time, emotional_state))
        
        # Keep only last 1000 states for memory efficiency
        if len(session.timeline.emotional_states) > 1000:
            session.timeline.emotional_states = session.timeline.emotional_states[-1000:]
    
    async def _apply_adaptive_adjustments(self, session: PlaybackSession, feedback: Dict[str, Any]):
        """Apply adaptive adjustments based on user feedback"""
        satisfaction = feedback.get("satisfaction", 0.5)
        intensity_change = feedback.get("intensity_change", 0.0)
        
        # Adjust current track volume based on satisfaction
        if satisfaction < 0.3:  # Low satisfaction
            current_track = session.playlist[session.current_track_index]
            current_track.volume = max(0.1, current_track.volume - 0.1)
        elif satisfaction > 0.7:  # High satisfaction
            current_track = session.playlist[session.current_track_index]
            current_track.volume = min(1.0, current_track.volume + 0.05)
        
        # Adjust emotional sensitivity based on feedback
        if abs(intensity_change) > 0.2:
            session.adaptive_parameters["emotional_responsiveness"] = min(
                1.0, max(0.1, session.adaptive_parameters["emotional_responsiveness"] + intensity_change * self.adaptation_rate)
            )
    
    async def cleanup_session(self, session_id: str):
        """Clean up a playback session"""
        try:
            if session_id in self.active_playback_tasks:
                self.active_playback_tasks[session_id].cancel()
                del self.active_playback_tasks[session_id]
            
            if session_id in self.sessions:
                del self.sessions[session_id]
            
            logger.info(f"Cleaned up playback session {session_id}")
            
        except Exception as e:
            logger.error(f"Error cleaning up session {session_id}: {e}")
    
    async def get_session_analytics(self, session_id: str) -> Dict[str, Any]:
        """Get analytics for a playback session"""
        try:
            session = self.sessions.get(session_id)
            if not session:
                raise ValueError(f"Session {session_id} not found")
            
            # Calculate session analytics
            total_duration = (datetime.utcnow() - session.created_at).total_seconds()
            tracks_played = len([t for t in session.playlist if t.playback_position > 0])
            
            # Emotional journey analysis
            if session.timeline.emotional_states:
                avg_valence = np.mean([s[1].get("valence", 0.5) for s in session.timeline.emotional_states])
                avg_arousal = np.mean([s[1].get("arousal", 0.5) for s in session.timeline.emotional_states])
                emotional_variance = np.var([s[1].get("intensity", 0.5) for s in session.timeline.emotional_states])
            else:
                avg_valence = avg_arousal = 0.5
                emotional_variance = 0.0
            
            return {
                "session_id": session_id,
                "total_duration": total_duration,
                "tracks_played": tracks_played,
                "total_tracks": len(session.playlist),
                "emotional_journey": {
                    "average_valence": avg_valence,
                    "average_arousal": avg_arousal,
                    "emotional_variance": emotional_variance,
                    "state_count": len(session.timeline.emotional_states)
                },
                "adaptive_adjustments": len(session.timeline.adaptive_adjustments),
                "session_created": session.created_at.isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error getting session analytics: {e}")
            raise