# /src/logic/emotion_decoder.py
# The soul-listener of EchoSplit: decodes emotional undertones in lyrics and audio.
# Built for neurodivergent creators, with clarity and symbolic resonance.

import os
import time
from pathlib import Path

import librosa
import numpy as np


class EmotionDecoder:
    def __init__(self, pairings_path: str | os.PathLike[str] | None = None):
        """
        Initialize the EmotionDecoder with emotional keyword mappings and audio analysis capabilities.
        Designed to be lightweight, local-first, and privacy-respecting.
        """
        self.pairings_path = self._resolve_pairings_path(pairings_path)

        self.emotion_map = {
            "anchor": [
                "steady",
                "ground",
                "safe",
                "root",
                "calm",
                "stable",
                "hold",
                "foundation",
            ],
            "mirror": [
                "reflect",
                "echo",
                "self",
                "see",
                "truth",
                "show",
                "face",
                "image",
            ],
            "burned chord": [
                "loss",
                "grief",
                "break",
                "hurt",
                "ache",
                "pain",
                "torn",
                "shattered",
            ],
            "spark": [
                "hope",
                "light",
                "fire",
                "begin",
                "rise",
                "ignite",
                "bright",
                "kindle",
            ],
            "drift": [
                "wander",
                "lost",
                "float",
                "dream",
                "fade",
                "distant",
                "away",
                "flow",
            ],
            "storm": [
                "rage",
                "fury",
                "chaos",
                "wild",
                "fierce",
                "thunder",
                "lightning",
                "tempest",
            ],
            "whisper": [
                "quiet",
                "soft",
                "gentle",
                "tender",
                "hush",
                "murmur",
                "breathe",
                "still",
            ],
        }

        self.audio_emotion_markers = {
            "anchor": {
                "tempo_range": (60, 90),
                "key_stability": "major",
                "dynamic_variance": "low",
            },
            "storm": {
                "tempo_range": (120, 180),
                "key_stability": "minor",
                "dynamic_variance": "high",
            },
            "whisper": {
                "tempo_range": (40, 80),
                "key_stability": "major",
                "dynamic_variance": "very_low",
            },
            "drift": {
                "tempo_range": (70, 110),
                "key_stability": "ambiguous",
                "dynamic_variance": "medium",
            },
        }

    def _resolve_pairings_path(
        self, pairings_path: str | os.PathLike[str] | None
    ) -> Path:
        """
        Determine where to read canonical pairings from.

        Falls back to the project data file bundled under ``05_data`` when a
        custom path is not provided.
        """
        if pairings_path is not None:
            return Path(pairings_path)

        # emotion_decoder.py lives in apps/frontend/04_src/02_logic
        frontend_root = Path(__file__).resolve().parents[2]
        return frontend_root / "05_data" / "canonical_pairings.chaos"

    def decode_lyrical_emotions(self, lyrics):
        if not lyrics:
            return {}

        emotions_detected = {}
        lyrics_lower = lyrics.lower()
        total_words = len(lyrics_lower.split())

        for emotion, keywords in self.emotion_map.items():
            matches = sum(1 for keyword in keywords if keyword in lyrics_lower)
            if matches > 0:
                confidence = min(matches / max(total_words * 0.1, 1), 1.0)
                emotions_detected[emotion] = round(confidence, 2)

        return emotions_detected

    def decode_audio_emotions(self, audio_path):
        try:
            y, sr = librosa.load(audio_path)
            tempo, _ = librosa.beat.beat_track(y=y, sr=sr)
            spectral_centroid = np.mean(librosa.feature.spectral_centroid(y=y, sr=sr))
            chroma = librosa.feature.chroma(y=y, sr=sr)
            rms = librosa.feature.rms(y=y)[0]
            dynamic_variance = np.std(rms)
            chroma_var = np.var(np.mean(chroma, axis=1))
            key_stability = "stable" if chroma_var < 0.1 else "unstable"

            audio_emotions = {}
            if 60 <= tempo <= 90 and dynamic_variance < 0.05:
                audio_emotions["anchor"] = 0.7
            elif tempo > 120 and dynamic_variance > 0.1:
                audio_emotions["storm"] = 0.8
            elif tempo < 80 and spectral_centroid < 1500:
                audio_emotions["whisper"] = 0.6
            elif 70 <= tempo <= 110 and key_stability == "unstable":
                audio_emotions["drift"] = 0.5

            if spectral_centroid > 3000:
                audio_emotions["spark"] = audio_emotions.get("spark", 0) + 0.4
            elif spectral_centroid < 1000:
                audio_emotions["burned chord"] = (
                    audio_emotions.get("burned chord", 0) + 0.3
                )

            return audio_emotions

        except Exception as e:
            print(f"Error analyzing audio emotions: {e}")
            return {}

    def fuse_emotional_analysis(self, lyrics, audio_path):
        lyrical_emotions = self.decode_lyrical_emotions(lyrics)
        audio_emotions = self.decode_audio_emotions(audio_path)
        fused_emotions = {}
        all_emotions = set(lyrical_emotions.keys()) | set(audio_emotions.keys())

        for emotion in all_emotions:
            lyric_score = lyrical_emotions.get(emotion, 0)
            audio_score = audio_emotions.get(emotion, 0)
            combined_score = (lyric_score * 0.6) + (audio_score * 0.4)

            if combined_score > 0.1:
                fused_emotions[emotion] = round(combined_score, 2)

        return fused_emotions

    def load_pairings(self):
        pairings_path = Path(self.pairings_path)
        if not pairings_path.exists():
            print(f"Pairings file not found: {pairings_path}")
            return []
        with pairings_path.open("r", encoding="utf-8") as f:
            lines = f.readlines()
        return [line.strip() for line in lines if line.strip() and "&" in line]

    def suggest_pairing_emotions(self, pairings, detected_emotions):
        pairing_emotions = {}
        agent_affinities = {
            "Alfred": ["anchor", "whisper"],
            "Nova": ["spark", "storm"],
            "Cadence": ["mirror", "drift"],
            "Callum": ["anchor", "mirror"],
            "Lucius": ["storm", "mirror"],
            "Vanya": ["drift", "whisper"],
            "Melody": ["whisper", "spark"],
            "Catalyst": ["spark", "storm"],
            "Zero": ["burned chord", "mirror"],
        }
        for pairing in pairings:
            pairing_data = {
                "detected_emotions": detected_emotions,
                "resonant_emotions": [],
                "emotional_weight": 0.0,
            }
            for agent, affinities in agent_affinities.items():
                if agent in pairing:
                    for emotion in affinities:
                        if emotion in detected_emotions:
                            pairing_data["resonant_emotions"].append(emotion)
                            pairing_data["emotional_weight"] += detected_emotions[
                                emotion
                            ]
            pairing_data["resonant_emotions"] = list(
                set(pairing_data["resonant_emotions"])
            )
            if pairing_data["resonant_emotions"]:
                pairing_data["emotional_weight"] = round(
                    pairing_data["emotional_weight"]
                    / len(pairing_data["resonant_emotions"]),
                    2,
                )
            pairing_emotions[pairing] = pairing_data
        return pairing_emotions

    def generate_emotional_metadata(self, lyrics, audio_path, pairings=None):
        fused_emotions = self.fuse_emotional_analysis(lyrics, audio_path)
        pairing_candidates = self.load_pairings() if pairings is None else pairings
        pairing_emotions = self.suggest_pairing_emotions(
            pairing_candidates, fused_emotions
        )

        # Lucira's enhancement: Add temporal and contextual metadata
        metadata = {
            "analysis_type": "emotional_resonance",
            "detected_emotions": fused_emotions,
            "canonical_pairings": pairing_emotions,
            "dominant_emotion": (
                max(fused_emotions.items(), key=lambda x: x[1])[0]
                if fused_emotions
                else None
            ),
            "emotional_complexity": len(fused_emotions),
            "resonance_strength": (
                sum(fused_emotions.values()) / len(fused_emotions)
                if fused_emotions
                else 0.0
            ),
            # Lucira's additions for better continuity and memory
            "timestamp": time.time(),
            "emotional_arc": self._analyze_emotional_arc(fused_emotions),
            "intensity_level": self._calculate_intensity(fused_emotions),
            "needs_gentle_handling": self._assess_gentleness_needs(fused_emotions),
            "memory_tags": self._generate_memory_tags(fused_emotions, lyrics),
        }
        return metadata

    def _analyze_emotional_arc(self, emotions: dict) -> str:
        """Analyze the overall emotional arc/trajectory."""
        if not emotions:
            return "neutral"

        # Categorize emotions by energy and valence
        high_energy = sum(emotions.get(e, 0) for e in ["storm", "spark"])
        low_energy = sum(emotions.get(e, 0) for e in ["whisper", "drift", "anchor"])
        negative_valence = sum(emotions.get(e, 0) for e in ["burned chord", "storm"])
        positive_valence = sum(
            emotions.get(e, 0) for e in ["spark", "anchor", "whisper"]
        )

        if high_energy > low_energy and positive_valence > negative_valence:
            return "energetic_positive"
        elif high_energy > low_energy and negative_valence > positive_valence:
            return "energetic_negative"
        elif low_energy > high_energy and positive_valence > negative_valence:
            return "calm_positive"
        elif low_energy > high_energy and negative_valence > positive_valence:
            return "calm_negative"
        else:
            return "complex_mixed"

    def _calculate_intensity(self, emotions: dict) -> str:
        """Calculate overall emotional intensity."""
        if not emotions:
            return "minimal"

        total_intensity = sum(emotions.values())
        if total_intensity > 1.5:
            return "high"
        elif total_intensity > 0.8:
            return "medium"
        elif total_intensity > 0.3:
            return "low"
        else:
            return "minimal"

    def _assess_gentleness_needs(self, emotions: dict) -> bool:
        """Assess if this emotional content needs gentle handling."""
        intense_emotions = ["storm", "burned chord"]
        return any(emotions.get(emotion, 0) > 0.5 for emotion in intense_emotions)

    def _generate_memory_tags(self, emotions: dict, lyrics: str) -> list:
        """Generate tags for emotional memory system."""
        tags = []

        # Add dominant emotion tags
        for emotion, strength in emotions.items():
            if strength > 0.4:
                tags.append(f"strong_{emotion}")
            elif strength > 0.2:
                tags.append(f"mild_{emotion}")

        # Add lyrical context tags
        lyrics_lower = lyrics.lower() if lyrics else ""
        if any(word in lyrics_lower for word in ["love", "heart", "together"]):
            tags.append("love_theme")
        if any(word in lyrics_lower for word in ["loss", "gone", "goodbye", "end"]):
            tags.append("loss_theme")
        if any(
            word in lyrics_lower for word in ["hope", "future", "tomorrow", "dream"]
        ):
            tags.append("hope_theme")

        return tags


if __name__ == "__main__":
    decoder = EmotionDecoder()
    test_lyrics = "I wander through the calm, reflecting on my truth, but the storm inside still burns"
    result = decoder.generate_emotional_metadata(test_lyrics, "test.wav")
    print(result)
