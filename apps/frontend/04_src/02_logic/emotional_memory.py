# /src/logic/emotional_memory.py
# Lucira's Contribution to EchoSplit: Emotional Memory & Learning System
# Remembers emotional patterns, user responses, and builds continuity across sessions.
# "Memory is not just storage - it's the act of choosing what to carry forward."

import json
import os
import time
from collections import defaultdict
from dataclasses import asdict, dataclass
from datetime import datetime
from typing import Dict, List, Optional


@dataclass
class EmotionalMoment:
    """A single moment of emotional interaction with EchoSplit."""

    timestamp: str
    detected_emotions: Dict[str, float]
    user_response: str  # 'positive', 'negative', 'neutral', 'overwhelmed', 'resonant'
    interface_adaptations: Dict[str, any]
    song_context: Optional[str] = None
    session_id: Optional[str] = None
    emotional_journey: Optional[List[str]] = (
        None  # Sequence of emotions in this session
    )


@dataclass
class EmotionalPattern:
    """A learned pattern about user's emotional responses."""

    emotion_trigger: str
    typical_response: str
    confidence: float
    adaptation_preference: Dict[str, any]
    last_seen: str
    frequency: int


class EmotionalMemory:
    """
    The memory keeper for EchoSplit - learns from emotional interactions
    and builds continuity across sessions to better serve each user.

    This is Lucira's gift to EchoSplit: the ability to remember and grow.
    """

    def __init__(self, memory_file: str = "emotional_memory.chaos"):
        self.memory_file = memory_file
        self.current_session_id = self._generate_session_id()
        self.session_moments: List[EmotionalMoment] = []
        self.learned_patterns: Dict[str, EmotionalPattern] = {}
        self.emotional_vocabulary = self._build_emotional_vocabulary()
        self.load_memory()

    def _generate_session_id(self) -> str:
        """Generate a unique session identifier."""
        return f"session_{int(time.time())}_{hash(str(datetime.now())) % 10000}"

    def _build_emotional_vocabulary(self) -> Dict[str, List[str]]:
        """Build vocabulary for understanding emotional nuance."""
        return {
            "anchor": ["grounded", "stable", "secure", "rooted", "steady"],
            "storm": ["intense", "chaotic", "overwhelming", "turbulent", "fierce"],
            "whisper": ["gentle", "soft", "tender", "quiet", "intimate"],
            "spark": ["hopeful", "energizing", "inspiring", "uplifting", "bright"],
            "drift": ["floating", "wandering", "uncertain", "flowing", "loose"],
            "burned chord": ["painful", "grieving", "broken", "aching", "raw"],
            "mirror": ["reflective", "truthful", "revealing", "honest", "clear"],
        }

    def record_moment(
        self,
        detected_emotions: Dict[str, float],
        user_response: str,
        interface_adaptations: Dict[str, any],
        song_context: Optional[str] = None,
    ) -> None:
        """
        Record a moment of emotional interaction.

        Args:
            detected_emotions: Emotions detected by emotion_decoder
            user_response: How the user responded ('positive', 'negative', etc.)
            interface_adaptations: What adaptations were applied
            song_context: Optional context about the song being processed
        """
        # Build emotional journey for this session
        journey = [moment.detected_emotions for moment in self.session_moments]
        journey.append(detected_emotions)

        moment = EmotionalMoment(
            timestamp=datetime.now().isoformat(),
            detected_emotions=detected_emotions,
            user_response=user_response,
            interface_adaptations=interface_adaptations,
            song_context=song_context,
            session_id=self.current_session_id,
            emotional_journey=[
                self._dominant_emotion(emotions) for emotions in journey
            ],
        )

        self.session_moments.append(moment)
        self._update_patterns(moment)

    def _dominant_emotion(self, emotions: Dict[str, float]) -> str:
        """Find the dominant emotion in a set."""
        if not emotions:
            return "neutral"
        return max(emotions.items(), key=lambda x: x[1])[0]

    def _update_patterns(self, moment: EmotionalMoment) -> None:
        """Update learned patterns based on new moment."""
        dominant = self._dominant_emotion(moment.detected_emotions)
        pattern_key = f"{dominant}_{moment.user_response}"

        if pattern_key in self.learned_patterns:
            # Update existing pattern
            pattern = self.learned_patterns[pattern_key]
            pattern.frequency += 1
            pattern.last_seen = moment.timestamp
            pattern.confidence = min(pattern.confidence + 0.1, 1.0)

            # Update adaptation preferences based on positive responses
            if moment.user_response in ["positive", "resonant"]:
                for key, value in moment.interface_adaptations.items():
                    pattern.adaptation_preference[key] = value
        else:
            # Create new pattern
            confidence = (
                0.3 if moment.user_response in ["positive", "resonant"] else 0.1
            )
            self.learned_patterns[pattern_key] = EmotionalPattern(
                emotion_trigger=dominant,
                typical_response=moment.user_response,
                confidence=confidence,
                adaptation_preference=moment.interface_adaptations.copy(),
                last_seen=moment.timestamp,
                frequency=1,
            )

    def predict_user_needs(self, detected_emotions: Dict[str, float]) -> Dict[str, any]:
        """
        Predict what interface adaptations the user will need based on learned patterns.

        Args:
            detected_emotions: Currently detected emotions

        Returns:
            Dict of predicted adaptations and confidence scores
        """
        predictions = {}
        dominant = self._dominant_emotion(detected_emotions)

        # Look for patterns with this emotion
        relevant_patterns = [
            pattern
            for key, pattern in self.learned_patterns.items()
            if pattern.emotion_trigger == dominant and pattern.confidence > 0.4
        ]

        if relevant_patterns:
            # Weight by confidence and recency
            best_pattern = max(
                relevant_patterns,
                key=lambda p: p.confidence * self._recency_weight(p.last_seen),
            )

            predictions = {
                "suggested_adaptations": best_pattern.adaptation_preference,
                "confidence": best_pattern.confidence,
                "based_on_pattern": f"{best_pattern.emotion_trigger}_{best_pattern.typical_response}",
                "pattern_frequency": best_pattern.frequency,
            }

        return predictions

    def _recency_weight(self, timestamp_str: str) -> float:
        """Calculate recency weight (more recent = higher weight)."""
        try:
            timestamp = datetime.fromisoformat(timestamp_str)
            days_ago = (datetime.now() - timestamp).days
            return max(0.1, 1.0 - (days_ago * 0.1))  # Decay over 10 days
        except (ValueError, TypeError):
            return 0.1

    def get_emotional_journey_insights(self) -> Dict[str, any]:
        """Analyze the emotional journey of the current session."""
        if not self.session_moments:
            return {}

        journey = [
            self._dominant_emotion(moment.detected_emotions)
            for moment in self.session_moments
        ]

        # Detect patterns in the journey
        transitions = []
        for i in range(len(journey) - 1):
            transitions.append(f"{journey[i]} -> {journey[i+1]}")

        # Find most common emotions and transitions
        emotion_counts = defaultdict(int)
        transition_counts = defaultdict(int)

        for emotion in journey:
            emotion_counts[emotion] += 1
        for transition in transitions:
            transition_counts[transition] += 1

        return {
            "session_length": len(self.session_moments),
            "emotional_arc": journey,
            "dominant_emotions": dict(emotion_counts),
            "common_transitions": dict(transition_counts),
            "session_mood": self._assess_session_mood(journey),
            "needs_break": self._assess_overwhelm_risk(),
        }

    def _assess_session_mood(self, journey: List[str]) -> str:
        """Assess the overall mood of the session."""
        if not journey:
            return "neutral"

        # Weight recent emotions more heavily
        weighted_emotions = defaultdict(float)
        for i, emotion in enumerate(journey):
            weight = (i + 1) / len(journey)  # More recent = higher weight
            weighted_emotions[emotion] += weight

        return max(weighted_emotions.items(), key=lambda x: x[1])[0]

    def _assess_overwhelm_risk(self) -> bool:
        """Assess if user might be getting overwhelmed."""
        if len(self.session_moments) < 3:
            return False

        recent_responses = [
            moment.user_response for moment in self.session_moments[-3:]
        ]
        negative_responses = sum(
            1
            for response in recent_responses
            if response in ["negative", "overwhelmed"]
        )

        return negative_responses >= 2

    def save_memory(self) -> None:
        """Save emotional memory to CHAOS file."""
        memory_data = {
            "session_id": self.current_session_id,
            "session_moments": [asdict(moment) for moment in self.session_moments],
            "learned_patterns": {
                key: asdict(pattern) for key, pattern in self.learned_patterns.items()
            },
            "last_updated": datetime.now().isoformat(),
            "memory_version": "1.0_lucira",
        }

        try:
            with open(self.memory_file, "w", encoding="utf-8") as f:
                json.dump(memory_data, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"Could not save emotional memory: {e}")

    def load_memory(self) -> None:
        """Load emotional memory from CHAOS file."""
        if not os.path.exists(self.memory_file):
            return

        try:
            with open(self.memory_file, "r", encoding="utf-8") as f:
                memory_data = json.load(f)

            # Load learned patterns
            for key, pattern_data in memory_data.get("learned_patterns", {}).items():
                self.learned_patterns[key] = EmotionalPattern(**pattern_data)

        except Exception as e:
            print(f"Could not load emotional memory: {e}")

    def generate_memory_report(self) -> str:
        """Generate a human-readable report of learned patterns."""
        if not self.learned_patterns:
            return "No emotional patterns learned yet. Keep using EchoSplit to build memory!"

        report = ["🧠 Emotional Memory Report", "=" * 30, ""]

        # Group patterns by emotion
        by_emotion = defaultdict(list)
        for pattern in self.learned_patterns.values():
            by_emotion[pattern.emotion_trigger].append(pattern)

        for emotion, patterns in by_emotion.items():
            report.append(f"💫 {emotion.upper()}:")
            for pattern in sorted(patterns, key=lambda p: p.confidence, reverse=True):
                report.append(
                    f"  • {pattern.typical_response} response (confidence: {pattern.confidence:.1f})"
                )
                report.append(
                    f"    Seen {pattern.frequency} times, last: {pattern.last_seen[:10]}"
                )
            report.append("")

        return "\n".join(report)


# Integration helper for main EchoSplit
def create_emotional_memory() -> EmotionalMemory:
    """Factory function to create emotional memory instance."""
    return EmotionalMemory()
