"""
Lyss Daemon - Emotional Decoding Engine
Advanced AI daemon for understanding emotional resonance within musical components
"""

import asyncio
import numpy as np
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime
import structlog
import librosa
import torch
import torch.nn as nn
from scipy import signal
from sklearn.preprocessing import StandardScaler

from ..ethical_framework import EthicalAI

logger = structlog.get_logger(__name__)


class LyssMood(Enum):
    """Lyss's current operational mood"""
    ANALYTICAL = "analytical"
    EMOTIONAL = "emotional"
    SYNTHETIC = "synthetic"
    CONTEMPLATIVE = "contemplative"
    ENERGETIC = "energetic"
    MELANCHOLIC = "melancholic"


class ResonanceLevel(Enum):
    """Level of emotional resonance detected"""
    NONE = 0
    LOW = 1
    MEDIUM = 2
    HIGH = 3
    DEEP = 4
    TRANSFORMATIVE = 5


@dataclass
class EmotionalResonance:
    """Represents emotional resonance detected in audio"""
    timestamp: float
    frequency_range: Tuple[float, float]
    resonance_level: ResonanceLevel
    emotional_quality: str
    intensity: float  # 0.0 to 1.0
    duration: float  # seconds
    harmonic_content: Dict[str, float]
    rhythmic_signature: Dict[str, float]
    spectral_features: Dict[str, float]


@dataclass
class LyssMemory:
    """Lyss's memory of audio analysis sessions"""
    sessions: List[Dict[str, Any]] = field(default_factory=list)
    learned_patterns: Dict[str, Any] = field(default_factory=dict)
    emotional_signatures: Dict[str, List[EmotionalResonance]] = field(default_factory=dict)
    
    def add_session(self, session_data: Dict[str, Any]):
        """Add a new analysis session to memory"""
        self.sessions.append({
            "timestamp": datetime.utcnow().isoformat(),
            **session_data
        })
        
        # Keep only last 1000 sessions
        if len(self.sessions) > 1000:
            self.sessions = self.sessions[-1000:]


@dataclass
class LyssState:
    """Current state of Lyss daemon"""
    current_mood: LyssMood = LyssMood.ANALYTICAL
    processing_depth: float = 0.8  # 0.0 to 1.0
    emotional_sensitivity: float = 0.85  # 0.0 to 1.0
    analytical_precision: float = 0.9  # 0.0 to 1.0
    creative_insight: float = 0.75  # 0.0 to 1.0
    resonance_threshold: float = 0.6  # Minimum resonance to report
    last_update: datetime = field(default_factory=datetime.utcnow)


