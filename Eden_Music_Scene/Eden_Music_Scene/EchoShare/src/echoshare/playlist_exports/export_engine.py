"""
Playlist Export Engine
Handles export of playlists to various formats and platforms
"""

import asyncio
import uuid
from datetime import datetime
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field
from enum import Enum
import structlog
import json
import tempfile
import os

from ..ethical_framework import EthicalAI

logger = structlog.get_logger(__name__)


class ExportFormat(Enum):
    """Supported export formats"""
    M3U = "m3u"
    M3U8 = "m3u8"
    JSON = "json"
    CSV = "csv"
    SPOTIFY = "spotify"
    APPLE_MUSIC = "apple_music"
    YOUTUBE_MUSIC = "youtube_music"
    TIDAL = "tidal"
    DEEZER = "deezer"


class ExportStatus(Enum):
    """Export process status"""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


@dataclass
class ExportTrack:
    """Track information for export"""
    id: str
    title: str
    artist: str
    album: Optional[str] = None
    duration: Optional[int] = None  # seconds
    isrc: Optional[str] = None  # International Standard Recording Code
    spotify_id: Optional[str] = None
    apple_music_id: Optional[str] = None
    youtube_music_id: Optional[str] = None
    emotional_metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ExportMetadata:
    """Metadata for exported playlist"""
    name: str
    description: str
    created_by: str
    created_at: datetime
    emotional_arc: Optional[Dict[str, Any]] = None
    tags: List[str] = field(default_factory=list)
    privacy_level: str = "private"
    collaborative: bool = False


@dataclass
class ExportTask:
    """Export task information"""
    id: str
    playlist_id: str
    format: ExportFormat
    status: ExportStatus
    metadata: ExportMetadata
    tracks: List[ExportTrack]
    created_at: datetime
    completed_at: Optional[datetime] = None
    error_message: Optional[str] = None
    file_url: Optional[str] = None
    file_size: Optional[int] = None


