"""
Spleeter Runner - Audio Source Separation Engine
GPU-accelerated audio separation using Spleeter with emotional context
"""

import asyncio
import os
import tempfile
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
from enum import Enum
import structlog
import numpy as np
import soundfile as sf
from spleeter.separator import Separator
from spleeter.audio import Codec

from ..lyss.daemon import LyssDaemon
from ..ethical_framework import EthicalAI

logger = structlog.get_logger(__name__)


class SeparationModel(Enum):
    """Available Spleeter separation models"""
    TWO_STEM = "2stems"  # vocals, accompaniment
    FOUR_STEM = "4stems"  # vocals, drums, bass, other
    FIVE_STEM = "5stems"  # vocals, drums, bass, piano, other


@dataclass
class SeparationResult:
    """Result of audio separation process"""
    stems: Dict[str, np.ndarray]
    sample_rate: int
    model_used: str
    processing_time: float
    audio_quality_metrics: Dict[str, float]
    emotional_analysis: Optional[Dict[str, Any]] = None


class SpleeterRunner:
    """
    Spleeter Audio Separation Engine with Emotional Context
    
    Provides GPU-accelerated audio source separation with
    emotional analysis integration through Lyss daemon.
    """
    
    def __init__(self):
        self.separators = {}
        self.lyss_daemon = LyssDaemon()
        self.ethical_ai = EthicalAI()
        
        # Initialize separators for different models
        self._initialize_separators()
        
        logger.info("SpleeterRunner initialized with GPU acceleration")
    
    def _initialize_separators(self):
        """Initialize Spleeter separators for different models"""
        try:
            # Initialize 2-stem separator
            self.separators[SeparationModel.TWO_STEM] = Separator(
                "spleeter:2stems",
                multiprocess=False
            )
            
            # Initialize 4-stem separator
            self.separators[SeparationModel.FOUR_STEM] = Separator(
                "spleeter:4stems",
                multiprocess=False
            )
            
            # Initialize 5-stem separator
            self.separators[SeparationModel.FIVE_STEM] = Separator(
                "spleeter:5stems",
                multiprocess=False
            )
            
            logger.info("Spleeter separators initialized successfully")
            
        except Exception as e:
            logger.error(f"Error initializing Spleeter separators: {e}")
            raise
    
    async def separate_audio(self,
                           audio_file_path: str,
                           model: SeparationModel = SeparationModel.FOUR_STEM,
                           output_format: str = "wav",
                           user_consent: Optional[Dict[str, bool]] = None) -> SeparationResult:
        """
        Separate audio file into stems using specified model
        
        Args:
            audio_file_path: Path to audio file
            model: Separation model to use
            output_format: Output audio format
            user_consent: User consent for processing
        
        Returns:
            SeparationResult with separated stems and analysis
        """
        try:
            import time
            start_time = time.time()
            
            # Validate ethical compliance
            is_permitted, violations = await self.ethical_ai.evaluate_action(
                "separate_audio", {
                    "audio_file": audio_file_path,
                    "model": model.value,
                    "consent": user_consent
                }
            )
            
            if not is_permitted:
                logger.warning("Ethical violations in audio separation request")
                raise ValueError("Audio separation not permitted due to ethical constraints")
            
            # Load audio file
            audio_data, sample_rate = await self._load_audio_file(audio_file_path)
            
            logger.info(f"Loaded audio: {audio_data.shape}, sample_rate: {sample_rate}")
            
            # Perform separation
            separator = self.separators.get(model)
            if not separator:
                raise ValueError(f"Separator model {model.value} not available")
            
            # Separate audio
            with tempfile.TemporaryDirectory() as temp_dir:
                # Create temporary output directory
                output_dir = os.path.join(temp_dir, "separated")
                os.makedirs(output_dir, exist_ok=True)
                
                # Create temporary input file if needed
                if not audio_file_path.endswith('.wav'):
                    temp_input = os.path.join(temp_dir, "input.wav")
                    sf.write(temp_input, audio_data, sample_rate)
                    input_path = temp_input
                else:
                    input_path = audio_file_path
                
                # Perform separation
                separator.separate_to_file(
                    input_path,
                    output_dir,
                    codec=Codec.WAV if output_format == "wav" else Codec.MP3
                )
                
                # Load separated stems
                stems = await self._load_separated_stems(output_dir, model)
            
            # Calculate processing time
            processing_time = time.time() - start_time
            
            # Calculate audio quality metrics
            quality_metrics = await self._calculate_quality_metrics(audio_data, stems, sample_rate)
            
            # Perform emotional analysis if consent given
            emotional_analysis = None
            if user_consent and user_consent.get("emotional_processing", False):
                emotional_analysis = await self.lyss_daemon.analyze_stem_emotions(
                    stems, sample_rate, user_consent
                )
            
            # Create result
            result = SeparationResult(
                stems=stems,
                sample_rate=sample_rate,
                model_used=model.value,
                processing_time=processing_time,
                audio_quality_metrics=quality_metrics,
                emotional_analysis=emotional_analysis
            )
            
            logger.info(f"Audio separation completed", extra={
                "model": model.value,
                "stems": len(stems),
                "processing_time": processing_time,
                "quality_score": quality_metrics.get("overall_quality", 0.0)
            })
            
            return result
            
        except Exception as e:
            logger.error(f"Error in audio separation: {e}")
            raise
    
    async def separate_audio_data(self,
                                audio_data: np.ndarray,
                                sample_rate: int,
                                model: SeparationModel = SeparationModel.FOUR_STEM,
                                user_consent: Optional[Dict[str, bool]] = None) -> SeparationResult:
        """
        Separate audio data directly without file I/O
        
        Args:
            audio_data: Audio waveform data
            sample_rate: Audio sample rate
            model: Separation model to use
            user_consent: User consent for processing
        
        Returns:
            SeparationResult with separated stems
        """
        try:
            import time
            start_time = time.time()
            
            # Validate ethical compliance
            is_permitted, violations = await self.ethical_ai.evaluate_action(
                "separate_audio_data", {
                    "audio_shape": audio_data.shape,
                    "sample_rate": sample_rate,
                    "model": model.value,
                    "consent": user_consent
                }
            )
            
            if not is_permitted:
                logger.warning("Ethical violations in audio data separation request")
                raise ValueError("Audio separation not permitted due to ethical constraints")
            
            # Ensure audio is in correct format (mono to stereo if needed)
            if len(audio_data.shape) == 1:
                audio_data = np.stack([audio_data, audio_data])
            
            # Perform separation
            separator = self.separators.get(model)
            if not separator:
                raise ValueError(f"Separator model {model.value} not available")
            
            # Separate using separator
            separated = separator.separate(audio_data.T)
            
            # Convert to stems dictionary
            stems = {}
            if model == SeparationModel.TWO_STEM:
                stems = {
                    "vocals": separated[:, :, 0].T,
                    "accompaniment": separated[:, :, 1].T
                }
            elif model == SeparationModel.FOUR_STEM:
                stems = {
                    "vocals": separated[:, :, 0].T,
                    "drums": separated[:, :, 1].T,
                    "bass": separated[:, :, 2].T,
                    "other": separated[:, :, 3].T
                }
            elif model == SeparationModel.FIVE_STEM:
                stems = {
                    "vocals": separated[:, :, 0].T,
                    "drums": separated[:, :, 1].T,
                    "bass": separated[:, :, 2].T,
                    "piano": separated[:, :, 3].T,
                    "other": separated[:, :, 4].T
                }
            
            # Calculate processing time
            processing_time = time.time() - start_time
            
            # Calculate quality metrics
            quality_metrics = await self._calculate_quality_metrics(audio_data.T, stems, sample_rate)
            
            # Perform emotional analysis if consent given
            emotional_analysis = None
            if user_consent and user_consent.get("emotional_processing", False):
                emotional_analysis = await self.lyss_daemon.analyze_stem_emotions(
                    stems, sample_rate, user_consent
                )
            
            # Create result
            result = SeparationResult(
                stems=stems,
                sample_rate=sample_rate,
                model_used=model.value,
                processing_time=processing_time,
                audio_quality_metrics=quality_metrics,
                emotional_analysis=emotional_analysis
            )
            
            logger.info(f"Audio data separation completed", extra={
                "model": model.value,
                "stems": len(stems),
                "processing_time": processing_time,
                "quality_score": quality_metrics.get("overall_quality", 0.0)
            })
            
            return result
            
        except Exception as e:
            logger.error(f"Error in audio data separation: {e}")
            raise
    
    async def batch_separate(self,
                           audio_files: List[str],
                           model: SeparationModel = SeparationModel.FOUR_STEM,
                           max_concurrent: int = 3,
                           user_consent: Optional[Dict[str, bool]] = None) -> List[SeparationResult]:
        """
        Separate multiple audio files in batch
        
        Args:
            audio_files: List of audio file paths
            model: Separation model to use
            max_concurrent: Maximum concurrent separations
            user_consent: User consent for processing
        
        Returns:
            List of SeparationResult objects
        """
        results = []
        
        # Process files in batches
        for i in range(0, len(audio_files), max_concurrent):
            batch = audio_files[i:i + max_concurrent]
            
            # Process batch concurrently
            batch_tasks = [
                self.separate_audio(audio_file, model, "wav", user_consent)
                for audio_file in batch
            ]
            
            batch_results = await asyncio.gather(*batch_tasks, return_exceptions=True)
            
            # Handle results and exceptions
            for result in batch_results:
                if isinstance(result, Exception):
                    logger.error(f"Batch separation error: {result}")
                    # Create error result
                    error_result = SeparationResult(
                        stems={},
                        sample_rate=44100,
                        model_used=model.value,
                        processing_time=0.0,
                        audio_quality_metrics={"error": True},
                        emotional_analysis=None
                    )
                    results.append(error_result)
                else:
                    results.append(result)
        
        return results
    
    async def _load_audio_file(self, file_path: str) -> Tuple[np.ndarray, int]:
        """Load audio file and return data and sample rate"""
        try:
            audio_data, sample_rate = librosa.load(file_path, sr=None, mono=False)
            
            # Ensure stereo format
            if len(audio_data.shape) == 1:
                audio_data = np.stack([audio_data, audio_data])
            
            return audio_data, sample_rate
            
        except Exception as e:
            logger.error(f"Error loading audio file {file_path}: {e}")
            raise
    
    async def _load_separated_stems(self, output_dir: str, model: SeparationModel) -> Dict[str, np.ndarray]:
        """Load separated stems from output directory"""
        stems = {}
        
        # Find the separated directory
        separated_dirs = [d for d in os.listdir(output_dir) if os.path.isdir(os.path.join(output_dir, d))]
        if not separated_dirs:
            raise ValueError("No separated audio directory found")
        
        separated_dir = os.path.join(output_dir, separated_dirs[0])
        
        # Load stem files
        stem_files = {
            "vocals": "vocals.wav",
            "accompaniment": "accompaniment.wav",
            "drums": "drums.wav",
            "bass": "bass.wav",
            "piano": "piano.wav",
            "other": "other.wav"
        }
        
        for stem_name, filename in stem_files.items():
            file_path = os.path.join(separated_dir, filename)
            if os.path.exists(file_path):
                try:
                    audio_data, _ = librosa.load(file_path, sr=None, mono=False)
                    stems[stem_name] = audio_data
                    logger.info(f"Loaded stem: {stem_name}, shape: {audio_data.shape}")
                except Exception as e:
                    logger.warning(f"Could not load stem {stem_name}: {e}")
        
        return stems
    
    async def _calculate_quality_metrics(self, original_audio: np.ndarray, 
                                       separated_stems: Dict[str, np.ndarray],
                                       sample_rate: int) -> Dict[str, float]:
        """Calculate quality metrics for separation"""
        metrics = {}
        
        try:
            # Signal-to-noise ratio estimation
            if len(separated_stems) > 0:
                reconstructed = sum(separated_stems.values())
                noise = original_audio - reconstructed
                
                signal_power = np.mean(original_audio ** 2)
                noise_power = np.mean(noise ** 2)
                
                if noise_power > 0:
                    snr = 10 * np.log10(signal_power / noise_power)
                    metrics["snr_db"] = float(snr)
                else:
                    metrics["snr_db"] = 100.0  # Perfect reconstruction
            
            # Spectral distortion
            original_spec = np.abs(librosa.stft(original_audio))
            reconstructed_spec = np.abs(librosa.stft(reconstructed))
            
            spectral_distortion = np.mean(np.abs(original_spec - reconstructed_spec))
            metrics["spectral_distortion"] = float(spectral_distortion)
            
            # Separation quality (based on stem independence)
            stem_correlations = []
            stem_names = list(separated_stems.keys())
            
            for i, stem1_name in enumerate(stem_names):
                stem1 = separated_stems[stem1_name]
                for j, stem2_name in enumerate(stem_names[i+1:], i+1):
                    stem2 = separated_stems[stem2_name]
                    
                    # Calculate correlation
                    correlation = np.corrcoef(stem1.flatten(), stem2.flatten())[0, 1]
                    stem_correlations.append(abs(correlation))
            
            if stem_correlations:
                avg_correlation = np.mean(stem_correlations)
                metrics["separation_quality"] = float(1.0 - avg_correlation)
            else:
                metrics["separation_quality"] = 1.0
            
            # Overall quality score
            snr_score = min(1.0, max(0.0, (metrics.get("snr_db", 0) + 20) / 40))
            distortion_score = min(1.0, max(0.0, 1.0 - metrics.get("spectral_distortion", 0) / 1000))
            separation_score = metrics.get("separation_quality", 0)
            
            metrics["overall_quality"] = (snr_score + distortion_score + separation_score) / 3
            
        except Exception as e:
            logger.error(f"Error calculating quality metrics: {e}")
            metrics = {
                "snr_db": 0.0,
                "spectral_distortion": 1.0,
                "separation_quality": 0.0,
                "overall_quality": 0.0,
                "error": str(e)
            }
        
        return metrics


