"""
Collaborative Sharing Engine
Handles collaborative playlist features and social sharing
"""

import asyncio
import uuid
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field
from enum import Enum
import structlog

from ..ethical_framework import EthicalAI

logger = structlog.get_logger(__name__)


class CollaborationRole(Enum):
    """Roles in collaborative playlist"""
    OWNER = "owner"
    EDITOR = "editor"
    CONTRIBUTOR = "contributor"
    VIEWER = "viewer"


class SharingPermission(Enum):
    """Sharing permission levels"""
    PRIVATE = "private"
    INVITE_ONLY = "invite_only"
    FRIENDS = "friends"
    PUBLIC = "public"


@dataclass
class CollaborativePlaylist:
    """Collaborative playlist with sharing features"""
    id: str
    original_playlist_id: str
    name: str
    description: str
    owner_id: str
    created_at: datetime
    permissions: SharingPermission
    collaborators: Dict[str, CollaborationRole] = field(default_factory=dict)
    emotional_voting: bool = True
    track_suggestions: List[Dict[str, Any]] = field(default_factory=list)
    voting_results: Dict[str, Dict[str, Any]] = field(default_factory=dict)
    shared_emotional_context: Dict[str, Any] = field(default_factory=dict)


@dataclass
class SharingInvitation:
    """Invitation to collaborate on playlist"""
    id: str
    playlist_id: str
    invited_by: str
    invited_user: str
    role: CollaborationRole
    message: str
    created_at: datetime
    expires_at: datetime
    accepted: Optional[bool] = None
    accepted_at: Optional[datetime] = None


@dataclass
class EmotionalVote:
    """Emotional vote on track or playlist element"""
    id: str
    playlist_id: str
    track_id: str
    user_id: str
    emotional_response: Dict[str, float]
    vote_type: str  # "like", "dislike", "suggestion", "emotional_match"
    comment: str = ""
    created_at: datetime = field(default_factory=datetime.utcnow)


