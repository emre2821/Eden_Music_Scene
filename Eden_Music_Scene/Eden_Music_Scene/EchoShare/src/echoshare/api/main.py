"""
EchoShare API - FastAPI application for sharing and playlist export service
"""

import asyncio
import os
from datetime import datetime
from typing import Dict, List, Optional, Any
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect, Depends, BackgroundTasks, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
import structlog
import uvicorn

from ..playlist_exports.export_engine import PlaylistExportEngine, ExportFormat, ExportTrack, ExportMetadata
from ..sharing.collaborative_engine import CollaborativeEngine, CollaborationRole, SharingPermission
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
export_engine = None
collaborative_engine = None
ethical_ai = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan management"""
    global export_engine, collaborative_engine, ethical_ai
    
    # Startup
    logger.info("Starting EchoShare service...")
    
    # Initialize core services
    export_engine = PlaylistExportEngine()
    collaborative_engine = CollaborativeEngine()
    ethical_ai = EthicalAI()
    
    logger.info("EchoShare services initialized successfully")
    
    yield
    
    # Shutdown
    logger.info("Shutting down EchoShare service...")


# Create FastAPI app
app = FastAPI(
    title="EchoShare API",
    description="Sharing & Playlist Export Service - Part of Eden Music Scene",
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
    sharing: bool = Field(description="Consent for sharing content")
    collaboration: bool = Field(description="Consent for collaboration features")
    public_sharing: bool = Field(description="Consent for public sharing")
    data_processing: bool = Field(description="Consent for data processing")
    metadata_sharing: bool = Field(description="Consent for metadata sharing")


class ExportRequest(BaseModel):
    playlist_id: str
    format: str = Field(description="Export format: m3u, m3u8, json, csv, spotify, apple_music, youtube_music")
    tracks: List[Dict[str, Any]] = Field(description="List of tracks to export")
    metadata: Dict[str, Any] = Field(description="Playlist metadata")
    consent: UserConsent


class CollaborativePlaylistRequest(BaseModel):
    original_playlist_id: str
    name: str
    description: str
    owner_id: str
    permissions: str = Field(default="private", description="Sharing permission level")
    consent: UserConsent


class InvitationRequest(BaseModel):
    playlist_id: str
    invited_by: str
    invited_user: str
    role: str = Field(description="Collaboration role: owner, editor, contributor, viewer")
    message: str = Field(default="")


class EmotionalVoteRequest(BaseModel):
    playlist_id: str
    user_id: str
    track_id: str
    emotional_response: Dict[str, float] = Field(description="Emotional response data")
    vote_type: str = Field(description="Vote type: like, dislike, suggestion, emotional_match")
    comment: str = Field(default="")


class TrackSuggestionRequest(BaseModel):
    playlist_id: str
    user_id: str
    track_data: Dict[str, Any]
    reason: str = Field(default="")


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
            "export_engine": "ready" if export_engine else "not_ready",
            "collaborative_engine": "ready" if collaborative_engine else "not_ready",
            "ethical_ai": "ready" if ethical_ai else "not_ready"
        }
    )


@app.post("/api/share/export")
async def export_playlist(request: ExportRequest, background_tasks: BackgroundTasks):
    """Export playlist to specified format"""
    try:
        # Validate consent
        if not ethical_ai.consent_manager.validate_consent(request.consent.dict()):
            raise HTTPException(
                status_code=400,
                detail="Consent required for playlist export"
            )
        
        # Convert tracks to ExportTrack objects
        export_tracks = []
        for track_data in request.tracks:
            track = ExportTrack(
                id=track_data.get("id", str(uuid.uuid4())),
                title=track_data.get("title", "Unknown Track"),
                artist=track_data.get("artist", "Unknown Artist"),
                album=track_data.get("album"),
                duration=track_data.get("duration"),
                isrc=track_data.get("isrc"),
                spotify_id=track_data.get("spotify_id"),
                apple_music_id=track_data.get("apple_music_id"),
                youtube_music_id=track_data.get("youtube_music_id"),
                emotional_metadata=track_data.get("emotional_metadata", {})
            )
            export_tracks.append(track)
        
        # Create export metadata
        metadata = ExportMetadata(
            name=request.metadata.get("name", "Exported Playlist"),
            description=request.metadata.get("description", ""),
            created_by=request.metadata.get("created_by", "Unknown"),
            created_at=datetime.utcnow(),
            emotional_arc=request.metadata.get("emotional_arc"),
            tags=request.metadata.get("tags", []),
            privacy_level=request.metadata.get("privacy_level", "private"),
            collaborative=request.metadata.get("collaborative", False)
        )
        
        # Start export
        task_id = await export_engine.export_playlist(
            playlist_id=request.playlist_id,
            tracks=export_tracks,
            metadata=metadata,
            export_format=ExportFormat(request.format),
            user_consent=request.consent.dict()
        )
        
        # Start background monitoring
        background_tasks.add_task(_monitor_export_task, task_id)
        
        return JSONResponse({
            "task_id": task_id,
            "status": "export_started",
            "format": request.format,
            "tracks": len(export_tracks)
        })
        
    except Exception as e:
        logger.error(f"Error exporting playlist: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to export playlist: {str(e)}"
        )


@app.get("/api/share/export/{task_id}/status")
async def get_export_status(task_id: str):
    """Get export task status"""
    try:
        status = await export_engine.get_export_status(task_id)
        return JSONResponse(status)
        
    except Exception as e:
        logger.error(f"Error getting export status: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get export status: {str(e)}"
        )


@app.delete("/api/share/export/{task_id}")
async def cancel_export(task_id: str):
    """Cancel export task"""
    try:
        success = await export_engine.cancel_export(task_id)
        return JSONResponse({
            "cancelled": success,
            "task_id": task_id
        })
        
    except Exception as e:
        logger.error(f"Error cancelling export: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to cancel export: {str(e)}"
        )


@app.get("/api/share/exports")
async def list_export_tasks(playlist_id: Optional[str] = None):
    """List export tasks"""
    try:
        tasks = await export_engine.list_export_tasks(playlist_id)
        return JSONResponse({"tasks": tasks})
        
    except Exception as e:
        logger.error(f"Error listing export tasks: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to list export tasks: {str(e)}"
        )


@app.post("/api/share/collaborative")
async def create_collaborative_playlist(request: CollaborativePlaylistRequest):
    """Create collaborative playlist"""
    try:
        # Validate consent
        if not ethical_ai.consent_manager.validate_consent(request.consent.dict()):
            raise HTTPException(
                status_code=400,
                detail="Consent required for collaborative playlist"
            )
        
        playlist_id = await collaborative_engine.create_collaborative_playlist(
            original_playlist_id=request.original_playlist_id,
            name=request.name,
            description=request.description,
            owner_id=request.owner_id,
            permissions=SharingPermission(request.permissions),
            user_consent=request.consent.dict()
        )
        
        return JSONResponse({
            "playlist_id": playlist_id,
            "status": "collaborative_playlist_created",
            "permissions": request.permissions
        })
        
    except Exception as e:
        logger.error(f"Error creating collaborative playlist: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to create collaborative playlist: {str(e)}"
        )


@app.post("/api/share/invite")
async def invite_collaborator(request: InvitationRequest):
    """Invite user to collaborate on playlist"""
    try:
        invitation_id = await collaborative_engine.invite_collaborator(
            playlist_id=request.playlist_id,
            invited_by=request.invited_by,
            invited_user=request.invited_user,
            role=CollaborationRole(request.role),
            message=request.message
        )
        
        return JSONResponse({
            "invitation_id": invitation_id,
            "status": "invitation_sent"
        })
        
    except Exception as e:
        logger.error(f"Error creating invitation: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to create invitation: {str(e)}"
        )


@app.post("/api/share/invite/{invitation_id}/accept")
async def accept_invitation(invitation_id: str, user_id: str):
    """Accept collaboration invitation"""
    try:
        success = await collaborative_engine.accept_invitation(invitation_id, user_id)
        return JSONResponse({
            "accepted": success,
            "invitation_id": invitation_id
        })
        
    except Exception as e:
        logger.error(f"Error accepting invitation: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to accept invitation: {str(e)}"
        )


@app.post("/api/share/vote")
async def submit_emotional_vote(request: EmotionalVoteRequest):
    """Submit emotional vote on track"""
    try:
        vote_id = await collaborative_engine.submit_emotional_vote(
            playlist_id=request.playlist_id,
            user_id=request.user_id,
            track_id=request.track_id,
            emotional_response=request.emotional_response,
            vote_type=request.vote_type,
            comment=request.comment
        )
        
        return JSONResponse({
            "vote_id": vote_id,
            "status": "vote_recorded"
        })
        
    except Exception as e:
        logger.error(f"Error submitting vote: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to submit vote: {str(e)}"
        )


@app.post("/api/share/suggest")
async def suggest_track(request: TrackSuggestionRequest):
    """Suggest track for collaborative playlist"""
    try:
        suggestion_id = await collaborative_engine.suggest_track(
            playlist_id=request.playlist_id,
            user_id=request.user_id,
            track_data=request.track_data,
            reason=request.reason
        )
        
        return JSONResponse({
            "suggestion_id": suggestion_id,
            "status": "suggestion_created"
        })
        
    except Exception as e:
        logger.error(f"Error suggesting track: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to suggest track: {str(e)}"
        )


@app.get("/api/share/collaborative/{playlist_id}")
async def get_collaborative_playlist(playlist_id: str, user_id: str):
    """Get collaborative playlist details"""
    try:
        playlist = await collaborative_engine.get_collaborative_playlist(playlist_id, user_id)
        return JSONResponse(playlist)
        
    except Exception as e:
        logger.error(f"Error getting collaborative playlist: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get collaborative playlist: {str(e)}"
        )


@app.put("/api/share/collaborative/{playlist_id}/permissions")
async def update_permissions(playlist_id: str, user_id: str, permissions: str):
    """Update playlist sharing permissions"""
    try:
        success = await collaborative_engine.update_sharing_permissions(
            playlist_id=playlist_id,
            user_id=user_id,
            new_permissions=SharingPermission(permissions)
        )
        
        return JSONResponse({
            "updated": success,
            "playlist_id": playlist_id,
            "new_permissions": permissions
        })
        
    except Exception as e:
        logger.error(f"Error updating permissions: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to update permissions: {str(e)}"
        )


@app.get("/api/share/consent/requirements")
async def get_consent_requirements():
    """Get information about consent requirements"""
    return JSONResponse({
        "required_consents": [
            "sharing",
            "collaboration",
            "public_sharing",
            "data_processing",
            "metadata_sharing"
        ],
        "consent_purpose": "To enable sharing and collaboration features while respecting user autonomy",
        "revocable": True,
        "data_retention": "Sharing data is retained according to user preferences and platform policies",
        "third_party_sharing": "Only with explicit consent and platform integrations",
        "ethical_framework": "Echolace DI Ethical Standards",
        "platform_integrations": "Spotify, Apple Music, YouTube Music, Tidal, Deezer"
    })


# WebSocket endpoint for real-time collaboration
class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[str, Dict[str, WebSocket]] = {}  # playlist_id -> user_id -> websocket

    async def connect(self, websocket: WebSocket, playlist_id: str, user_id: str):
        await websocket.accept()
        if playlist_id not in self.active_connections:
            self.active_connections[playlist_id] = {}
        self.active_connections[playlist_id][user_id] = websocket

    def disconnect(self, playlist_id: str, user_id: str):
        if playlist_id in self.active_connections and user_id in self.active_connections[playlist_id]:
            del self.active_connections[playlist_id][user_id]
            if not self.active_connections[playlist_id]:
                del self.active_connections[playlist_id]

    async def broadcast_to_playlist(self, playlist_id: str, message: Dict[str, Any], exclude_user: Optional[str] = None):
        if playlist_id in self.active_connections:
            for user_id, websocket in self.active_connections[playlist_id].items():
                if user_id != exclude_user:
                    await websocket.send_json(message)


manager = ConnectionManager()


@app.websocket("/ws/share/{playlist_id}/{user_id}")
async def websocket_endpoint(websocket: WebSocket, playlist_id: str, user_id: str):
    """WebSocket endpoint for real-time collaboration"""
    await manager.connect(websocket, playlist_id, user_id)
    try:
        while True:
            data = await websocket.receive_json()
            
            if data.get("type") == "emotional_vote":
                # Broadcast vote to other collaborators
                await manager.broadcast_to_playlist(playlist_id, {
                    "type": "new_vote",
                    "user_id": user_id,
                    "vote_data": data.get("vote_data", {})
                }, exclude_user=user_id)
            
            elif data.get("type") == "track_suggestion":
                # Broadcast suggestion to other collaborators
                await manager.broadcast_to_playlist(playlist_id, {
                    "type": "new_suggestion",
                    "user_id": user_id,
                    "suggestion_data": data.get("suggestion_data", {})
                }, exclude_user=user_id)
            
            elif data.get("type") == "heartbeat"):
                await websocket.send_json({
                    "type": "heartbeat",
                    "timestamp": datetime.utcnow().isoformat()
                })
                
    except WebSocketDisconnect:
        manager.disconnect(playlist_id, user_id)


# Background tasks
async def _monitor_export_task(task_id: str):
    """Monitor export task and notify via WebSocket when complete"""
    try:
        while True:
            status = await export_engine.get_export_status(task_id)
            
            if status["status"] in ["completed", "failed", "cancelled"]:
                # Could notify via WebSocket or other mechanism
                logger.info(f"Export task {task_id} completed with status: {status['status']}")
                break
            
            await asyncio.sleep(2)  # Check every 2 seconds
            
    except Exception as e:
        logger.error(f"Error monitoring export task {task_id}: {e}")


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
    port = int(os.getenv("PORT", 8004))
    host = os.getenv("HOST", "0.0.0.0")
    
    uvicorn.run(
        "main:app",
        host=host,
        port=port,
        reload=os.getenv("ENVIRONMENT") == "development",
        workers=1
    )