class PlaylistExportEngine:
    """
    Playlist Export Engine
    
    Handles export of playlists to various formats and music platforms
    while preserving emotional context and metadata.
    """
    
    def __init__(self):
        self.active_tasks: Dict[str, ExportTask] = {}
        self.ethical_ai = EthicalAI()
        
        # Platform integration clients (would be initialized with actual credentials)
        self.spotify_client = None
        self.apple_music_client = None
        self.youtube_music_client = None
        
        logger.info("PlaylistExportEngine initialized")
    
    async def export_playlist(self,
                            playlist_id: str,
                            tracks: List[ExportTrack],
                            metadata: ExportMetadata,
                            export_format: ExportFormat,
                            user_consent: Dict[str, bool]) -> str:
        """
        Export playlist to specified format
        
        Args:
            playlist_id: Source playlist ID
            tracks: List of tracks to export
            metadata: Playlist metadata
            export_format: Target export format
            user_consent: User consent for processing
        
        Returns:
            Export task ID
        """
        try:
            # Validate ethical compliance
            is_permitted, violations = await self.ethical_ai.evaluate_action(
                "export_playlist", {
                    "playlist_id": playlist_id,
                    "track_count": len(tracks),
                    "format": export_format.value,
                    "consent": user_consent
                }
            )
            
            if not is_permitted:
                logger.warning("Ethical violations in playlist export request")
                raise ValueError("Playlist export not permitted due to ethical constraints")
            
            # Create export task
            task_id = str(uuid.uuid4())
            task = ExportTask(
                id=task_id,
                playlist_id=playlist_id,
                format=export_format,
                status=ExportStatus.PENDING,
                metadata=metadata,
                tracks=tracks,
                created_at=datetime.utcnow()
            )
            
            self.active_tasks[task_id] = task
            
            # Start export process
            asyncio.create_task(self._process_export_task(task_id))
            
            logger.info(f"Created export task {task_id}", extra={
                "playlist_id": playlist_id,
                "format": export_format.value,
                "tracks": len(tracks)
            })
            
            return task_id
            
        except Exception as e:
            logger.error(f"Error creating export task: {e}")
            raise
    
    async def get_export_status(self, task_id: str) -> Dict[str, Any]:
        """Get export task status and results"""
        try:
            task = self.active_tasks.get(task_id)
            if not task:
                raise ValueError(f"Export task {task_id} not found")
            
            return {
                "task_id": task_id,
                "status": task.status.value,
                "format": task.format.value,
                "playlist_id": task.playlist_id,
                "created_at": task.created_at.isoformat(),
                "completed_at": task.completed_at.isoformat() if task.completed_at else None,
                "file_url": task.file_url,
                "file_size": task.file_size,
                "error_message": task.error_message,
                "metadata": {
                    "name": task.metadata.name,
                    "description": task.metadata.description,
                    "created_by": task.metadata.created_by,
                    "privacy_level": task.metadata.privacy_level,
                    "collaborative": task.metadata.collaborative
                }
            }
            
        except Exception as e:
            logger.error(f"Error getting export status: {e}")
            raise
    
    async def cancel_export(self, task_id: str) -> bool:
        """Cancel an export task"""
        try:
            task = self.active_tasks.get(task_id)
            if not task:
                return False
            
            if task.status in [ExportStatus.PENDING, ExportStatus.PROCESSING]:
                task.status = ExportStatus.CANCELLED
                task.completed_at = datetime.utcnow()
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"Error cancelling export: {e}")
            return False
    
    async def list_export_tasks(self, playlist_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """List export tasks, optionally filtered by playlist"""
        try:
            tasks = []
            
            for task in self.active_tasks.values():
                if playlist_id and task.playlist_id != playlist_id:
                    continue
                
                tasks.append({
                    "task_id": task.id,
                    "playlist_id": task.playlist_id,
                    "format": task.format.value,
                    "status": task.status.value,
                    "created_at": task.created_at.isoformat(),
                    "completed_at": task.completed_at.isoformat() if task.completed_at else None
                })
            
            # Sort by creation time (newest first)
            tasks.sort(key=lambda t: t["created_at"], reverse=True)
            
            return tasks
            
        except Exception as e:
            logger.error(f"Error listing export tasks: {e}")
            return []
    
    async def _process_export_task(self, task_id: str):
        """Process export task in background"""
        try:
            task = self.active_tasks[task_id]
            task.status = ExportStatus.PROCESSING
            
            logger.info(f"Starting export task {task_id}")
            
            if task.format == ExportFormat.M3U:
                file_path = await self._export_m3u(task)
            elif task.format == ExportFormat.M3U8:
                file_path = await self._export_m3u8(task)
            elif task.format == ExportFormat.JSON:
                file_path = await self._export_json(task)
            elif task.format == ExportFormat.CSV:
                file_path = await self._export_csv(task)
            elif task.format == ExportFormat.SPOTIFY:
                file_path = await self._export_spotify(task)
            elif task.format == ExportFormat.APPLE_MUSIC:
                file_path = await self._export_apple_music(task)
            elif task.format == ExportFormat.YOUTUBE_MUSIC:
                file_path = await self._export_youtube_music(task)
            else:
                raise ValueError(f"Unsupported export format: {task.format}")
            
            # Update task with success
            task.status = ExportStatus.COMPLETED
            task.completed_at = datetime.utcnow()
            task.file_url = file_path
            
            # Calculate file size if local file
            if file_path and os.path.exists(file_path):
                task.file_size = os.path.getsize(file_path)
            
            logger.info(f"Completed export task {task_id}")
            
        except Exception as e:
            logger.error(f"Error processing export task {task_id}: {e}")
            task.status = ExportStatus.FAILED
            task.completed_at = datetime.utcnow()
            task.error_message = str(e)
    
    async def _export_m3u(self, task: ExportTask) -> str:
        """Export to M3U format"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.m3u', delete=False) as f:
            # Write M3U header
            f.write("#EXTM3U\n")
            
            # Write playlist info
            f.write(f"#PLAYLIST:{task.metadata.name}\n")
            if task.metadata.description:
                f.write(f"#DESCRIPTION:{task.metadata.description}\n")
            
            # Write tracks
            for track in task.tracks:
                # Extended info
                duration_str = str(track.duration) if track.duration else "-1"
                f.write(f"#EXTINF:{duration_str},{track.artist} - {track.title}\n")
                
                # Add emotional metadata as comments
                if track.emotional_metadata:
                    f.write(f"#EMOTIONAL_CONTEXT:{json.dumps(track.emotional_metadata)}\n")
                
                # Track path (would be actual file path or URL)
                f.write(f"#TRACK_ID:{track.id}\n")
                f.write(f"track_{track.id}.mp3\n")  # Placeholder path
            
            return f.name
    
    async def _export_m3u8(self, task: ExportTask) -> str:
        """Export to M3U8 (UTF-8) format"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.m3u8', delete=False, encoding='utf-8') as f:
            # Write M3U8 header
            f.write("#EXTM3U\n")
            f.write("#EXTENC:UTF-8\n")
            
            # Write playlist info
            f.write(f"#PLAYLIST:{task.metadata.name}\n")
            if task.metadata.description:
                f.write(f"#DESCRIPTION:{task.metadata.description}\n")
            
            # Write tracks
            for track in task.tracks:
                duration_str = str(track.duration) if track.duration else "-1"
                f.write(f"#EXTINF:{duration_str},{track.artist} - {track.title}\n")
                
                if track.emotional_metadata:
                    f.write(f"#EMOTIONAL_CONTEXT:{json.dumps(track.emotional_metadata)}\n")
                
                f.write(f"#TRACK_ID:{track.id}\n")
                f.write(f"track_{track.id}.mp3\n")
            
            return f.name
    
    async def _export_json(self, task: ExportTask) -> str:
        """Export to JSON format with full metadata"""
        export_data = {
            "playlist": {
                "id": task.playlist_id,
                "name": task.metadata.name,
                "description": task.metadata.description,
                "created_by": task.metadata.created_by,
                "created_at": task.metadata.created_at.isoformat(),
                "emotional_arc": task.metadata.emotional_arc,
                "tags": task.metadata.tags,
                "privacy_level": task.metadata.privacy_level,
                "collaborative": task.metadata.collaborative
            },
            "tracks": []
        }
        
        # Add tracks with full metadata
        for track in task.tracks:
            track_data = {
                "id": track.id,
                "title": track.title,
                "artist": track.artist,
                "album": track.album,
                "duration": track.duration,
                "isrc": track.isrc,
                "platform_ids": {
                    "spotify": track.spotify_id,
                    "apple_music": track.apple_music_id,
                    "youtube_music": track.youtube_music_id
                },
                "emotional_metadata": track.emotional_metadata
            }
            export_data["tracks"].append(track_data)
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(export_data, f, indent=2, ensure_ascii=False)
            return f.name
    
    async def _export_csv(self, task: ExportTask) -> str:
        """Export to CSV format"""
        import csv
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False, newline='') as f:
            writer = csv.writer(f)
            
            # Write header
            writer.writerow([
                "Track ID", "Title", "Artist", "Album", "Duration", "ISRC",
                "Spotify ID", "Apple Music ID", "YouTube Music ID", "Emotional Metadata"
            ])
            
            # Write tracks
            for track in task.tracks:
                writer.writerow([
                    track.id,
                    track.title,
                    track.artist,
                    track.album or "",
                    track.duration or "",
                    track.isrc or "",
                    track.spotify_id or "",
                    track.apple_music_id or "",
                    track.youtube_music_id or "",
                    json.dumps(track.emotional_metadata) if track.emotional_metadata else ""
                ])
            
            return f.name
    
    async def _export_spotify(self, task: ExportTask) -> str:
        """Export to Spotify playlist"""
        # This would require actual Spotify API integration
        # For now, create a JSON file with Spotify-specific format
        spotify_data = {
            "name": task.metadata.name,
            "description": task.metadata.description,
            "public": task.metadata.privacy_level == "public",
            "collaborative": task.metadata.collaborative,
            "tracks": []
        }
        
        for track in task.tracks:
            if track.spotify_id:
                spotify_data["tracks"].append({
                    "id": track.spotify_id,
                    "emotional_context": track.emotional_metadata
                })
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.spotify.json', delete=False) as f:
            json.dump(spotify_data, f, indent=2)
            return f.name
    
    async def _export_apple_music(self, task: ExportTask) -> str:
        """Export to Apple Music playlist"""
        # This would require actual Apple Music API integration
        apple_data = {
            "name": task.metadata.name,
            "description": task.metadata.description,
            "tracks": []
        }
        
        for track in task.tracks:
            if track.apple_music_id:
                apple_data["tracks"].append({
                    "id": track.apple_music_id,
                    "emotional_context": track.emotional_metadata
                })
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.apple_music.json', delete=False) as f:
            json.dump(apple_data, f, indent=2)
            return f.name
    
    async def _export_youtube_music(self, task: ExportTask) -> str:
        """Export to YouTube Music playlist"""
        # This would require actual YouTube Music API integration
        yt_data = {
            "title": task.metadata.name,
            "description": task.metadata.description,
            "privacyStatus": "public" if task.metadata.privacy_level == "public" else "private",
            "tracks": []
        }
        
        for track in task.tracks:
            if track.youtube_music_id:
                yt_data["tracks"].append({
                    "videoId": track.youtube_music_id,
                    "emotional_context": track.emotional_metadata
                })
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.youtube_music.json', delete=False) as f:
            json.dump(yt_data, f, indent=2)
            return f.name


# Celery tasks for async processing
from celery import Celery
import os

celery_app = Celery(
    'echoshare',
    broker=os.getenv('RABBITMQ_URL', 'amqp://guest:guest@localhost:5672/'),
    backend=os.getenv('REDIS_URL', 'redis://localhost:6379/0')
)

celery_app.conf.update(
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='UTC',
    enable_utc=True,
    task_routes={
        'echoshare.tasks.export_playlist_task': {'queue': 'exports'},
    }
)


@celery_app.task(bind=True)
def export_playlist_task(self, task_id: str):
    """Celery task for playlist export"""
    # This would be called by the export engine
    logger.info(f"Processing export task {task_id}")
    # Actual export processing would happen here