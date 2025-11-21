"""
EchoPlay API - FastAPI application for emotional playback engine
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

from ..playback_engine.emotional_playback import EmotionalPlaybackEngine, PlaybackSession, PlaybackState
from ..emotional_timeline.timeline_engine import EmotionalTimelineEngine, TimelineMode, EmotionalWaypoint
from ..adaptive_controls.feedback_processor import FeedbackProcessor, FeedbackType, UserConsent
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
playback_engine = None
timeline_engine = None
feedback_processor = None
ethical_ai = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan management"""
    global playback_engine, timeline_engine, feedback_processor, ethical_ai
    
    # Startup
    logger.info("Starting EchoPlay service...")
    
    # Initialize core services
    playback_engine = EmotionalPlaybackEngine()
    timeline_engine = EmotionalTimelineEngine()
    feedback_processor = FeedbackProcessor()
    ethical_ai = EthicalAI()
    
    logger.info("EchoPlay services initialized successfully")
    
    yield
    
    # Shutdown
    logger.info("Shutting down EchoPlay service...")


# Create FastAPI app
app = FastAPI(
    title="EchoPlay API",
    description="Emotional Playback Engine & Adaptive Timeline Service - Part of Eden Music Scene",
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
class PlaybackSessionRequest(BaseModel):
    playlist: List[Dict[str, Any]] = Field(description="List of tracks with audio data and metadata")
    user_preferences: Dict[str, Any] = Field(default_factory=dict)
    consent: UserConsent


class PlaybackControlRequest(BaseModel):
    session_id: str
    action: str = Field(description="play, pause, skip, seek, stop")
    parameters: Dict[str, Any] = Field(default_factory=dict)


class EmotionalFeedbackRequest(BaseModel):
    session_id: str
    feedback_type: str = Field(description="Type of feedback: emotional_response, satisfaction, etc.")
    data: Dict[str, Any] = Field(description="Feedback data")
    playback_position: float = Field(default=0.0)


class TimelineRequest(BaseModel):
    session_id: str
    total_duration: float
    mode: str = Field(default="adaptive", description="Timeline mode: linear, curved, adaptive, responsive")
    initial_emotion: Optional[Dict[str, float]] = None
    target_emotion: Optional[Dict[str, float]] = None
    waypoints: Optional[List[Dict[str, Any]]] = None


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
            "playback_engine": "ready" if playback_engine else "not_ready",
            "timeline_engine": "ready" if timeline_engine else "not_ready",
            "feedback_processor": "ready" if feedback_processor else "not_ready",
            "ethical_ai": "ready" if ethical_ai else "not_ready"
        }
    )


@app.post("/api/play/session")
async def create_playback_session(request: PlaybackSessionRequest, background_tasks: BackgroundTasks):
    """Create a new emotional playback session"""
    try:
        # Validate consent
        if not ethical_ai.consent_manager.validate_consent(request.consent.dict()):
            raise HTTPException(
                status_code=400,
                detail="Consent required for playback session"
            )
        
        # Create session
        session_id = await playback_engine.create_session(
            playlist_data=request.playlist,
            user_preferences=request.user_preferences,
            user_consent=request.consent.dict()
        )
        
        # Start background monitoring
        background_tasks.add_task(_monitor_session, session_id)
        
        return JSONResponse({
            "session_id": session_id,
            "status": "session_created",
            "tracks": len(request.playlist),
            "preferences_applied": list(request.user_preferences.keys())
        })
        
    except Exception as e:
        logger.error(f"Error creating playback session: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to create session: {str(e)}"
        )


@app.post("/api/play/control")
async def control_playback(request: PlaybackControlRequest):
    """Control playback (play, pause, skip, seek, stop)"""
    try:
        result = await playback_engine.control_playback(
            session_id=request.session_id,
            action=request.action,
            **request.parameters
        )
        
        return JSONResponse(result)
        
    except Exception as e:
        logger.error(f"Error controlling playback: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to control playback: {str(e)}"
        )