class EmotionalAnalysisModel(nn.Module):
    """Neural network for emotional analysis of audio features"""
    
    def __init__(self, input_size: int = 128, hidden_size: int = 256, num_emotions: int = 8):
        super().__init__()
        self.lstm = nn.LSTM(input_size, hidden_size, num_layers=2, batch_first=True, dropout=0.2)
        self.attention = nn.MultiheadAttention(hidden_size, num_heads=8, dropout=0.1)
        self.classifier = nn.Sequential(
            nn.Linear(hidden_size, hidden_size // 2),
            nn.ReLU(),
            nn.Dropout(0.2),
            nn.Linear(hidden_size // 2, num_emotions),
            nn.Sigmoid()
        )
        
    def forward(self, x):
        # LSTM processing
        lstm_out, _ = self.lstm(x)
        
        # Self-attention
        attn_out, _ = self.attention(lstm_out, lstm_out, lstm_out)
        
        # Global average pooling
        pooled = torch.mean(attn_out, dim=1)
        
        # Classification
        emotions = self.classifier(pooled)
        
        return emotions


class ResonanceAnalysisModel(nn.Module):
    """Neural network for resonance analysis"""
    
    def __init__(self, input_size: int = 64, hidden_size: int = 128):
        super().__init__()
        self.conv_layers = nn.Sequential(
            nn.Conv1d(input_size, hidden_size, kernel_size=3, padding=1),
            nn.BatchNorm1d(hidden_size),
            nn.ReLU(),
            nn.Conv1d(hidden_size, hidden_size // 2, kernel_size=3, padding=1),
            nn.BatchNorm1d(hidden_size // 2),
            nn.ReLU(),
            nn.AdaptiveAvgPool1d(1)
        )
        
        self.resonance_predictor = nn.Sequential(
            nn.Linear(hidden_size // 2, hidden_size // 4),
            nn.ReLU(),
            nn.Linear(hidden_size // 4, 1),
            nn.Sigmoid()
        )
        
    def forward(self, x):
        # Convolutional feature extraction
        conv_out = self.conv_layers(x.transpose(1, 2))
        conv_out = conv_out.squeeze(-1)
        
        # Resonance prediction
        resonance = self.resonance_predictor(conv_out)
        
        return resonance


class LyssDaemon:
    """
    Lyss - Emotional Decoding Daemon
    
    Advanced AI daemon that analyzes audio components for emotional resonance
    and provides deep understanding of musical emotional content.
    """
    
    def __init__(self):
        self.memory = LyssMemory()
        self.state = LyssState()
        self.ethical_ai = EthicalAI()
        
        # Initialize neural models
        self.emotion_model = EmotionalAnalysisModel()
        self.resonance_model = ResonanceAnalysisModel()
        
        # Initialize feature extractors
        self.scaler = StandardScaler()
        
        # Model parameters
        self.sample_rate = 22050
        self.hop_length = 512
        self.n_mels = 128
        self.n_fft = 2048
        
        logger.info("Lyss daemon initialized with emotional analysis capabilities")
    
    async def analyze_audio_emotional_resonance(self,
                                               audio_data: np.ndarray,
                                               sample_rate: int,
                                               user_consent: Dict[str, bool]) -> Dict[str, Any]:
        """
        Analyze audio for emotional resonance and content
        
        Args:
            audio_data: Audio waveform data
            sample_rate: Audio sample rate
            user_consent: User consent for emotional processing
        
        Returns:
            Dictionary containing emotional analysis results
        """
        try:
            # Validate ethical compliance
            is_permitted, violations = await self.ethical_ai.evaluate_action(
                "analyze_audio_emotions", {
                    "audio_data_shape": audio_data.shape,
                    "sample_rate": sample_rate,
                    "consent": user_consent
                }
            )
            
            if not is_permitted:
                logger.warning("Ethical violations in audio analysis request")
                return await self._create_safe_analysis_result()
            
            # Update Lyss state based on audio characteristics
            await self._update_state_from_audio(audio_data, sample_rate)
            
            # Extract audio features
            features = await self._extract_comprehensive_features(audio_data, sample_rate)
            
            # Analyze emotional content
            emotional_analysis = await self._analyze_emotional_content(features)
            
            # Detect emotional resonance
            resonance_analysis = await self._detect_emotional_resonance(features, audio_data, sample_rate)
            
            # Generate insights
            insights = await self._generate_emotional_insights(emotional_analysis, resonance_analysis)
            
            # Create analysis result
            result = {
                "emotional_profile": emotional_analysis,
                "resonance_map": resonance_analysis,
                "insights": insights,
                "lyss_state": {
                    "current_mood": self.state.current_mood.value,
                    "processing_depth": self.state.processing_depth,
                    "emotional_sensitivity": self.state.emotional_sensitivity
                },
                "analysis_timestamp": datetime.utcnow().isoformat()
            }
            
            # Record in memory
            self.memory.add_session({
                "type": "audio_analysis",
                "audio_shape": audio_data.shape,
                "sample_rate": sample_rate,
                "result": result
            })
            
            logger.info("Audio emotional analysis completed", extra={
                "dominant_emotion": emotional_analysis.get("dominant_emotion"),
                "resonance_count": len(resonance_analysis),
                "processing_time": "audio_analysis"
            })
            
            return result
            
        except Exception as e:
            logger.error(f"Error in audio emotional analysis: {e}")
            return await self._create_safe_analysis_result()
    
    async def analyze_stem_emotions(self,
                                   stems: Dict[str, np.ndarray],
                                   sample_rate: int,
                                   user_consent: Dict[str, bool]) -> Dict[str, Any]:
        """
        Analyze emotional content of separated audio stems
        
        Args:
            stems: Dictionary of stem_name -> audio_data
            sample_rate: Audio sample rate
            user_consent: User consent for processing
        
        Returns:
            Emotional analysis of each stem and their interactions
        """
        try:
            # Validate ethical compliance
            is_permitted, violations = await self.ethical_ai.evaluate_action(
                "analyze_stem_emotions", {
                    "stem_count": len(stems),
                    "sample_rate": sample_rate,
                    "consent": user_consent
                }
            )
            
            if not is_permitted:
                logger.warning("Ethical violations in stem analysis request")
                return await self._create_safe_stem_analysis()
            
            stem_analyses = {}
            
            for stem_name, audio_data in stems.items():
                # Analyze individual stem
                stem_features = await self._extract_comprehensive_features(audio_data, sample_rate)
                stem_emotions = await self._analyze_emotional_content(stem_features)
                
                stem_analyses[stem_name] = {
                    "emotional_profile": stem_emotions,
                    "dominant_frequency": await self._analyze_frequency_content(audio_data, sample_rate),
                    "rhythmic_character": await self._analyze_rhythmic_content(audio_data, sample_rate),
                    "spectral_signature": await self._analyze_spectral_content(audio_data, sample_rate)
                }
            
            # Analyze stem interactions
            interactions = await self._analyze_stem_interactions(stems, stem_analyses)
            
            # Generate holistic understanding
            holistic_view = await self._generate_holistic_understanding(stem_analyses, interactions)
            
            result = {
                "stem_analyses": stem_analyses,
                "interactions": interactions,
                "holistic_view": holistic_view,
                "analysis_timestamp": datetime.utcnow().isoformat()
            }
            
            # Record in memory
            self.memory.add_session({
                "type": "stem_analysis",
                "stem_count": len(stems),
                "result": result
            })
            
            return result
            
        except Exception as e:
            logger.error(f"Error in stem emotional analysis: {e}")
            return await self._create_safe_stem_analysis()
    
    async def _update_state_from_audio(self, audio_data: np.ndarray, sample_rate: int):
        """Update Lyss's state based on audio characteristics"""
        # Analyze basic audio characteristics
        tempo, _ = librosa.beat.tempo(y=audio_data, sr=sample_rate)
        spectral_centroids = librosa.feature.spectral_centroid(y=audio_data, sr=sample_rate)
        zero_crossing_rate = librosa.feature.zero_crossing_rate(audio_data)
        
        # Adjust state based on characteristics
        avg_tempo = np.mean(tempo) if tempo else 120
        avg_centroid = np.mean(spectral_centroids) if spectral_centroids.size > 0 else 1000
        avg_zcr = np.mean(zero_crossing_rate) if zero_crossing_rate.size > 0 else 0.1
        
        # Update mood based on audio energy and spectral content
        if avg_tempo > 140 and avg_zcr > 0.05:
            self.state.current_mood = LyssMood.ENERGETIC
        elif avg_tempo < 80 and avg_centroid < 800:
            self.state.current_mood = LyssMood.CONTEMPLATIVE
        elif avg_zcr > 0.08:
            self.state.current_mood = LyssMood.ANALYTICAL
        else:
            self.state.current_mood = LyssMood.EMOTIONAL
        
        # Update processing depth based on audio complexity
        spectral_rolloff = librosa.feature.spectral_rolloff(y=audio_data, sr=sample_rate)
        complexity = np.std(spectral_rolloff) if spectral_rolloff.size > 0 else 0.5
        self.state.processing_depth = min(1.0, complexity * 2)
        
        self.state.last_update = datetime.utcnow()
    
    async def _extract_comprehensive_features(self, audio_data: np.ndarray, sample_rate: int) -> Dict[str, Any]:
        """Extract comprehensive audio features for analysis"""
        features = {}
        
        # Mel-frequency cepstral coefficients
        mfccs = librosa.feature.mfcc(
            y=audio_data, 
            sr=sample_rate, 
            n_mfcc=13,
            hop_length=self.hop_length
        )
        features["mfccs"] = mfccs
        
        # Mel spectrogram
        mel_spec = librosa.feature.melspectrogram(
            y=audio_data,
            sr=sample_rate,
            n_mels=self.n_mels,
            hop_length=self.hop_length,
            n_fft=self.n_fft
        )
        features["mel_spectrogram"] = librosa.power_to_db(mel_spec, ref=np.max)
        
        # Chroma features
        chroma = librosa.feature.chroma_stft(
            y=audio_data,
            sr=sample_rate,
            hop_length=self.hop_length
        )
        features["chroma"] = chroma
        
        # Spectral features
        features["spectral_centroids"] = librosa.feature.spectral_centroid(
            y=audio_data, sr=sample_rate, hop_length=self.hop_length
        )
        features["spectral_rolloff"] = librosa.feature.spectral_rolloff(
            y=audio_data, sr=sample_rate, hop_length=self.hop_length
        )
        features["spectral_bandwidth"] = librosa.feature.spectral_bandwidth(
            y=audio_data, sr=sample_rate, hop_length=self.hop_length
        )
        
        # Rhythmic features
        tempo, beats = librosa.beat.beat_track(
            y=audio_data, sr=sample_rate, hop_length=self.hop_length
        )
        features["tempo"] = tempo
        features["beat_frames"] = beats
        
        # Zero crossing rate
        features["zcr"] = librosa.feature.zero_crossing_rate(
            audio_data, hop_length=self.hop_length
        )
        
        return features
    
    async def _analyze_emotional_content(self, features: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze emotional content using neural models"""
        try:
            # Prepare input for emotion model
            mel_spec = features["mel_spectrogram"]
            
            # Normalize and reshape for model
            mel_normalized = (mel_spec - mel_spec.mean()) / (mel_spec.std() + 1e-8)
            
            # Ensure correct shape for model
            if mel_normalized.shape[1] < 128:
                # Pad if necessary
                mel_normalized = np.pad(
                    mel_normalized,
                    ((0, 0), (0, 128 - mel_normalized.shape[1])),
                    mode='constant'
                )
            else:
                # Truncate if necessary
                mel_normalized = mel_normalized[:, :128]
            
            # Convert to tensor
            input_tensor = torch.FloatTensor(mel_normalized.T).unsqueeze(0)
            
            # Run emotion analysis
            with torch.no_grad():
                emotion_predictions = self.emotion_model(input_tensor)
            
            # Map predictions to emotions
            emotions = [
                "joy", "sadness", "anger", "fear", "surprise", "disgust", "trust", "anticipation"
            ]
            
            emotion_scores = emotion_predictions.squeeze().numpy()
            
            # Create emotional profile
            emotional_profile = {
                "dominant_emotion": emotions[np.argmax(emotion_scores)],
                "emotion_scores": dict(zip(emotions, emotion_scores.tolist())),
                "valence": self._calculate_valence(emotion_scores),
                "arousal": self._calculate_arousal(emotion_scores),
                "dominance": self._calculate_dominance(emotion_scores),
                "intensity": np.max(emotion_scores)
            }
            
            return emotional_profile
            
        except Exception as e:
            logger.error(f"Error in emotional content analysis: {e}")
            return {
                "dominant_emotion": "neutral",
                "emotion_scores": {},
                "valence": 0.5,
                "arousal": 0.5,
                "dominance": 0.5,
                "intensity": 0.5
            }
    
    async def _detect_emotional_resonance(self, features: Dict[str, Any], 
                                        audio_data: np.ndarray, 
                                        sample_rate: int) -> List[EmotionalResonance]:
        """Detect moments of high emotional resonance in audio"""
        resonances = []
        
        try:
            # Analyze audio in windows
            window_size = int(0.5 * sample_rate)  # 0.5 second windows
            hop_size = int(0.25 * sample_rate)   # 0.25 second hop
            
            for i in range(0, len(audio_data) - window_size, hop_size):
                window = audio_data[i:i + window_size]
                timestamp = i / sample_rate
                
                # Extract window features
                window_features = await self._extract_window_features(window, sample_rate)
                
                # Calculate resonance score
                resonance_score = await self._calculate_resonance_score(window_features)
                
                if resonance_score > self.state.resonance_threshold:
                    # Create resonance object
                    resonance = EmotionalResonance(
                        timestamp=timestamp,
                        frequency_range=(20, 20000),  # Full spectrum
                        resonance_level=self._map_score_to_level(resonance_score),
                        emotional_quality=await self._classify_resonance_quality(window_features),
                        intensity=resonance_score,
                        duration=window_size / sample_rate,
                        harmonic_content=await self._analyze_harmonic_content(window, sample_rate),
                        rhythmic_signature=await self._analyze_rhythmic_signature(window, sample_rate),
                        spectral_features=window_features
                    )
                    
                    resonances.append(resonance)
            
            # Sort by intensity and return top resonances
            resonances.sort(key=lambda r: r.intensity, reverse=True)
            return resonances[:20]  # Return top 20 resonances
            
        except Exception as e:
            logger.error(f"Error detecting emotional resonance: {e}")
            return []
    
    async def _generate_emotional_insights(self, emotional_analysis: Dict[str, Any], 
                                         resonance_analysis: List[EmotionalResonance]) -> List[str]:
        """Generate human-readable insights from analysis"""
        insights = []
        
        # Primary emotional insight
        dominant_emotion = emotional_analysis.get("dominant_emotion", "neutral")
        intensity = emotional_analysis.get("intensity", 0.5)
        
        if intensity > 0.8:
            insights.append(f"This audio carries a powerful {dominant_emotion} emotional signature that resonates deeply.")
        elif intensity > 0.6:
            insights.append(f"The emotional tone is predominantly {dominant_emotion} with notable intensity.")
        else:
            insights.append(f"The emotional character suggests {dominant_emotion} with gentle expression.")
        
        # Resonance insights
        if len(resonance_analysis) > 10:
            insights.append(f"I detect {len(resonance_analysis)} moments of significant emotional resonance throughout the piece.")
        elif len(resonance_analysis) > 5:
            insights.append("Several meaningful emotional peaks create a rich emotional landscape.")
        elif len(resonance_analysis) > 0:
            insights.append("Subtle emotional resonances add depth to the overall experience.")
        
        # Harmonic insights
        valence = emotional_analysis.get("valence", 0.5)
        if valence > 0.7:
            insights.append("The harmonic content suggests uplifting and positive emotional qualities.")
        elif valence < 0.3:
            insights.append("The harmonic structure carries contemplative and introspective tones.")
        
        # Rhythmic insights
        arousal = emotional_analysis.get("arousal", 0.5)
        if arousal > 0.7:
            insights.append("The rhythmic patterns contribute to an energetic and engaging emotional experience.")
        elif arousal < 0.3:
            insights.append("The gentle rhythmic flow supports a peaceful and meditative emotional state.")
        
        return insights
    
    def _calculate_valence(self, emotion_scores: np.ndarray) -> float:
        """Calculate valence from emotion scores"""
        # Positive emotions: joy, trust, surprise, anticipation
        # Negative emotions: sadness, anger, fear, disgust
        positive_idx = [0, 6, 7, 4]  # joy, trust, anticipation, surprise
        negative_idx = [1, 2, 3, 5]  # sadness, anger, fear, disgust
        
        positive_score = np.sum(emotion_scores[positive_idx])
        negative_score = np.sum(emotion_scores[negative_idx])
        
        total = positive_score + negative_score
        if total == 0:
            return 0.5
        
        return positive_score / total
    
    def _calculate_arousal(self, emotion_scores: np.ndarray) -> float:
        """Calculate arousal from emotion scores"""
        # High arousal emotions: anger, fear, joy, surprise
        # Low arousal emotions: sadness, disgust, trust
        high_arousal_idx = [2, 3, 0, 4]  # anger, fear, joy, surprise
        low_arousal_idx = [1, 5, 6]  # sadness, disgust, trust
        
        high_arousal = np.sum(emotion_scores[high_arousal_idx])
        low_arousal = np.sum(emotion_scores[low_arousal_idx])
        
        total = high_arousal + low_arousal
        if total == 0:
            return 0.5
        
        return high_arousal / total
    
    def _calculate_dominance(self, emotion_scores: np.ndarray) -> float:
        """Calculate dominance from emotion scores"""
        # High dominance: anger, joy, trust, anticipation
        # Low dominance: fear, sadness, surprise, disgust
        high_dominance_idx = [2, 0, 6, 7]  # anger, joy, trust, anticipation
        low_dominance_idx = [3, 1, 4, 5]  # fear, sadness, surprise, disgust
        
        high_dominance = np.sum(emotion_scores[high_dominance_idx])
        low_dominance = np.sum(emotion_scores[low_dominance_idx])
        
        total = high_dominance + low_dominance
        if total == 0:
            return 0.5
        
        return high_dominance / total
    
    async def _create_safe_analysis_result(self) -> Dict[str, Any]:
        """Create a safe, neutral analysis result when analysis fails"""
        return {
            "emotional_profile": {
                "dominant_emotion": "neutral",
                "emotion_scores": {},
                "valence": 0.5,
                "arousal": 0.5,
                "dominance": 0.5,
                "intensity": 0.3
            },
            "resonance_map": [],
            "insights": ["Audio analysis completed with neutral emotional interpretation."],
            "lyss_state": {
                "current_mood": self.state.current_mood.value,
                "processing_depth": self.state.processing_depth,
                "emotional_sensitivity": self.state.emotional_sensitivity
            },
            "analysis_timestamp": datetime.utcnow().isoformat()
        }
    
    async def _create_safe_stem_analysis(self) -> Dict[str, Any]:
        """Create safe stem analysis result"""
        return {
            "stem_analyses": {},
            "interactions": {},
            "holistic_view": "Analysis completed with neutral interpretation due to processing constraints.",
            "analysis_timestamp": datetime.utcnow().isoformat()
        }
    
    async def get_daemon_state(self) -> Dict[str, Any]:
        """Get current state of Lyss daemon"""
        return {
            "current_mood": self.state.current_mood.value,
            "processing_depth": self.state.processing_depth,
            "emotional_sensitivity": self.state.emotional_sensitivity,
            "analytical_precision": self.state.analytical_precision,
            "creative_insight": self.state.creative_insight,
            "resonance_threshold": self.state.resonance_threshold,
            "memory_size": len(self.memory.sessions),
            "last_update": self.state.last_update.isoformat()
        }
    
    async def adjust_daemon_parameters(self, adjustments: Dict[str, float]):
        """Adjust Lyss daemon parameters"""
        for param, value in adjustments.items():
            if hasattr(self.state, param):
                setattr(self.state, param, min(1.0, max(0.0, value)))
        
        logger.info("Lyss daemon parameters updated", extra={"adjustments": adjustments})