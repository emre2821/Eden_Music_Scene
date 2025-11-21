"""
Dynamic Playlist Engine
Generates and manages playlists based on emotional routing and user preferences
"""

import asyncio
import uuid
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field
from enum import Enum
import structlog

from ..mood_router.emotional_routing import MoodRouter, MoodRoute, EmotionalPoint
from ..ethical_framework import EthicalAI

logger = structlog.get_logger(__name__)


class PlaylistType(Enum):
    """Types of playlists that can be generated"""
    EMOTIONAL_JOURNEY = "emotional_journey"
    MOOD_MAINTENANCE = "mood_maintenance"
    ENERGY_BUILDING = "energy_building"
    CONTEMPLATIVE_DIVE = "contemplative_dive"
    DISCOVERY_EXPEDITION = "discovery_expedition"
    NOSTALGIC_VOYAGE = "nostalgic_voyage"
    ECSTATIC_RELEASE = "ecstatic_release"
    HEALING_SESSION = "healing_session"


class PlaylistStatus(Enum):
    """Status of playlist generation"""
    PENDING = "pending"
    GENERATING = "generating"
    READY = "ready"
    PLAYING = "playing"
    COMPLETED = "completed"
    INTERRUPTED = "interrupted"


@dataclass
class PlaylistTrack:
    """Represents a track in a playlist"""
    id: str
    title: str
    artist: str
    duration: int  # seconds
    audio_features: Dict[str, float]  # valence, energy, danceability, etc.
    emotional_profile: EmotionalPoint
    transition_notes: str = ""
    play_count: int = 0
    last_played: Optional[datetime] = None


@dataclass
class DynamicPlaylist:
    """Dynamic playlist with emotional routing"""
    id: str
    name: str
    description: str
    type: PlaylistType
    status: PlaylistStatus
    route: MoodRoute
    tracks: List[PlaylistTrack] = field(default_factory=list)
    total_duration: int = 0  # seconds
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)
    user_preferences: Dict[str, Any] = field(default_factory=dict)
    play_history: List[Dict[str, Any]] = field(default_factory=list)
    adaptive_parameters: Dict[str, Any] = field(default_factory=dict)


