"""
EchoDJ API - FastAPI application for DJ Voltage personality service
"""

import asyncio
import os
from datetime import datetime
from typing import Dict, List, Optional, Any
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect, Depends, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
import structlog
import uvicorn

from ..voltage.personality import DJVoltage, VoltageResponse
from ..mood_router.emotional_routing import MoodRouter, EmotionalArc, TransitionStyle
from ..playlist_engine.dynamic_playlist import PlaylistGenerationEngine, DynamicPlaylist, PlaylistType
from ..ethical_framework import EthicalAI

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
dj_voltage = None
mood_router = None
playlist_engine = None
ethical_ai = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan management"""
    global dj_voltage, mood_router, playlist_engine, ethical_ai
    
    # Startup
    logger.info("Starting EchoDJ service...")
    
    # Initialize core services
    dj_voltage = DJVoltage()
    mood_router = MoodRouter()
    playlist_engine = PlaylistGenerationEngine()
    ethical_ai = EthicalAI()
    
    logger.info("EchoDJ services initialized successfully")
    
    yield
    
    # Shutdown
    logger.info("Shutting down EchoDJ service...")


# Create FastAPI app
app = FastAPI(
    title="EchoDJ API",
    description="Emotional DJ Intelligence Service - Part of Eden Music Scene",
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
class UserEmotion(BaseModel):
    valence: float = Field(ge=-1.0, le=1.0, description="Pleasantness of emotion")
    arousal: float = Field(ge=0.0, le=1.0, description="Energy level of emotion")
    dominance: float = Field(ge=0.0, le=1.0, description="Control/feeling of power")
    depth: float = Field(ge=0.0, le=1.0, description="Emotional complexity")
    resonance: float = Field(ge=0.0, le=1.0, description="How much it resonates with user")


class UserConsent(BaseModel):
    emotional_processing: bool = Field(description="Consent for emotional data processing")
    data_storage: bool = Field(description="Consent for data storage")
    personality_interaction: bool = Field(description="Consent for AI personality interaction")


class PlaylistRequest(BaseModel):
    text: str = Field(description="User's playlist request text")
    target_emotion: Optional[UserEmotion] = None
    duration_minutes: int = Field(default=60, ge=10, le=480, description="Playlist duration in minutes")
    playlist_type: Optional[str] = None
    consent: UserConsent


class VoltageInteractionRequest(BaseModel):
    message: str = Field(description="User message to DJ Voltage")
    emotional_context: UserEmotion
    consent: UserConsent


class EmotionalAnalysisRequest(BaseModel):
    text: str = Field(description="Text to analyze for emotional content")
    consent: UserConsent


class PlaylistAdaptationRequest(BaseModel):
    playlist_id: str
    feedback_type: str = Field(description="Type of feedback: skip_frequency, emotional_response, completion_rate")
    feedback_data: Dict[str, Any]


class HealthResponse(BaseModel):
    status: str
    timestamp: datetime
    version: str
    services: Dict[str, str]


class ErrorResponse(BaseModel):
    error: str
    detail: str
    timestamp: datetime


# API endpoints
@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint"""
    return HealthResponse(
        status="healthy",
        timestamp=datetime.utcnow(),
        version="1.0.0",
        services={
            "dj_voltage": "ready" if dj_voltage else "not_ready",
            "mood_router": "ready" if mood_router else "not_ready",
            "playlist_engine": "ready" if playlist_engine else "not_ready",
            "ethical_ai": "ready" if ethical_ai else "not_ready"
        }
    )