@app.get("/api/play/state/{session_id}")
async def get_playback_state(session_id: str):
    """Get current playback state"""
    try:
        state = await playback_engine.get_playback_state(session_id)
        return JSONResponse(state)
        
    except Exception as e:
        logger.error(f"Error getting playback state: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get playback state: {str(e)}"
        )


@app.post("/api/play/feedback")
async def submit_emotional_feedback(request: EmotionalFeedbackRequest):
    """Submit emotional feedback for adaptive playback"""
    try:
        feedback_data = {
            "session_id": request.session_id,
            "type": request.feedback_type,
            "data": request.data,
            "playback_position": request.playback_position,
            "track_id": request.data.get("track_id", ""),
            "context": request.data.get("context", {})
        }
        
        feedback_id = await feedback_processor.submit_feedback(feedback_data)
        
        # Also process through playback engine for immediate adaptation
        await playback_engine.provide_emotional_feedback(
            session_id=request.session_id,
            feedback=request.data
        )
        
        return JSONResponse({
            "feedback_id": feedback_id,
            "status": "feedback_recorded",
            "session_id": request.session_id
        })
        
    except Exception as e:
        logger.error(f"Error submitting feedback: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to submit feedback: {str(e)}"
        )


@app.post("/api/play/timeline")
async def create_emotional_timeline(request: TimelineRequest):
    """Create emotional timeline for playback session"""
    try:
        # Convert waypoints if provided
        waypoints = None
        if request.waypoints:
            waypoints = [
                EmotionalWaypoint(
                    timestamp=w["timestamp"],
                    valence=w["valence"],
                    arousal=w["arousal"],
                    dominance=w["dominance"],
                    intensity=w["intensity"],
                    duration=w.get("duration", 0.0),
                    transition_curve=w.get("transition_curve", "smooth")
                )
                for w in request.waypoints
            ]
        
        timeline_id = await timeline_engine.create_timeline(
            session_id=request.session_id,
            total_duration=request.total_duration,
            mode=TimelineMode(request.mode),
            initial_emotion=request.initial_emotion,
            target_emotion=request.target_emotion,
            waypoints=waypoints
        )
        
        return JSONResponse({
            "timeline_id": timeline_id,
            "session_id": request.session_id,
            "mode": request.mode,
            "duration": request.total_duration
        })
        
    except Exception as e:
        logger.error(f"Error creating timeline: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to create timeline: {str(e)}"
        )


@app.get("/api/play/timeline/{timeline_id}")
async def get_timeline_state(timeline_id: str):
    """Get emotional timeline state"""
    try:
        state = await timeline_engine.get_timeline_state(timeline_id)
        return JSONResponse(state)
        
    except Exception as e:
        logger.error(f"Error getting timeline state: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get timeline state: {str(e)}"
        )


@app.post("/api/play/timeline/{timeline_id}/advance")
async def advance_timeline(timeline_id: str, time_delta: float, feedback: Optional[Dict[str, Any]] = None):
    """Advance emotional timeline with optional feedback"""
    try:
        state = await timeline_engine.advance_timeline(timeline_id, time_delta, feedback)
        return JSONResponse(state)
        
    except Exception as e:
        logger.error(f"Error advancing timeline: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to advance timeline: {str(e)}"
        )


@app.get("/api/play/analytics/{session_id}")
async def get_session_analytics(session_id: str):
    """Get analytics for playback session"""
    try:
        analytics = await playback_engine.get_session_analytics(session_id)
        return JSONResponse(analytics)
        
    except Exception as e:
        logger.error(f"Error getting session analytics: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get analytics: {str(e)}"
        )


@app.get("/api/play/feedback/analytics/{session_id}")
async def get_feedback_analytics(session_id: str, hours: int = 1):
    """Get feedback analytics for session"""
    try:
        from datetime import timedelta
        analytics = await feedback_processor.get_feedback_analytics(
            session_id, 
            timedelta(hours=hours)
        )
        return JSONResponse(analytics)
        
    except Exception as e:
        logger.error(f"Error getting feedback analytics: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get feedback analytics: {str(e)}"
        )


