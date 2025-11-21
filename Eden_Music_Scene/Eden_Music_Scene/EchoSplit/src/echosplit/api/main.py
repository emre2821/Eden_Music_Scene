"""
EchoSplit API - FastAPI application for audio analysis and emotional decoding
"""

import asyncio
import os
import tempfile
from datetime import datetime
from typing import Dict, List, Optional, Any
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect, Depends, BackgroundTasks, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
import structlog
import uvicorn
import numpy as np

from ..lyss.daemon import LyssDaemon
from ..spleeter_runner.separator import SpleeterRunner, SeparationModel
from ..resonance.emotional_resonance import EmotionalResonanceEngine, ResonanceTimeline
from ..ethical_framework import EthicalAI, ConsentManager

# Configure logging
structlog.configure(
    processors=[
        structlog.stdlib.filter_by_level,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.processors.UnicodeDecoder(),
        structlog.processors.JSONRenderer()
    ],
    context_class=dict,
    logger_factory=structlog.stdlib.LoggerFactory(),
    wrapper_class=structlog.stdlib.BoundLogger,
    cache_logger_on_first_use=True,
)

logger = structlog.get_logger(__name__)

# Global service instances
lyss_daemon = None
spleeter_runner = None
resonance_engine = None
ethical_ai = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan management"""
    global lyss_daemon, spleeter_runner, resonance_engine, ethical_ai
    
    # Startup
    logger.info("Starting EchoSplit service...")
    
    # Initialize core services
    lyss_daemon = LyssDaemon()
    spleeter_runner = SpleeterRunner()
    resonance_engine = EmotionalResonanceEngine()
    ethical_ai = EthicalAI()
    
    logger.info("EchoSplit services initialized successfully")
    
    yield
    
    # Shutdown
    logger.info("Shutting down EchoSplit service...")


# Create FastAPI app
app = FastAPI(
    title="EchoSplit API",
    description="Advanced Audio Analysis & Emotional Decoding Service - Part of Eden Music Scene",
    version="1.0.0",
    lifespan=lifespan
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Pydantic models for API requests/responses
class UserConsent(BaseModel):
    audio_processing: bool = Field(description="Consent for audio processing")
    emotional_analysis: bool = Field(description="Consent for emotional analysis")
    data_storage: bool = Field(description="Consent for data storage")
    model_usage: bool = Field(description="Consent for AI model usage")


class SeparationRequest(BaseModel):
    model: str = Field(default="4stems", description="Separation model: 2stems, 4stems, 5stems")
    output_format: str = Field(default="wav", description="Output format: wav, mp3")
    include_emotional_analysis: bool = Field(default=True, description="Include emotional analysis")
    consent: UserConsent


class ResonanceAnalysisRequest(BaseModel):
    analysis_type: str = Field(description="Type: timeline, frequency, stem_interactions")
    include_patterns: bool = Field(default=True, description="Include resonance patterns")
    consent: UserConsent


class LyssStateResponse(BaseModel):
    current_mood: str
    processing_depth: float
    emotional_sensitivity: float
    analytical_precision: float
    creative_insight: float
    memory_size: int
    last_update: datetime


class HealthResponse(BaseModel):
    status: str
    timestamp: datetime
    version: str
    services: Dict[str, str]
    gpu_available: bool


class ErrorResponse(BaseModel):
    error: str
    detail: str
    timestamp: datetime


# API endpoints
@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint"""
    import torch
    gpu_available = torch.cuda.is_available()
    
    return HealthResponse(
        status="healthy",
        timestamp=datetime.utcnow(),
        version="1.0.0",
        services={
            "lyss_daemon": "ready" if lyss_daemon else "not_ready",
            "spleeter_runner": "ready" if spleeter_runner else "not_ready",
            "resonance_engine": "ready" if resonance_engine else "not_ready",
            "ethical_ai": "ready" if ethical_ai else "not_ready"
        },
        gpu_available=gpu_available
    )