@app.post("/api/dj/generate-playlist")
async def generate_playlist(request: PlaylistRequest, background_tasks: BackgroundTasks):
    """Generate an emotional playlist based on user input"""
    try:
        # Validate consent
        if not ethical_ai.consent_manager.validate_consent(request.consent.dict()):
            raise HTTPException(
                status_code=400,
                detail="Consent required for playlist generation"
            )
        
        # Convert user emotion to dict
        user_emotion = request.target_emotion.dict() if request.target_emotion else {
            "valence": 0.5,
            "arousal": 0.5,
            "dominance": 0.5,
            "depth": 0.5,
            "resonance": 0.7
        }
        
        # Mock available tracks (in real implementation, this would come from EchoStore)
        available_tracks = await _get_mock_available_tracks()
        
        # Generate preferences
        preferences = {
            "complexity": 4,
            "familiarity_preference": 0.6,
            "discovery_rate": 0.3,
            "emotional_sensitivity": 0.8,
            "max_artist_tracks": 2,
            "experience_level": "intermediate"
        }
        
        # Generate playlist
        playlist = await playlist_engine.generate_playlist(
            user_request=request.dict(),
            user_emotion=user_emotion,
            available_tracks=available_tracks,
            preferences=preferences
        )
        
        # Start background adaptation monitoring
        background_tasks.add_task(_monitor_playlist_adaptation, playlist.id)
        
        return JSONResponse({
            "playlist_id": playlist.id,
            "name": playlist.name,
            "description": playlist.description,
            "type": playlist.type.value,
            "tracks": [
                {
                    "id": track.id,
                    "title": track.title,
                    "artist": track.artist,
                    "duration": track.duration,
                    "transition_notes": track.transition_notes
                }
                for track in playlist.tracks
            ],
            "total_duration": playlist.total_duration,
            "emotional_route": {
                "arc_type": playlist.route.arc_type.value,
                "estimated_impact": playlist.route.estimated_impact,
                "waypoints": len(playlist.route.waypoints)
            }
        })
        
    except Exception as e:
        logger.error(f"Error generating playlist: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to generate playlist: {str(e)}"
        )


@app.post("/api/dj/voltage/interact")
async def voltage_interaction(request: VoltageInteractionRequest):
    """Interact with DJ Voltage personality"""
    try:
        # Validate consent
        if not ethical_ai.consent_manager.validate_consent(request.consent.dict()):
            raise HTTPException(
                status_code=400,
                detail="Consent required for personality interaction"
            )
        
        # Process interaction with DJ Voltage
        response = await dj_voltage.process_request(
            user_input=request.message,
            emotional_context=request.emotional_context.dict(),
            user_consent=request.consent.dict()
        )
        
        return JSONResponse({
            "response": response.message,
            "emotional_tone": response.emotional_tone,
            "suggested_action": response.suggested_action,
            "confidence": response.confidence,
            "ethical_considerations": response.ethical_considerations
        })
        
    except Exception as e:
        logger.error(f"Error in voltage interaction: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to process interaction: {str(e)}"
        )


@app.get("/api/dj/voltage/personality")
async def get_voltage_state():
    """Get DJ Voltage's current personality state"""
    try:
        state = await dj_voltage.get_personality_state()
        return JSONResponse({
            "current_mood": state["current_mood"],
            "emotional_state": state["emotional_state"],
            "energy_level": state["energy_level"],
            "empathy_level": state["empathy_level"],
            "traits": state["traits"],
            "memory_size": state["memory_size"],
            "last_update": state["last_update"]
        })
    except Exception as e:
        logger.error(f"Error getting voltage state: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get personality state: {str(e)}"
        )