class PlaylistGenerationEngine:
    """
    Advanced playlist generation engine with emotional intelligence
    """
    
    def __init__(self):
        self.mood_router = MoodRouter()
        self.ethical_ai = EthicalAI()
        self.playlist_cache = {}
        self.generation_queue = asyncio.Queue()
        self.active_generations = {}
    
    async def generate_playlist(self,
                              user_request: Dict[str, Any],
                              user_emotion: Dict[str, float],
                              available_tracks: List[Dict[str, Any]],
                              preferences: Dict[str, Any]) -> DynamicPlaylist:
        """
        Generate a dynamic playlist based on user input and emotional context
        
        Args:
            user_request: User's playlist request details
            user_emotion: Current emotional state
            available_tracks: Pool of tracks to select from
            preferences: User preferences and constraints
        
        Returns:
            Generated DynamicPlaylist object
        """
        try:
            # Validate ethical compliance
            is_permitted, violations = await self.ethical_ai.evaluate_action(
                "generate_playlist", {
                    "user_request": user_request,
                    "user_emotion": user_emotion,
                    "preferences": preferences
                }
            )
            
            if not is_permitted:
                logger.warning("Ethical violations in playlist generation request")
                return await self._create_fallback_playlist(user_request, available_tracks)
            
            # Determine playlist type
            playlist_type = await self._determine_playlist_type(user_request, user_emotion)
            
            # Create emotional route
            target_emotion = user_request.get("target_emotion")
            duration_minutes = user_request.get("duration_minutes", 60)
            
            route = await self.mood_router.create_emotional_route(
                user_emotion=user_emotion,
                target_emotion=target_emotion,
                duration_minutes=duration_minutes,
                preferences=preferences
            )
            
            # Select tracks based on emotional route
            selected_tracks = await self._select_tracks_for_route(route, available_tracks, preferences)
            
            # Create playlist object
            playlist = DynamicPlaylist(
                id=str(uuid.uuid4()),
                name=await self._generate_playlist_name(playlist_type, user_emotion),
                description=await self._generate_playlist_description(route, playlist_type),
                type=playlist_type,
                status=PlaylistStatus.READY,
                route=route,
                tracks=selected_tracks,
                total_duration=sum(track.duration for track in selected_tracks),
                user_preferences=preferences,
                adaptive_parameters={
                    "emotional_sensitivity": preferences.get("emotional_sensitivity", 0.7),
                    "discovery_rate": preferences.get("discovery_rate", 0.3),
                    "familiarity_balance": preferences.get("familiarity_balance", 0.5)
                }
            )
            
            # Cache the playlist
            self.playlist_cache[playlist.id] = playlist
            
            logger.info("Playlist generated successfully", extra={
                "playlist_id": playlist.id,
                "type": playlist_type.value,
                "tracks": len(selected_tracks),
                "duration": playlist.total_duration
            })
            
            return playlist
            
        except Exception as e:
            logger.error(f"Error generating playlist: {e}")
            return await self._create_fallback_playlist(user_request, available_tracks)
    
    async def _determine_playlist_type(self, user_request: Dict[str, Any], user_emotion: Dict[str, float]) -> PlaylistType:
        """Determine the appropriate playlist type based on user input and emotion"""
        request_text = user_request.get("text", "").lower()
        
        # Keyword-based detection
        if any(word in request_text for word in ["journey", "adventure", "explore"]):
            return PlaylistType.DISCOVERY_EXPEDITION
        elif any(word in request_text for word in ["energy", "pump", "motivate"]):
            return PlaylistType.ENERGY_BUILDING
        elif any(word in request_text for word in ["calm", "peaceful", "meditate"]):
            return PlaylistType.CONTEMPLATIVE_DIVE
        elif any(word in request_text for word in ["heal", "therapy", "comfort"]):
            return PlaylistType.HEALING_SESSION
        elif any(word in request_text for word in ["nostalgia", "memories", "classic"]):
            return PlaylistType.NOSTALGIC_VOYAGE
        elif any(word in request_text for word in ["party", "dance", "celebrate"]):
            return PlaylistType.ECSTATIC_RELEASE
        elif any(word in request_text for word in ["maintain", "keep", "steady"]):
            return PlaylistType.MOOD_MAINTENANCE
        
        # Emotion-based detection
        valence = user_emotion.get("valence", 0.5)
        arousal = user_emotion.get("arousal", 0.5)
        
        if valence < 0.4 and arousal < 0.4:
            return PlaylistType.HEALING_SESSION
        elif valence > 0.7 and arousal > 0.7:
            return PlaylistType.ECSTATIC_RELEASE
        elif valence < 0.5:
            return PlaylistType.CONTEMPLATIVE_DIVE
        elif arousal < 0.4:
            return PlaylistType.CONTEMPLATIVE_DIVE
        else:
            return PlaylistType.EMOTIONAL_JOURNEY
    
    async def _select_tracks_for_route(self, route: MoodRoute, available_tracks: List[Dict[str, Any]], 
                                     preferences: Dict[str, Any]) -> List[PlaylistTrack]:
        """Select tracks that best fit the emotional route"""
        playlist_tracks = []
        
        # Convert available tracks to PlaylistTrack objects with emotional analysis
        track_candidates = []
        for track_data in available_tracks:
            track = await self._create_playlist_track(track_data)
            track_candidates.append(track)
        
        # Select tracks for each waypoint in the route
        for i, waypoint in enumerate([route.start_point] + route.waypoints + [route.end_point]):
            # Find best matching tracks for this emotional state
            suitable_tracks = await self._find_tracks_for_emotion(track_candidates, waypoint, preferences)
            
            # Select the best track (avoiding duplicates)
            selected_track = await self._select_best_track(suitable_tracks, playlist_tracks, preferences)
            
            if selected_track:
                # Add transition notes
                if i > 0:
                    prev_waypoint = [route.start_point] + route.waypoints + [route.end_point][i-1]
                    selected_track.transition_notes = await self._generate_transition_notes(prev_waypoint, waypoint)
                
                playlist_tracks.append(selected_track)
        
        # Ensure playlist meets duration requirements
        playlist_tracks = await self._adjust_playlist_duration(playlist_tracks, route.total_duration, track_candidates)
        
        return playlist_tracks
    
    async def _create_playlist_track(self, track_data: Dict[str, Any]) -> PlaylistTrack:
        """Create a PlaylistTrack object from track data"""
        return PlaylistTrack(
            id=track_data.get("id", str(uuid.uuid4())),
            title=track_data.get("name", "Unknown Track"),
            artist=track_data.get("artist", "Unknown Artist"),
            duration=track_data.get("duration_ms", 180000) // 1000,  # Convert to seconds
            audio_features=track_data.get("audio_features", {}),
            emotional_profile=EmotionalPoint(
                timestamp=0.0,
                valence=track_data.get("valence", 0.5),
                arousal=track_data.get("energy", 0.5),
                dominance=track_data.get("dominance", 0.5),
                depth=track_data.get("depth", 0.5),
                resonance=track_data.get("popularity", 0.5)
            )
        )
    
    async def _find_tracks_for_emotion(self, tracks: List[PlaylistTrack], target_emotion: EmotionalPoint, 
                                     preferences: Dict[str, Any]) -> List[Tuple[PlaylistTrack, float]]:
        """Find tracks that match a target emotional state"""
        scored_tracks = []
        
        for track in tracks:
            # Calculate emotional distance
            distance = track.emotional_profile.distance_to(target_emotion)
            
            # Apply preferences weighting
            familiarity_weight = preferences.get("familiarity_preference", 0.5)
            popularity_boost = track.emotional_profile.resonance * familiarity_weight
            
            # Calculate final score (lower distance is better)
            score = 1.0 / (1.0 + distance) + popularity_boost * 0.2
            
            scored_tracks.append((track, score))
        
        # Sort by score
        scored_tracks.sort(key=lambda x: x[1], reverse=True)
        
        return scored_tracks
    
    async def _select_best_track(self, scored_tracks: List[Tuple[PlaylistTrack, float]], 
                               existing_tracks: List[PlaylistTrack], 
                               preferences: Dict[str, Any]) -> Optional[PlaylistTrack]:
        """Select the best track avoiding duplicates and respecting diversity"""
        existing_artist_counts = {}
        for track in existing_tracks:
            existing_artist_counts[track.artist] = existing_artist_counts.get(track.artist, 0) + 1
        
        for track, score in scored_tracks:
            # Skip if artist already has too many tracks
            max_artist_tracks = preferences.get("max_artist_tracks", 2)
            if existing_artist_counts.get(track.artist, 0) >= max_artist_tracks:
                continue
            
            # Skip if track is already in playlist
            if any(t.id == track.id for t in existing_tracks):
                continue
            
            return track
        
        return None
    
    async def _generate_transition_notes(self, from_emotion: EmotionalPoint, to_emotion: EmotionalPoint) -> str:
        """Generate notes about the emotional transition between tracks"""
        valence_change = to_emotion.valence - from_emotion.valence
        arousal_change = to_emotion.arousal - from_emotion.arousal
        
        if valence_change > 0.2:
            mood_change = "lifting"
        elif valence_change < -0.2:
            mood_change = "deepening"
        else:
            mood_change = "maintaining"
        
        if arousal_change > 0.2:
            energy_change = "energizing"
        elif arousal_change < -0.2:
            energy_change = "calming"
        else:
            energy_change = "steady"
        
        return f"{mood_change} and {energy_change} transition"
    
    async def _adjust_playlist_duration(self, tracks: List[PlaylistTrack], target_duration_minutes: int, 
                                      available_tracks: List[PlaylistTrack]) -> List[PlaylistTrack]:
        """Adjust playlist to meet target duration"""
        current_duration = sum(track.duration for track in tracks) // 60  # Convert to minutes
        target_duration = target_duration_minutes
        
        if current_duration < target_duration:
            # Add more tracks
            remaining_duration = target_duration - current_duration
            avg_track_duration = np.mean([track.duration for track in available_tracks]) // 60
            
            tracks_needed = max(1, int(remaining_duration / avg_track_duration))
            
            # Add tracks that fit the emotional progression
            for _ in range(tracks_needed):
                if len(available_tracks) == 0:
                    break
                
                # Find track that extends the emotional journey
                best_track = None
                best_score = -1
                
                for track in available_tracks:
                    if track in tracks:
                        continue
                    
                    # Score based on emotional continuity
                    if tracks:
                        last_track = tracks[-1]
                        emotional_distance = track.emotional_profile.distance_to(last_track.emotional_profile)
                        score = 1.0 / (1.0 + emotional_distance)
                    else:
                        score = 0.5
                    
                    if score > best_score:
                        best_score = score
                        best_track = track
                
                if best_track:
                    tracks.append(best_track)
        
        elif current_duration > target_duration:
            # Remove tracks while maintaining emotional flow
            while current_duration > target_duration and len(tracks) > 1:
                # Remove track that disrupts flow the least
                best_removal_index = 0
                best_flow_score = float('inf')
                
                for i in range(1, len(tracks) - 1):
                    # Calculate flow disruption if this track is removed
                    before_track = tracks[i-1]
                    after_track = tracks[i+1]
                    disruption = after_track.emotional_profile.distance_to(before_track.emotional_profile)
                    
                    if disruption < best_flow_score:
                        best_flow_score = disruption
                        best_removal_index = i
                
                tracks.pop(best_removal_index)
                current_duration = sum(track.duration for track in tracks) // 60
        
        return tracks
    
    async def _generate_playlist_name(self, playlist_type: PlaylistType, user_emotion: Dict[str, float]) -> str:
        """Generate an appropriate name for the playlist"""
        name_templates = {
            PlaylistType.EMOTIONAL_JOURNEY: "Emotional Journey Through Sound",
            PlaylistType.MOOD_MAINTENANCE: "Steady State Sessions",
            PlaylistType.ENERGY_BUILDING: "Energy Ascension",
            PlaylistType.CONTEMPLATIVE_DIVE: "Deep Contemplation",
            PlaylistType.DISCOVERY_EXPEDITION: "Sonic Discovery Expedition",
            PlaylistType.NOSTALGIC_VOYAGE: "Nostalgic Sound Voyage",
            PlaylistType.ECSTATIC_RELEASE: "Ecstatic Energy Release",
            PlaylistType.HEALING_SESSION: "Healing Sound Session"
        }
        
        base_name = name_templates.get(playlist_type, "Curated Sound Experience")
        
        # Add emotional context
        valence = user_emotion.get("valence", 0.5)
        arousal = user_emotion.get("arousal", 0.5)
        
        if valence > 0.7 and arousal > 0.7:
            mood_descriptor = "Energetic Joy"
        elif valence > 0.7:
            mood_descriptor = "Peaceful Contentment"
        elif valence < 0.3:
            mood_descriptor = "Contemplative Depth"
        elif arousal > 0.7:
            mood_descriptor = "Dynamic Energy"
        else:
            mood_descriptor = "Balanced Flow"
        
        return f"{base_name}: {mood_descriptor}"
    
    async def _generate_playlist_description(self, route: MoodRoute, playlist_type: PlaylistType) -> str:
        """Generate a description for the playlist"""
        start_desc = await self._describe_emotional_point(route.start_point)
        end_desc = await self._describe_emotional_point(route.end_point)
        
        return f"A carefully crafted {playlist_type.value.replace('_', ' ')} that begins with {start_desc} and journeys toward {end_desc}. This playlist respects your emotional state while guiding you through a meaningful musical experience."
    
    async def _describe_emotional_point(self, point: EmotionalPoint) -> str:
        """Generate a human-readable description of an emotional point"""
        valence_desc = "positive" if point.valence > 0.6 else "contemplative" if point.valence < 0.4 else "balanced"
        energy_desc = "high energy" if point.arousal > 0.7 else "gentle" if point.arousal < 0.4 else "moderate energy"
        
        return f"{valence_desc} and {energy_desc} moments"
    
    async def _create_fallback_playlist(self, user_request: Dict[str, Any], available_tracks: List[Dict[str, Any]]) -> DynamicPlaylist:
        """Create a safe fallback playlist when generation fails"""
        tracks = []
        for i, track_data in enumerate(available_tracks[:10]):  # Limit to 10 tracks
            track = await self._create_playlist_track(track_data)
            tracks.append(track)
        
        route = MoodRoute(
            start_point=EmotionalPoint(0.0, 0.6, 0.5, 0.6, 0.5, 0.7),
            end_point=EmotionalPoint(1.0, 0.6, 0.5, 0.6, 0.5, 0.7),
            waypoints=[],
            arc_type="stable",
            transition_style="smooth",
            total_duration=60,
            estimated_impact=0.5
        )
        
        return DynamicPlaylist(
            id=str(uuid.uuid4()),
            name="Curated Selection",
            description="A thoughtfully selected collection of tracks",
            type=PlaylistType.EMOTIONAL_JOURNEY,
            status=PlaylistStatus.READY,
            route=route,
            tracks=tracks,
            total_duration=sum(track.duration for track in tracks)
        )
    
    async def adapt_playlist(self, playlist_id: str, feedback: Dict[str, Any]) -> DynamicPlaylist:
        """
        Adapt playlist based on user feedback and listening patterns
        
        Args:
            playlist_id: ID of playlist to adapt
            feedback: User feedback and listening data
        
        Returns:
            Updated DynamicPlaylist object
        """
        playlist = self.playlist_cache.get(playlist_id)
        if not playlist:
            raise ValueError(f"Playlist {playlist_id} not found")
        
        # Record feedback
        playlist.play_history.append({
            "timestamp": datetime.utcnow().isoformat(),
            "feedback": feedback
        })
        
        # Adapt based on feedback type
        adaptation_type = feedback.get("type")
        
        if adaptation_type == "skip_frequency":
            await self._adapt_to_skips(playlist, feedback)
        elif adaptation_type == "emotional_response":
            await self._adapt_to_emotional_feedback(playlist, feedback)
        elif adaptation_type == "completion_rate":
            await self._adapt_to_completion_patterns(playlist, feedback)
        
        playlist.updated_at = datetime.utcnow()
        return playlist
    
    async def _adapt_to_skips(self, playlist: DynamicPlaylist, feedback: Dict[str, Any]):
        """Adapt playlist based on skip patterns"""
        skip_data = feedback.get("skip_data", {})
        
        # Identify problematic tracks
        high_skip_tracks = []
        for track_id, skip_rate in skip_data.items():
            if skip_rate > 0.7:  # 70% skip rate
                high_skip_tracks.append(track_id)
        
        # Replace problematic tracks
        for track in playlist.tracks:
            if track.id in high_skip_tracks:
                # Find replacement track with similar emotional profile but better reception
                replacement = await self._find_replacement_track(track, playlist.tracks)
                if replacement:
                    playlist.tracks[playlist.tracks.index(track)] = replacement
    
    async def _adapt_to_emotional_feedback(self, playlist: DynamicPlaylist, feedback: Dict[str, Any]):
        """Adapt playlist based on emotional feedback"""
        emotional_response = feedback.get("emotional_response", {})
        
        # Adjust emotional route based on actual user response
        if emotional_response.get("overall_satisfaction", 0.5) < 0.4:
            # Recreate route with different parameters
            new_route = await self.mood_router.create_emotional_route(
                user_emotion=emotional_response.get("current_state", {}),
                target_emotion=None,  # Let system determine target
                duration_minutes=playlist.route.total_duration,
                preferences=playlist.user_preferences
            )
            
            playlist.route = new_route
            
            # Update track selection to match new route
            new_tracks = await self._select_tracks_for_route(new_route, playlist.tracks, playlist.user_preferences)
            playlist.tracks = new_tracks
    
    async def _adapt_to_completion_patterns(self, playlist: DynamicPlaylist, feedback: Dict[str, Any]):
        """Adapt playlist based on completion patterns"""
        completion_rate = feedback.get("completion_rate", 1.0)
        
        if completion_rate < 0.5:
            # Playlist too long or not engaging enough
            target_duration = int(playlist.route.total_duration * 0.7)  # Reduce by 30%
            playlist.tracks = await self._adjust_playlist_duration(playlist.tracks, target_duration, playlist.tracks)
            playlist.route.total_duration = target_duration