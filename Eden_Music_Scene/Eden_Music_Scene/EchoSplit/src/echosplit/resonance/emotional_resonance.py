"""
Emotional Resonance Analysis Engine
Advanced analysis of emotional resonance patterns in audio components
"""

import asyncio
import numpy as np
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime
import structlog
import librosa
from scipy import signal
from scipy.stats import entropy
from sklearn.cluster import KMeans
from sklearn.decomposition import PCA

from ..lyss.daemon import LyssDaemon, EmotionalResonance, ResonanceLevel
from ..ethical_framework import EthicalAI

logger = structlog.get_logger(__name__)


class ResonancePattern(Enum):
    """Types of emotional resonance patterns"""
    SUSTAINED = "sustained"
    PULSATING = "pulsating"
    BUILDING = "building"
    FADING = "fading"
    OSCILLATING = "oscillating"
    SURGE = "surge"
    WAVE = "wave"
    STATIC = "static"


class ResonanceHarmonic(Enum):
    """Harmonic relationships in resonance"""
    FUNDAMENTAL = "fundamental"
    OCTAVE = "octave"
    FIFTH = "fifth"
    THIRD = "third"
    SEVENTH = "seventh"
    DISSONANT = "dissonant"


@dataclass
class ResonanceSignature:
    """Signature pattern of emotional resonance"""
    pattern_type: ResonancePattern
    frequency_center: float  # Hz
    frequency_spread: float  # Hz
    temporal_duration: float  # seconds
    intensity_profile: List[float]  # Intensity over time
    harmonic_content: Dict[ResonanceHarmonic, float]
    emotional_quality: str
    resonance_level: ResonanceLevel
    confidence: float  # 0.0 to 1.0


@dataclass
class ResonanceTimeline:
    """Timeline of emotional resonance events"""
    total_duration: float
    resonance_events: List[EmotionalResonance] = field(default_factory=list)
    signature_patterns: List[ResonanceSignature] = field(default_factory=list)
    emotional_arc: List[Tuple[float, float, str]] = field(default_factory=list)  # (time, intensity, quality)