@app.get("/api/play/consent/requirements")
async def get_consent_requirements():
    """Get information about consent requirements"""
    return JSONResponse({
        "required_consents": [
            "adaptive_playback",
            "feedback_collection",
            "data_storage",
            "timeline_tracking"
        ],
        "consent_purpose": "To provide adaptive emotional playback experiences while respecting user autonomy",
        "revocable": True,
        "data_retention": "Playback data is processed in real-time and not stored permanently",
        "third_party_sharing": False,
        "ethical_framework": "Echolace DI Ethical Standards",
        "audio_processing": "Real-time audio processing with emotional awareness"
    })


# WebSocket endpoint for real-time playback streaming
class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[str, WebSocket] = {}

    async def connect(self, websocket: WebSocket, session_id: str):
        await websocket.accept()
        self.active_connections[session_id] = websocket

    def disconnect(self, session_id: str):
        if session_id in self.active_connections:
            del self.active_connections[session_id]

    async def send_to_session(self, session_id: str, message: Dict[str, Any]):
        if session_id in self.active_connections:
            await self.active_connections[session_id].send_json(message)


manager = ConnectionManager()


@app.websocket("/ws/play/{session_id}")
async def websocket_endpoint(websocket: WebSocket, session_id: str):
    """WebSocket endpoint for real-time playback streaming and control"""
    await manager.connect(websocket, session_id)
    try:
        while True:
            data = await websocket.receive_json()
            
            if data.get("type") == "playback_control":
                # Handle playback control commands
                action = data.get("action")
                parameters = data.get("parameters", {})
                
                try:
                    result = await playback_engine.control_playback(session_id, action, **parameters)
                    await websocket.send_json({
                        "type": "control_result",
                        "data": result
                    })
                except Exception as e:
                    await websocket.send_json({
                        "type": "error",
                        "message": str(e)
                    })
            
            elif data.get("type") == "feedback":
                # Handle real-time feedback
                feedback_data = {
                    "session_id": session_id,
                    "type": data.get("feedback_type", "custom"),
                    "data": data.get("data", {}),
                    "playback_position": data.get("playback_position", 0.0)
                }
                
                try:
                    feedback_id = await feedback_processor.submit_feedback(feedback_data)
                    await websocket.send_json({
                        "type": "feedback_received",
                        "feedback_id": feedback_id
                    })
                except Exception as e:
                    await websocket.send_json({
                        "type": "error",
                        "message": str(e)
                    })
            
            elif data.get("type") == "state_request":
                # Send current playback state
                try:
                    state = await playback_engine.get_playback_state(session_id)
                    await websocket.send_json({
                        "type": "playback_state",
                        "data": state
                    })
                except Exception as e:
                    await websocket.send_json({
                        "type": "error",
                        "message": str(e)
                    })
            
            elif data.get("type") == "heartbeat"):
                await websocket.send_json({
                    "type": "heartbeat",
                    "timestamp": datetime.utcnow().isoformat()
                })
                
    except WebSocketDisconnect:
        manager.disconnect(session_id)


# Background tasks
async def _monitor_session(session_id: str):
    """Monitor playback session and send updates via WebSocket"""
    try:
        while True:
            # Get current state
            state = await playback_engine.get_playback_state(session_id)
            
            # Send to WebSocket if connected
            await manager.send_to_session(session_id, {
                "type": "state_update",
                "data": state
            })
            
            # Check if session is still active
            if state.get("state") == "stopped" and state.get("current_track") is None:
                break
            
            await asyncio.sleep(1.0)  # Update every second
            
    except Exception as e:
        logger.error(f"Error monitoring session {session_id}: {e}")


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
    port = int(os.getenv("PORT", 8003))
    host = os.getenv("HOST", "0.0.0.0")
    
    uvicorn.run(
        "main:app",
        host=host,
        port=port,
        reload=os.getenv("ENVIRONMENT") == "development",
        workers=1
    )