@app.post("/api/split/separate")
async def separate_audio(file: UploadFile = File(...), request: SeparationRequest = Depends()):
    """Separate audio file into stems with optional emotional analysis"""
    try:
        # Validate consent
        if not ethical_ai.consent_manager.validate_consent(request.consent.dict()):
            raise HTTPException(
                status_code=400,
                detail="Consent required for audio separation"
            )
        
        # Save uploaded file temporarily
        with tempfile.NamedTemporaryFile(delete=False, suffix="." + file.filename.split('.')[-1]) as tmp_file:
            content = await file.read()
            tmp_file.write(content)
            tmp_file_path = tmp_file.name
        
        try:
            # Perform separation
            result = await spleeter_runner.separate_audio(
                audio_file_path=tmp_file_path,
                model=SeparationModel(request.model),
                output_format=request.output_format,
                user_consent=request.consent.dict()
            )
            
            # Convert numpy arrays to lists for JSON serialization
            serializable_stems = {k: v.tolist() for k, v in result.stems.items()}
            
            response = {
                "stems": serializable_stems,
                "sample_rate": result.sample_rate,
                "model_used": result.model_used,
                "processing_time": result.processing_time,
                "audio_quality_metrics": result.audio_quality_metrics
            }
            
            # Include emotional analysis if requested and consented
            if request.include_emotional_analysis and result.emotional_analysis:
                response["emotional_analysis"] = result.emotional_analysis
            
            return JSONResponse(response)
            
        finally:
            # Clean up temporary file
            import os
            if os.path.exists(tmp_file_path):
                os.unlink(tmp_file_path)
                
    except Exception as e:
        logger.error(f"Error separating audio: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to separate audio: {str(e)}"
        )


@app.post("/api/split/analyze")
async def analyze_audio_resonance(file: UploadFile = File(...), request: ResonanceAnalysisRequest = Depends()):
    """Analyze audio for emotional resonance"""
    try:
        # Validate consent
        if not ethical_ai.consent_manager.validate_consent(request.consent.dict()):
            raise HTTPException(
                status_code=400,
                detail="Consent required for resonance analysis"
            )
        
        # Save uploaded file temporarily
        with tempfile.NamedTemporaryFile(delete=False, suffix="." + file.filename.split('.')[-1]) as tmp_file:
            content = await file.read()
            tmp_file.write(content)
            tmp_file_path = tmp_file.name
        
        try:
            # Load audio
            import librosa
            audio_data, sample_rate = librosa.load(tmp_file_path, sr=None, mono=False)
            
            # Ensure correct shape
            if len(audio_data.shape) == 1:
                audio_data = audio_data[np.newaxis, :]
            
            # Analyze based on type
            if request.analysis_type == "timeline":
                result = await resonance_engine.analyze_resonance_timeline(
                    audio_data, sample_rate, request.consent.dict()
                )
                
                # Convert to serializable format
                serializable_result = {
                    "total_duration": result.total_duration,
                    "resonance_events": [
                        {
                            "timestamp": r.timestamp,
                            "frequency_range": r.frequency_range,
                            "resonance_level": r.resonance_level.value,
                            "emotional_quality": r.emotional_quality,
                            "intensity": r.intensity,
                            "duration": r.duration,
                            "harmonic_content": r.harmonic_content,
                            "rhythmic_signature": r.rhythmic_signature,
                            "spectral_features": r.spectral_features
                        }
                        for r in result.resonance_events
                    ],
                    "signature_patterns": [
                        {
                            "pattern_type": p.pattern_type.value,
                            "frequency_center": p.frequency_center,
                            "frequency_spread": p.frequency_spread,
                            "temporal_duration": p.temporal_duration,
                            "intensity_profile": p.intensity_profile,
                            "harmonic_content": {k.value: v for k, v in p.harmonic_content.items()},
                            "emotional_quality": p.emotional_quality,
                            "resonance_level": p.resonance_level.value,
                            "confidence": p.confidence
                        }
                        for p in result.signature_patterns
                    ],
                    "emotional_arc": result.emotional_arc
                }
                
            elif request.analysis_type == "frequency":
                result = await resonance_engine.analyze_frequency_resonance(
                    audio_data, sample_rate, request.consent.dict()
                )
                serializable_result = result
            
            else:
                raise HTTPException(status_code=400, detail="Invalid analysis type")
            
            return JSONResponse(serializable_result)
            
        finally:
            # Clean up temporary file
            import os
            if os.path.exists(tmp_file_path):
                os.unlink(tmp_file_path)
                
    except Exception as e:
        logger.error(f"Error analyzing audio resonance: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to analyze resonance: {str(e)}"
        )