class EmotionalResonanceEngine:
    """
    Advanced engine for analyzing emotional resonance in audio
    
    Provides deep analysis of how different frequency components
    and temporal patterns create emotional resonance.
    """
    
    def __init__(self):
        self.lyss_daemon = LyssDaemon()
        self.ethical_ai = EthicalAI()
        
        # Analysis parameters
        self.resonance_window = 0.5  # seconds
        self.frequency_bands = [
            (20, 80),    # Sub-bass
            (80, 250),   # Bass
            (250, 500),  # Low midrange
            (500, 2000), # Midrange
            (2000, 4000), # Upper midrange
            (4000, 8000), # Presence
            (8000, 20000) # Brilliance
        ]
        
        # Resonance detection thresholds
        self.intensity_threshold = 0.6
        self.duration_threshold = 0.1  # seconds
        self.frequency_stability_threshold = 0.8
        
        logger.info("EmotionalResonanceEngine initialized")
    
    async def analyze_resonance_timeline(self,
                                       audio_data: np.ndarray,
                                       sample_rate: int,
                                       user_consent: Dict[str, bool]) -> ResonanceTimeline:
        """
        Analyze emotional resonance timeline throughout audio
        
        Args:
            audio_data: Audio waveform data
            sample_rate: Audio sample rate
            user_consent: User consent for processing
        
        Returns:
            ResonanceTimeline with detailed resonance analysis
        """
        try:
            # Validate ethical compliance
            is_permitted, violations = await self.ethical_ai.evaluate_action(
                "analyze_resonance_timeline", {
                    "audio_shape": audio_data.shape,
                    "sample_rate": sample_rate,
                    "consent": user_consent
                }
            )
            
            if not is_permitted:
                logger.warning("Ethical violations in resonance analysis request")
                return await self._create_safe_resonance_timeline(audio_data, sample_rate)
            
            # Get basic emotional resonances from Lyss
            basic_resonances = await self.lyss_daemon._detect_emotional_resonance(
                await self.lyss_daemon._extract_comprehensive_features(audio_data, sample_rate),
                audio_data,
                sample_rate
            )
            
            # Enhance resonances with detailed analysis
            enhanced_resonances = await self._enhance_resonance_analysis(
                basic_resonances, audio_data, sample_rate
            )
            
            # Detect resonance patterns
            signature_patterns = await self._detect_resonance_patterns(
                enhanced_resonances, audio_data, sample_rate
            )
            
            # Build emotional arc
            emotional_arc = await self._build_emotional_arc(
                enhanced_resonances, audio_data, sample_rate
            )
            
            # Create timeline
            timeline = ResonanceTimeline(
                total_duration=len(audio_data) / sample_rate,
                resonance_events=enhanced_resonances,
                signature_patterns=signature_patterns,
                emotional_arc=emotional_arc
            )
            
            logger.info("Resonance timeline analysis completed", extra={
                "resonance_events": len(enhanced_resonances),
                "signature_patterns": len(signature_patterns),
                "duration": timeline.total_duration
            })
            
            return timeline
            
        except Exception as e:
            logger.error(f"Error in resonance timeline analysis: {e}")
            return await self._create_safe_resonance_timeline(audio_data, sample_rate)
    
    async def analyze_frequency_resonance(self,
                                        audio_data: np.ndarray,
                                        sample_rate: int,
                                        user_consent: Dict[str, bool]) -> Dict[str, Any]:
        """
        Analyze emotional resonance by frequency bands
        
        Args:
            audio_data: Audio waveform data
            sample_rate: Audio sample rate
            user_consent: User consent for processing
        
        Returns:
            Frequency-based resonance analysis
        """
        try:
            # Validate ethical compliance
            is_permitted, violations = await self.ethical_ai.evaluate_action(
                "analyze_frequency_resonance", {
                    "audio_shape": audio_data.shape,
                    "sample_rate": sample_rate,
                    "consent": user_consent
                }
            )
            
            if not is_permitted:
                logger.warning("Ethical violations in frequency resonance analysis")
                return await self._create_safe_frequency_analysis()
            
            # Analyze each frequency band
            band_resonances = {}
            
            for band_name, (low_freq, high_freq) in zip(
                ["sub_bass", "bass", "low_mid", "mid", "upper_mid", "presence", "brilliance"],
                self.frequency_bands
            ):
                # Filter audio for frequency band
                filtered_audio = await self._filter_frequency_band(
                    audio_data, sample_rate, low_freq, high_freq
                )
                
                # Analyze resonance in this band
                resonance_analysis = await self._analyze_band_resonance(
                    filtered_audio, sample_rate, low_freq, high_freq
                )
                
                band_resonances[band_name] = resonance_analysis
            
            # Cross-band analysis
            cross_band_patterns = await self._analyze_cross_band_patterns(band_resonances)
            
            # Dominant frequency characteristics
            dominant_freqs = await self._identify_dominant_frequencies(audio_data, sample_rate)
            
            result = {
                "band_resonances": band_resonances,
                "cross_band_patterns": cross_band_patterns,
                "dominant_frequencies": dominant_freqs,
                "analysis_timestamp": datetime.utcnow().isoformat()
            }
            
            return result
            
        except Exception as e:
            logger.error(f"Error in frequency resonance analysis: {e}")
            return await self._create_safe_frequency_analysis()
    
    async def analyze_stem_resonance_interactions(self,
                                                stems: Dict[str, np.ndarray],
                                                sample_rate: int,
                                                user_consent: Dict[str, bool]) -> Dict[str, Any]:
        """
        Analyze how different stems create emotional resonance together
        
        Args:
            stems: Dictionary of stem_name -> audio_data
            sample_rate: Audio sample rate
            user_consent: User consent for processing
        
        Returns:
            Analysis of stem resonance interactions
        """
        try:
            # Validate ethical compliance
            is_permitted, violations = await self.ethical_ai.evaluate_action(
                "analyze_stem_resonance_interactions", {
                    "stem_count": len(stems),
                    "sample_rate": sample_rate,
                    "consent": user_consent
                }
            )
            
            if not is_permitted:
                logger.warning("Ethical violations in stem resonance analysis")
                return await self._create_safe_stem_analysis()
            
            # Individual stem resonance analysis
            stem_resonances = {}
            for stem_name, audio_data in stems.items():
                resonance_timeline = await self.analyze_resonance_timeline(
                    audio_data, sample_rate, user_consent
                )
                stem_resonances[stem_name] = resonance_timeline
            
            # Stem interaction analysis
            interactions = await self._analyze_stem_interactions(stems, stem_resonances)
            
            # Resonance synergy analysis
            synergy_map = await self._analyze_resonance_synergy(stem_resonances)
            
            # Emotional complementarity
            complementarity = await self._analyze_emotional_complementarity(stem_resonances)
            
            result = {
                "stem_resonances": stem_resonances,
                "interactions": interactions,
                "synergy_map": synergy_map,
                "complementarity": complementarity,
                "analysis_timestamp": datetime.utcnow().isoformat()
            }
            
            return result
            
        except Exception as e:
            logger.error(f"Error in stem resonance analysis: {e}")
            return await self._create_safe_stem_analysis()
    
    async def _enhance_resonance_analysis(self, basic_resonances: List[EmotionalResonance],
                                        audio_data: np.ndarray, sample_rate: int) -> List[EmotionalResonance]:
        """Enhance basic resonance analysis with detailed features"""
        enhanced_resonances = []
        
        for resonance in basic_resonances:
            # Extract audio segment around resonance
            start_sample = max(0, int((resonance.timestamp - 0.25) * sample_rate))
            end_sample = min(len(audio_data), int((resonance.timestamp + 0.25) * sample_rate))
            segment = audio_data[start_sample:end_sample]
            
            if len(segment) > 0:
                # Detailed spectral analysis
                spectral_features = await self._analyze_detailed_spectrum(segment, sample_rate)
                
                # Harmonic content analysis
                harmonic_content = await self._analyze_harmonic_resonance(segment, sample_rate)
                
                # Rhythmic signature
                rhythmic_signature = await self._analyze_rhythmic_resonance(segment, sample_rate)
                
                # Create enhanced resonance
                enhanced_resonance = EmotionalResonance(
                    timestamp=resonance.timestamp,
                    frequency_range=resonance.frequency_range,
                    resonance_level=resonance.resonance_level,
                    emotional_quality=resonance.emotional_quality,
                    intensity=resonance.intensity,
                    duration=resonance.duration,
                    harmonic_content=harmonic_content,
                    rhythmic_signature=rhythmic_signature,
                    spectral_features=spectral_features
                )
                
                enhanced_resonances.append(enhanced_resonance)
        
        return enhanced_resonances
    
    async def _detect_resonance_patterns(self, resonances: List[EmotionalResonance],
                                       audio_data: np.ndarray, sample_rate: int) -> List[ResonanceSignature]:
        """Detect signature patterns in resonance events"""
        patterns = []
        
        if len(resonances) < 3:
            return patterns
        
        # Group resonances by temporal proximity
        temporal_groups = await self._group_resonances_temporally(resonances, max_gap=2.0)
        
        for group in temporal_groups:
            if len(group) >= 3:
                # Analyze pattern in this group
                pattern = await self._analyze_pattern_in_group(group, audio_data, sample_rate)
                if pattern:
                    patterns.append(pattern)
        
        return patterns
    
    async def _build_emotional_arc(self, resonances: List[EmotionalResonance],
                                 audio_data: np.ndarray, sample_rate: int) -> List[Tuple[float, float, str]]:
        """Build emotional arc from resonance timeline"""
        arc = []
        
        if not resonances:
            return arc
        
        # Create time windows for arc analysis
        window_size = 5.0  # 5 second windows
        total_duration = len(audio_data) / sample_rate
        
        for window_start in np.arange(0, total_duration, window_size):
            window_end = window_start + window_size
            
            # Find resonances in this window
            window_resonances = [
                r for r in resonances
                if window_start <= r.timestamp < window_end
            ]
            
            if window_resonances:
                # Calculate window emotional characteristics
                avg_intensity = np.mean([r.intensity for r in window_resonances])
                dominant_quality = max(
                    set(r.emotional_quality for r in window_resonances),
                    key=lambda q: sum(1 for r in window_resonances if r.emotional_quality == q)
                )
                
                arc.append((window_start + window_size/2, avg_intensity, dominant_quality))
        
        return arc
    
    async def _filter_frequency_band(self, audio_data: np.ndarray, sample_rate: int,
                                   low_freq: float, high_freq: float) -> np.ndarray:
        """Filter audio data to specific frequency band"""
        # Design bandpass filter
        nyquist = sample_rate / 2
        low_norm = low_freq / nyquist
        high_norm = high_freq / nyquist
        
        b, a = signal.butter(4, [low_norm, high_norm], btype='band')
        
        # Apply filter
        if len(audio_data.shape) == 2:  # Stereo
            filtered = np.array([
                signal.filtfilt(b, a, audio_data[0]),
                signal.filtfilt(b, a, audio_data[1])
            ])
        else:  # Mono
            filtered = signal.filtfilt(b, a, audio_data)
        
        return filtered
    
    async def _analyze_band_resonance(self, audio_data: np.ndarray, sample_rate: int,
                                    low_freq: float, high_freq: float) -> Dict[str, Any]:
        """Analyze resonance within a specific frequency band"""
        # Extract features
        spectral_centroids = librosa.feature.spectral_centroid(
            y=audio_data, sr=sample_rate
        )
        
        spectral_rolloff = librosa.feature.spectral_rolloff(
            y=audio_data, sr=sample_rate
        )
        
        zero_crossing_rate = librosa.feature.zero_crossing_rate(audio_data)
        
        # Calculate resonance metrics
        avg_centroid = np.mean(spectral_centroids) if spectral_centroids.size > 0 else 0
        spectral_spread = np.std(spectral_centroids) if spectral_centroids.size > 0 else 0
        avg_zcr = np.mean(zero_crossing_rate) if zero_crossing_rate.size > 0 else 0
        
        # Resonance score based on spectral characteristics
        resonance_score = min(1.0, (spectral_spread / (avg_centroid + 1e-8)) * 2)
        
        return {
            "frequency_range": (low_freq, high_freq),
            "resonance_score": float(resonance_score),
            "spectral_centroid": float(avg_centroid),
            "spectral_spread": float(spectral_spread),
            "zero_crossing_rate": float(avg_zcr),
            "dominant_emotional_quality": await self._classify_band_emotion(resonance_score, avg_zcr)
        }
    
    async def _analyze_cross_band_patterns(self, band_resonances: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Analyze patterns across frequency bands"""
        patterns = []
        
        # Look for harmonic relationships
        band_names = list(band_resonances.keys())
        
        for i, band1 in enumerate(band_names):
            for band2 in band_names[i+1:]:
                res1 = band_resonances[band1]["resonance_score"]
                res2 = band_resonances[band2]["resonance_score"]
                
                # Check for correlated resonance
                if abs(res1 - res2) < 0.2:
                    patterns.append({
                        "type": "correlated_resonance",
                        "bands": [band1, band2],
                        "strength": min(res1, res2)
                    })
        
        return patterns
    
    async def _identify_dominant_frequencies(self, audio_data: np.ndarray, sample_rate: int) -> List[float]:
        """Identify dominant frequencies in audio"""
        # Compute FFT
        fft = np.fft.fft(audio_data)
        freqs = np.fft.fftfreq(len(audio_data), 1/sample_rate)
        
        # Find peaks in magnitude spectrum
        magnitude = np.abs(fft)
        
        # Only consider positive frequencies
        pos_freqs = freqs[:len(freqs)//2]
        pos_magnitude = magnitude[:len(magnitude)//2]
        
        # Find peaks
        peaks, _ = signal.find_peaks(pos_magnitude, height=np.max(pos_magnitude) * 0.1)
        
        # Return top 5 dominant frequencies
        if len(peaks) > 0:
            top_peaks = sorted(peaks, key=lambda p: pos_magnitude[p], reverse=True)[:5]
            return [float(pos_freqs[p]) for p in top_peaks]
        
        return []
    
    async def _analyze_stem_interactions(self, stems: Dict[str, np.ndarray],
                                       stem_resonances: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze interactions between different stems"""
        interactions = {
            "temporal_alignment": {},
            "frequency_complementarity": {},
            "emotional_synthesis": {}
        }
        
        stem_names = list(stems.keys())
        
        # Temporal alignment analysis
        for i, stem1 in enumerate(stem_names):
            for stem2 in stem_names[i+1:]:
                # Calculate temporal correlation
                correlation = np.corrcoef(
                    stems[stem1].flatten(),
                    stems[stem2].flatten()
                )[0, 1]
                
                interactions["temporal_alignment"][f"{stem1}_{stem2}"] = float(abs(correlation))
        
        return interactions
    
    async def _analyze_resonance_synergy(self, stem_resonances: Dict[str, Any]) -> Dict[str, float]:
        """Analyze how stem resonances work together"""
        synergy_scores = {}
        
        # Calculate overall resonance synergy
        all_intensities = []
        for stem_name, timeline in stem_resonances.items():
            for event in timeline.resonance_events:
                all_intensities.append(event.intensity)
        
        if all_intensities:
            synergy_scores["overall_synergy"] = float(np.mean(all_intensities))
        else:
            synergy_scores["overall_synergy"] = 0.0
        
        return synergy_scores
    
    async def _analyze_emotional_complementarity(self, stem_resonances: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze how stem emotions complement each other"""
        complementarity = {
            "emotional_balance": 0.0,
            "dominant_emotions": {},
            "emotional_harmony": 0.0
        }
        
        # Collect emotional qualities from all stems
        all_qualities = []
        for stem_name, timeline in stem_resonances.items():
            for event in timeline.resonance_events:
                all_qualities.append(event.emotional_quality)
        
        if all_qualities:
            # Calculate emotional balance
            quality_counts = {}
            for quality in all_qualities:
                quality_counts[quality] = quality_counts.get(quality, 0) + 1
            
            # Balance is higher when emotions are distributed
            balance = 1.0 - (max(quality_counts.values()) / len(all_qualities))
            complementarity["emotional_balance"] = float(balance)
            complementarity["dominant_emotions"] = quality_counts
        
        return complementarity
    
    async def _create_safe_resonance_timeline(self, audio_data: np.ndarray, sample_rate: int) -> ResonanceTimeline:
        """Create safe resonance timeline when analysis fails"""
        return ResonanceTimeline(
            total_duration=len(audio_data) / sample_rate,
            resonance_events=[],
            signature_patterns=[],
            emotional_arc=[(0.0, 0.5, "neutral")]
        )
    
    async def _create_safe_frequency_analysis(self) -> Dict[str, Any]:
        """Create safe frequency analysis when analysis fails"""
        return {
            "band_resonances": {},
            "cross_band_patterns": [],
            "dominant_frequencies": [],
            "analysis_timestamp": datetime.utcnow().isoformat()
        }
    
    async def _create_safe_stem_analysis(self) -> Dict[str, Any]:
        """Create safe stem analysis when analysis fails"""
        return {
            "stem_resonances": {},
            "interactions": {},
            "synergy_map": {},
            "complementarity": {},
            "analysis_timestamp": datetime.utcnow().isoformat()
        }
    
    async def _classify_band_emotion(self, resonance_score: float, zcr: float) -> str:
        """Classify emotional quality of frequency band"""
        if resonance_score > 0.7 and zcr > 0.05:
            return "energetic_excitement"
        elif resonance_score > 0.5 and zcr < 0.03:
            return "peaceful_resonance"
        elif resonance_score < 0.3:
            return "subtle_presence"
        else:
            return "balanced_expression"