# Celery tasks for async processing
from celery import Celery
from celery.signals import worker_process_init

# Initialize Celery app
celery_app = Celery(
    'echosplit',
    broker=os.getenv('RABBITMQ_URL', 'amqp://guest:guest@localhost:5672/'),
    backend=os.getenv('REDIS_URL', 'redis://localhost:6379/0')
)

# Celery configuration
celery_app.conf.update(
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='UTC',
    enable_utc=True,
    task_routes={
        'echosplit.tasks.separate_audio_task': {'queue': 'separation'},
        'echosplit.tasks.analyze_emotions_task': {'queue': 'analysis'},
    }
)

# Global separator instance for Celery workers
separator_instance = None


@worker_process_init.connect
def init_worker(**kwargs):
    """Initialize separator instance in worker process"""
    global separator_instance
    separator_instance = SpleeterRunner()


@celery_app.task(bind=True)
def separate_audio_task(self, audio_file_path: str, model: str, output_format: str, user_consent: dict):
    """Celery task for audio separation"""
    try:
        if not separator_instance:
            raise RuntimeError("Separator not initialized in worker")
        
        # Run separation
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        result = loop.run_until_complete(
            separator_instance.separate_audio(
                audio_file_path,
                SeparationModel(model),
                output_format,
                user_consent
            )
        )
        
        # Convert numpy arrays to lists for serialization
        serializable_result = {
            "stems": {k: v.tolist() for k, v in result.stems.items()},
            "sample_rate": result.sample_rate,
            "model_used": result.model_used,
            "processing_time": result.processing_time,
            "audio_quality_metrics": result.audio_quality_metrics,
            "emotional_analysis": result.emotional_analysis
        }
        
        return serializable_result
        
    except Exception as exc:
        logger.error(f"Task failed: {exc}")
        self.retry(countdown=60, max_retries=3)