@app.get("/api/split/lyss/state")
async def get_lyss_state():
    """Get Lyss daemon's current state"""
    try:
        state = await lyss_daemon.get_daemon_state()
        return JSONResponse(state)
    except Exception as e:
        logger.error(f"Error getting Lyss state: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get Lyss state: {str(e)}"
        )


@app.post("/api/split/lyss/adjust")
async def adjust_lyss_parameters(adjustments: Dict[str, float]):
    """Adjust Lyss daemon parameters"""
    try:
        # Validate parameter ranges
        for param, value in adjustments.items():
            if not (0.0 <= value <= 1.0):
                raise HTTPException(
                    status_code=400,
                    detail=f"Parameter {param} must be between 0.0 and 1.0"
                )
        
        await lyss_daemon.adjust_daemon_parameters(adjustments)
        
        return JSONResponse({
            "status": "parameters_updated",
            "adjustments": adjustments,
            "timestamp": datetime.utcnow().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Error adjusting Lyss parameters: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to adjust parameters: {str(e)}"
        )


@app.get("/api/split/consent/requirements")
async def get_consent_requirements():
    """Get information about consent requirements"""
    return JSONResponse({
        "required_consents": [
            "audio_processing",
            "emotional_analysis",
            "data_storage",
            "model_usage"
        ],
        "consent_purpose": "To provide advanced audio analysis and emotional decoding while respecting user autonomy",
        "revocable": True,
        "data_retention": "Audio data is processed temporarily and not stored permanently",
        "third_party_sharing": False,
        "ethical_framework": "Echolace DI Ethical Standards",
        "gpu_usage": "GPU acceleration is used for complex audio processing tasks"
    })


# WebSocket endpoint for real-time analysis updates
class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def broadcast(self, message: str):
        for connection in self.active_connections:
            await connection.send_text(message)


manager = ConnectionManager()


@app.websocket("/ws/split")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket endpoint for real-time analysis updates"""
    await manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_json()
            
            if data.get("type") == "analysis_update":
                # Send Lyss state update
                state = await lyss_daemon.get_daemon_state()
                await websocket.send_json({
                    "type": "lyss_state",
                    "data": state
                })
            
            elif data.get("type") == "heartbeat":
                await websocket.send_json({
                    "type": "heartbeat",
                    "timestamp": datetime.utcnow().isoformat()
                })
                
    except WebSocketDisconnect:
        manager.disconnect(websocket)


# Background tasks
async def _monitor_gpu_usage():
    """Monitor GPU usage and report to WebSocket clients"""
    import torch
    
    while True:
        if torch.cuda.is_available():
            gpu_usage = torch.cuda.memory_allocated() / torch.cuda.max_memory_allocated()
            
            await manager.broadcast(f"GPU usage: {gpu_usage:.2%}")
        
        await asyncio.sleep(30)  # Check every 30 seconds


# Error handlers
@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """Global exception handler"""
    logger.error(f"Unhandled exception: {exc}")
    return JSONResponse(
        status_code=500,
        content=ErrorResponse(
            error="Internal server error",
            detail=str(exc),
            timestamp=datetime.utcnow()
        ).dict()
    )


if __name__ == "__main__":
    port = int(os.getenv("PORT", 8002))
    host = os.getenv("HOST", "0.0.0.0")
    
    uvicorn.run(
        "main:app",
        host=host,
        port=port,
        reload=os.getenv("ENVIRONMENT") == "development",
        workers=1
    )