class CollaborativeEngine:
    """
    Collaborative Sharing Engine
    
    Manages collaborative playlist features, sharing permissions,
    and social interaction while preserving emotional context.
    """
    
    def __init__(self):
        self.collaborative_playlists: Dict[str, CollaborativePlaylist] = {}
        self.active_invitations: Dict[str, SharingInvitation] = {}
        self.emotional_votes: Dict[str, List[EmotionalVote]] = {}
        self.ethical_ai = EthicalAI()
        
        logger.info("CollaborativeEngine initialized")
    
    async def create_collaborative_playlist(self,
                                          original_playlist_id: str,
                                          name: str,
                                          description: str,
                                          owner_id: str,
                                          permissions: SharingPermission,
                                          user_consent: Dict[str, bool]) -> str:
        """
        Create a new collaborative playlist
        
        Args:
            original_playlist_id: Source playlist ID
            name: Collaborative playlist name
            description: Playlist description
            owner_id: Owner user ID
            permissions: Sharing permission level
            user_consent: User consent for collaboration
        
        Returns:
            Collaborative playlist ID
        """
        try:
            # Validate ethical compliance
            is_permitted, violations = await self.ethical_ai.evaluate_action(
                "create_collaborative_playlist", {
                    "original_playlist_id": original_playlist_id,
                    "owner_id": owner_id,
                    "permissions": permissions.value,
                    "consent": user_consent
                }
            )
            
            if not is_permitted:
                logger.warning("Ethical violations in collaborative playlist creation")
                raise ValueError("Collaborative playlist creation not permitted")
            
            # Create collaborative playlist
            collab_id = str(uuid.uuid4())
            collaborative_playlist = CollaborativePlaylist(
                id=collab_id,
                original_playlist_id=original_playlist_id,
                name=name,
                description=description,
                owner_id=owner_id,
                created_at=datetime.utcnow(),
                permissions=permissions,
                collaborators={owner_id: CollaborationRole.OWNER}
            )
            
            self.collaborative_playlists[collab_id] = collaborative_playlist
            self.emotional_votes[collab_id] = []
            
            logger.info(f"Created collaborative playlist {collab_id}", extra={
                "owner_id": owner_id,
                "permissions": permissions.value
            })
            
            return collab_id
            
        except Exception as e:
            logger.error(f"Error creating collaborative playlist: {e}")
            raise
    
    async def invite_collaborator(self,
                                playlist_id: str,
                                invited_by: str,
                                invited_user: str,
                                role: CollaborationRole,
                                message: str,
                                expires_hours: int = 168) -> str:
        """
        Invite a user to collaborate on playlist
        
        Args:
            playlist_id: Collaborative playlist ID
            invited_by: User ID sending invitation
            invited_user: User ID being invited
            role: Collaboration role
            message: Invitation message
            expires_hours: Hours until invitation expires
        
        Returns:
            Invitation ID
        """
        try:
            playlist = self.collaborative_playlists.get(playlist_id)
            if not playlist:
                raise ValueError(f"Collaborative playlist {playlist_id} not found")
            
            # Check permissions
            if invited_by not in playlist.collaborators:
                raise ValueError("Only collaborators can invite others")
            
            # Create invitation
            invitation_id = str(uuid.uuid4())
            invitation = SharingInvitation(
                id=invitation_id,
                playlist_id=playlist_id,
                invited_by=invited_by,
                invited_user=invited_user,
                role=role,
                message=message,
                created_at=datetime.utcnow(),
                expires_at=datetime.utcnow() + timedelta(hours=expires_hours)
            )
            
            self.active_invitations[invitation_id] = invitation
            
            logger.info(f"Created invitation {invitation_id}", extra={
                "playlist_id": playlist_id,
                "invited_user": invited_user,
                "role": role.value
            })
            
            return invitation_id
            
        except Exception as e:
            logger.error(f"Error creating invitation: {e}")
            raise
    
    async def accept_invitation(self, invitation_id: str, user_id: str) -> bool:
        """Accept a collaboration invitation"""
        try:
            invitation = self.active_invitations.get(invitation_id)
            if not invitation:
                return False
            
            # Check if invitation is for this user
            if invitation.invited_user != user_id:
                return False
            
            # Check if invitation is still valid
            if datetime.utcnow() > invitation.expires_at:
                return False
            
            # Add user as collaborator
            playlist = self.collaborative_playlists[invitation.playlist_id]
            playlist.collaborators[user_id] = invitation.role
            
            # Mark invitation as accepted
            invitation.accepted = True
            invitation.accepted_at = datetime.utcnow()
            
            logger.info(f"User {user_id} accepted invitation {invitation_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error accepting invitation: {e}")
            return False
    
    async def submit_emotional_vote(self,
                                  playlist_id: str,
                                  user_id: str,
                                  track_id: str,
                                  emotional_response: Dict[str, float],
                                  vote_type: str,
                                  comment: str = "") -> str:
        """
        Submit emotional vote on track in collaborative playlist
        
        Args:
            playlist_id: Collaborative playlist ID
            user_id: User ID voting
            track_id: Track ID being voted on
            emotional_response: Emotional response data
            vote_type: Type of vote
            comment: Optional comment
        
        Returns:
            Vote ID
        """
        try:
            playlist = self.collaborative_playlists.get(playlist_id)
            if not playlist:
                raise ValueError(f"Playlist {playlist_id} not found")
            
            # Check if user is collaborator
            if user_id not in playlist.collaborators:
                raise ValueError("Only collaborators can vote")
            
            # Validate vote type
            valid_vote_types = ["like", "dislike", "suggestion", "emotional_match"]
            if vote_type not in valid_vote_types:
                raise ValueError(f"Invalid vote type: {vote_type}")
            
            # Create emotional vote
            vote_id = str(uuid.uuid4())
            vote = EmotionalVote(
                id=vote_id,
                playlist_id=playlist_id,
                track_id=track_id,
                user_id=user_id,
                emotional_response=emotional_response,
                vote_type=vote_type,
                comment=comment
            )
            
            # Store vote
            if playlist_id not in self.emotional_votes:
                self.emotional_votes[playlist_id] = []
            
            self.emotional_votes[playlist_id].append(vote)
            
            # Update voting results
            await self._update_voting_results(playlist_id, track_id)
            
            logger.info(f"Submitted emotional vote {vote_id}", extra={
                "playlist_id": playlist_id,
                "user_id": user_id,
                "vote_type": vote_type
            })
            
            return vote_id
            
        except Exception as e:
            logger.error(f"Error submitting emotional vote: {e}")
            raise
    
    async def suggest_track(self,
                          playlist_id: str,
                          user_id: str,
                          track_data: Dict[str, Any],
                          reason: str = "") -> str:
        """
        Suggest a track for collaborative playlist
        
        Args:
            playlist_id: Collaborative playlist ID
            user_id: User ID making suggestion
            track_data: Track information
            reason: Reason for suggestion
        
        Returns:
            Suggestion ID
        """
        try:
            playlist = self.collaborative_playlists.get(playlist_id)
            if not playlist:
                raise ValueError(f"Playlist {playlist_id} not found")
            
            # Check permissions
            if user_id not in playlist.collaborators:
                raise ValueError("Only collaborators can suggest tracks")
            
            # Create track suggestion
            suggestion_id = str(uuid.uuid4())
            suggestion = {
                "id": suggestion_id,
                "user_id": user_id,
                "track_data": track_data,
                "reason": reason,
                "created_at": datetime.utcnow(),
                "votes": [],
                "status": "pending"
            }
            
            playlist.track_suggestions.append(suggestion)
            
            logger.info(f"Created track suggestion {suggestion_id}", extra={
                "playlist_id": playlist_id,
                "user_id": user_id,
                "track_title": track_data.get("title", "Unknown")
            })
            
            return suggestion_id
            
        except Exception as e:
            logger.error(f"Error suggesting track: {e}")
            raise
    
    async def vote_on_suggestion(self,
                               playlist_id: str,
                               user_id: str,
                               suggestion_id: str,
                               vote: str,
                               emotional_response: Optional[Dict[str, float]] = None) -> bool:
        """Vote on a track suggestion"""
        try:
            playlist = self.collaborative_playlists.get(playlist_id)
            if not playlist:
                return False
            
            # Find suggestion
            suggestion = None
            for s in playlist.track_suggestions:
                if s["id"] == suggestion_id:
                    suggestion = s
                    break
            
            if not suggestion:
                return False
            
            # Check if user is collaborator
            if user_id not in playlist.collaborators:
                return False
            
            # Add vote
            user_vote = {
                "user_id": user_id,
                "vote": vote,  # "approve", "reject", "neutral"
                "emotional_response": emotional_response or {},
                "timestamp": datetime.utcnow()
            }
            
            suggestion["votes"].append(user_vote)
            
            # Check if suggestion should be accepted/rejected
            await self._evaluate_suggestion(playlist, suggestion)
            
            return True
            
        except Exception as e:
            logger.error(f"Error voting on suggestion: {e}")
            return False
    
    async def get_collaborative_playlist(self, playlist_id: str, user_id: str) -> Dict[str, Any]:
        """Get collaborative playlist details for user"""
        try:
            playlist = self.collaborative_playlists.get(playlist_id)
            if not playlist:
                raise ValueError(f"Playlist {playlist_id} not found")
            
            # Check user access
            user_role = playlist.collaborators.get(user_id)
            if not user_role and playlist.permissions != SharingPermission.PUBLIC:
                raise ValueError("Access denied")
            
            # Get emotional votes
            votes = self.emotional_votes.get(playlist_id, [])
            
            # Calculate aggregated emotional context
            aggregated_emotions = await self._calculate_aggregated_emotions(votes)
            
            return {
                "playlist": {
                    "id": playlist.id,
                    "name": playlist.name,
                    "description": playlist.description,
                    "owner_id": playlist.owner_id,
                    "created_at": playlist.created_at.isoformat(),
                    "permissions": playlist.permissions.value,
                    "user_role": user_role.value if user_role else None,
                    "emotional_voting": playlist.emotional_voting,
                    "collaborator_count": len(playlist.collaborators)
                },
                "suggestions": playlist.track_suggestions,
                "voting_results": playlist.voting_results,
                "aggregated_emotions": aggregated_emotions,
                "recent_votes": [
                    {
                        "id": v.id,
                        "track_id": v.track_id,
                        "user_id": v.user_id,
                        "vote_type": v.vote_type,
                        "emotional_response": v.emotional_response,
                        "comment": v.comment,
                        "created_at": v.created_at.isoformat()
                    }
                    for v in sorted(votes, key=lambda x: x.created_at, reverse=True)[:10]
                ]
            }
            
        except Exception as e:
            logger.error(f"Error getting collaborative playlist: {e}")
            raise
    
    async def update_sharing_permissions(self,
                                       playlist_id: str,
                                       user_id: str,
                                       new_permissions: SharingPermission) -> bool:
        """Update playlist sharing permissions"""
        try:
            playlist = self.collaborative_playlists.get(playlist_id)
            if not playlist:
                return False
            
            # Check if user is owner
            if playlist.owner_id != user_id:
                return False
            
            playlist.permissions = new_permissions
            
            logger.info(f"Updated permissions for playlist {playlist_id}", extra={
                "new_permissions": new_permissions.value
            })
            
            return True
            
        except Exception as e:
            logger.error(f"Error updating permissions: {e}")
            return False
    
    async def remove_collaborator(self,
                                playlist_id: str,
                                owner_id: str,
                                user_id_to_remove: str) -> bool:
        """Remove collaborator from playlist"""
        try:
            playlist = self.collaborative_playlists.get(playlist_id)
            if not playlist:
                return False
            
            # Check if requester is owner
            if playlist.owner_id != owner_id:
                return False
            
            # Can't remove owner
            if user_id_to_remove == playlist.owner_id:
                return False
            
            if user_id_to_remove in playlist.collaborators:
                del playlist.collaborators[user_id_to_remove]
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"Error removing collaborator: {e}")
            return False
    
    async def _update_voting_results(self, playlist_id: str, track_id: str):
        """Update voting results for track"""
        playlist = self.collaborative_playlists[playlist_id]
        votes = self.emotional_votes.get(playlist_id, [])
        
        # Filter votes for this track
        track_votes = [v for v in votes if v.track_id == track_id]
        
        if not track_votes:
            return
        
        # Calculate aggregated results
        vote_counts = {}
        emotional_aggregates = {
            "valence": [],
            "arousal": [],
            "dominance": [],
            "intensity": []
        }
        
        for vote in track_votes:
            vote_type = vote.vote_type
            vote_counts[vote_type] = vote_counts.get(vote_type, 0) + 1
            
            # Aggregate emotional responses
            for emotion_key in emotional_aggregates:
                if emotion_key in vote.emotional_response:
                    emotional_aggregates[emotion_key].append(vote.emotional_response[emotion_key])
        
        # Calculate averages
        emotional_averages = {}
        for emotion_key, values in emotional_aggregates.items():
            if values:
                emotional_averages[emotion_key] = sum(values) / len(values)
        
        # Store results
        playlist.voting_results[track_id] = {
            "vote_counts": vote_counts,
            "emotional_averages": emotional_averages,
            "total_votes": len(track_votes),
            "last_updated": datetime.utcnow().isoformat()
        }
    
    async def _evaluate_suggestion(self, playlist: CollaborativePlaylist, suggestion: Dict[str, Any]):
        """Evaluate whether to accept or reject track suggestion"""
        votes = suggestion["votes"]
        
        if not votes:
            return
        
        # Count votes
        approve_votes = sum(1 for v in votes if v["vote"] == "approve")
        reject_votes = sum(1 for v in votes if v["vote"] == "reject")
        total_votes = len(votes)
        
        # Decision logic
        approval_rate = approve_votes / total_votes if total_votes > 0 else 0
        
        if approval_rate >= 0.6 and total_votes >= 2:  # 60% approval with minimum 2 votes
            suggestion["status"] = "accepted"
            logger.info(f"Suggestion {suggestion['id']} accepted")
        elif reject_votes >= 2:  # 2 reject votes
            suggestion["status"] = "rejected"
            logger.info(f"Suggestion {suggestion['id']} rejected")
    
    async def _calculate_aggregated_emotions(self, votes: List[EmotionalVote]) -> Dict[str, Any]:
        """Calculate aggregated emotional context from votes"""
        if not votes:
            return {}
        
        emotional_aggregates = {
            "valence": [],
            "arousal": [],
            "dominance": [],
            "intensity": []
        }
        
        for vote in votes:
            for emotion_key in emotional_aggregates:
                if emotion_key in vote.emotional_response:
                    emotional_aggregates[emotion_key].append(vote.emotional_response[emotion_key])
        
        # Calculate statistics
        result = {}
        for emotion_key, values in emotional_aggregates.items():
            if values:
                result[emotion_key] = {
                    "average": sum(values) / len(values),
                    "min": min(values),
                    "max": max(values),
                    "count": len(values)
                }
        
        return result