@app.post("/api/dj/mood/analyze")
async def analyze_emotional_content(request: EmotionalAnalysisRequest):
    """Analyze text for emotional content"""
    try:
        # Validate consent
        if not ethical_ai.consent_manager.validate_consent(request.consent.dict()):
            raise HTTPException(
                status_code=400,
                detail="Consent required for emotional analysis"
            )
        
        # Mock emotional analysis (in real implementation, this would use ML models)
        analysis = await _perform_emotional_analysis(request.text)
        
        return JSONResponse({
            "text": request.text,
            "dominant_emotion": analysis["dominant_emotion"],
            "emotional_state": analysis["emotional_state"],
            "confidence": analysis["confidence"],
            "analysis_timestamp": datetime.utcnow().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Error analyzing emotional content: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to analyze content: {str(e)}"
        )


@app.post("/api/dj/playlist/adapt")
async def adapt_playlist(request: PlaylistAdaptationRequest):
    """Adapt playlist based on user feedback"""
    try:
        # Adapt playlist using feedback
        adapted_playlist = await playlist_engine.adapt_playlist(
            playlist_id=request.playlist_id,
            feedback={
                "type": request.feedback_type,
                **request.feedback_data
            }
        )
        
        return JSONResponse({
            "playlist_id": adapted_playlist.id,
            "adaptation_applied": True,
            "updated_track_count": len(adapted_playlist.tracks),
            "updated_duration": adapted_playlist.total_duration,
            "last_updated": adapted_playlist.updated_at.isoformat()
        })
        
    except Exception as e:
        logger.error(f"Error adapting playlist: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to adapt playlist: {str(e)}"
        )


@app.get("/api/dj/consent/status")
async def get_consent_requirements():
    """Get information about consent requirements"""
    return JSONResponse({
        "required_consents": [
            "emotional_processing",
            "data_storage", 
            "personality_interaction"
        ],
        "consent_purpose": "To provide personalized emotional music experiences while respecting user autonomy",
        "revocable": True,
        "data_retention": "User data is retained only as long as necessary for the service",
        "third_party_sharing": False,
        "ethical_framework": "Echolace DI Ethical Standards"
    })


# WebSocket endpoint for real-time interactions
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


@app.websocket("/ws/dj")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket endpoint for real-time DJ interactions"""
    await manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_json()
            
            # Process interaction
            if data.get("type") == "interaction":
                response = await dj_voltage.process_request(
                    user_input=data.get("message", ""),
                    emotional_context=data.get("emotional_context", {}),
                    user_consent=data.get("consent", {})
                )
                
                await websocket.send_json({
                    "type": "response",
                    "data": {
                        "response": response.message,
                        "emotional_tone": response.emotional_tone,
                        "confidence": response.confidence
                    }
                })
            
            elif data.get("type") == "heartbeat":
                await websocket.send_json({
                    "type": "heartbeat",
                    "timestamp": datetime.utcnow().isoformat()
                })
                
    except WebSocketDisconnect:
        manager.disconnect(websocket)


# Background tasks
async def _monitor_playlist_adaptation(playlist_id: str):
    """Monitor playlist adaptation in background"""
    # This would typically connect to EchoPlay for real-time feedback
    logger.info(f"Starting adaptation monitoring for playlist {playlist_id}")
    
    # Mock monitoring loop
    while True:
        await asyncio.sleep(300)  # Check every 5 minutes
        # In real implementation, would collect feedback and adapt playlist
        logger.debug(f"Monitoring playlist {playlist_id}")


# Helper functions
async def _get_mock_available_tracks() -> List[Dict[str, Any]]:
    """Get mock available tracks for demonstration"""
    import random
    
    genres = ["ambient", "electronic", "jazz", "classical", "folk", "soul"]
    artists = ["Aurora Waves", "Digital Dreams", "Jazz Collective", "Symphony Orchestra", 
               "Mountain Echo", "Soul Sisters", "Electronic Pulse", "Classical Fusion"]
    
    tracks = []
    for i in range(50):
        track = {
            "id": f"track_{i}",
            "name": f"Musical Journey {i+1}",
            "artist": random.choice(artists),
            "duration_ms": random.randint(180000, 480000),  # 3-8 minutes
            "valence": random.uniform(0.2, 0.9),
            "energy": random.uniform(0.1, 0.9),
            "danceability": random.uniform(0.2, 0.8),
            "genre": random.choice(genres),
            "popularity": random.uniform(0.3, 0.9),
            "dominance": random.uniform(0.3, 0.8),
            "depth": random.uniform(0.4, 0.9)
        }
        tracks.append(track)
    
    return tracks


async def _perform_emotional_analysis(text: str) -> Dict[str, Any]:
    """Perform emotional analysis on text (mock implementation)"""
    import random
    
    emotions = ["joyful", "contemplative", "energetic", "peaceful", "nostalgic", "excited"]
    
    return {
        "dominant_emotion": random.choice(emotions),
        "emotional_state": {
            "valence": random.uniform(0.3, 0.9),
            "arousal": random.uniform(0.2, 0.8),
            "dominance": random.uniform(0.4, 0.8)
        },
        "confidence": random.uniform(0.6, 0.95)
    }


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
    port = int(os.getenv("PORT", 8000))
    host = os.getenv("HOST", "0.0.0.0")
    
    uvicorn.run(
        "main:app",
        host=host,
        port=port,
        reload=os.getenv("ENVIRONMENT") == "development",
        workers=1
    )