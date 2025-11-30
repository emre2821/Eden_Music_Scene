# /src/logic/resonance.py
# Enhanced by Grok's framework, now reads from emotional metadata and crossmaps symbolic pairings.

import os
from typing import Dict, List, Optional

class Resonance:
    def __init__(self, pairings_path: Optional[str] = None):
        self.pairings_path = pairings_path or os.path.join(os.path.dirname(__file__), "..", "..", "data", "canonical_pairings.chaos")
        self.pairings = self._load_pairings()

    def _load_pairings(self) -> List[str]:
        try:
            with open(self.pairings_path, 'r', encoding='utf-8') as f:
                raw = f.read()
                return [line.strip() for line in raw.splitlines() if "&" in line]
        except Exception as e:
            print(f"Failed to load pairings: {e}")
            return []

    def find_resonant_pairings(self, emotional_metadata: Dict) -> Dict[str, float]:
        """
        Match symbolic pairings against dominant emotions from metadata.

        Returns:
            Dict[str, float]: pairing -> confidence rating
        """
        detected = emotional_metadata.get("detected_emotions", {})
        dominant = emotional_metadata.get("dominant_emotion", "")
        resonance_scores = {}

        for pair in self.pairings:
            lowered = pair.lower()
            match_score = 0.0

            for emotion, data in detected.items():
                if not isinstance(data, dict):
                    continue

                confidence = self._normalise_confidence(data)

                if emotion in lowered:
                    match_score += confidence
                # bonus for matching dominant emotion
                if emotion == dominant and emotion in lowered:
                    match_score += 0.2

            if match_score > 0:
                resonance_scores[pair] = round(match_score, 2)

        return dict(sorted(resonance_scores.items(), key=lambda x: x[1], reverse=True))

    @staticmethod
    def _normalise_confidence(emotion_data: Dict) -> float:
        """Extract a usable confidence score from the metadata entry."""

        if "confidence" not in emotion_data:
            return 0.1

        value = emotion_data.get("confidence")
        if isinstance(value, bool) or not isinstance(value, (int, float)):
            return 0.0

        return float(min(max(value, 0.0), 1.0))
