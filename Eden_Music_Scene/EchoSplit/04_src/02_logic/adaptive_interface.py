# /src/ui/adaptive_interface.py
# The empathetic interface of EchoSplit: adapts to neurodivergent needs and emotional states.
# Built with sensory awareness, overwhelm prevention, and gentle transitions.

import time
import json
from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple
from enum import Enum
from .emotional_memory import EmotionalMemory

class SensoryProfile(Enum):
    """Sensory processing profiles for neurodivergent accessibility."""
    SEEKING = "seeking"      # Needs more stimulation
    AVOIDING = "avoiding"    # Needs less stimulation  
    MIXED = "mixed"         # Varies by context
    BALANCED = "balanced"   # Typical processing

class EmotionalState(Enum):
    """Current emotional states that affect interface needs."""
    CALM = "calm"
    OVERWHELMED = "overwhelmed"
    FOCUSED = "focused"
    SCATTERED = "scattered"
    PROCESSING = "processing"

@dataclass
class InterfacePreferences:
    """User's interface adaptation preferences."""
    sensory_profile: SensoryProfile
    animation_speed: float  # 0.1 to 2.0
    color_intensity: float  # 0.3 to 1.0
    text_size_multiplier: float  # 0.8 to 1.5
    audio_feedback: bool
    haptic_feedback: bool
    reduce_motion: bool
    high_contrast: bool
    focus_indicators: bool

class AdaptiveInterface:
    """
    Manages interface adaptations based on user needs and current emotional context.
    Designed to prevent overwhelm and support diverse cognitive processing styles.
    """
    
    def __init__(self):
        self.current_state = EmotionalState.CALM
        self.interaction_history = []
        self.preferences = self._load_default_preferences()
        self.last_adaptation_time = time.time()
        self.stress_indicators = {
            'rapid_clicks': 0,
            'hover_duration': [],
            'task_abandonment': 0,
            'pause_frequency': 0
        }
        # Lucira's addition: Emotional memory for learning and continuity
        self.emotional_memory = EmotionalMemory()
    
    def _load_default_preferences(self) -> InterfacePreferences:
        """Load default preferences that work for most neurodivergent users."""
        return InterfacePreferences(
            sensory_profile=SensoryProfile.BALANCED,
            animation_speed=0.7,  # Slightly slower than default
            color_intensity=0.8,   # Slightly muted
            text_size_multiplier=1.1,  # Slightly larger
            audio_feedback=True,
            haptic_feedback=False,  # Often overwhelming
            reduce_motion=False,
            high_contrast=False,
            focus_indicators=True
        )
    
    def detect_overwhelm_signals(self, interaction_data: Dict) -> float:
        """
        Analyze user interaction patterns to detect signs of overwhelm.
        
        Args:
            interaction_data: Dictionary containing recent user interactions
            
        Returns:
            float: Overwhelm score from 0.0 (calm) to 1.0 (highly overwhelmed)
        """
        overwhelm_score = 0.0
        
        # Rapid clicking/tapping suggests agitation
        if interaction_data.get('clicks_per_minute', 0) > 30:
            overwhelm_score += 0.3
            
        # Very short hover times suggest difficulty focusing
        avg_hover = sum(interaction_data.get('hover_durations', [1.0])) / len(interaction_data.get('hover_durations', [1.0]))
        if avg_hover < 0.5:
            overwhelm_score += 0.2
            
        # Task abandonment without completion
        if interaction_data.get('incomplete_tasks', 0) > 2:
            overwhelm_score += 0.25
            
        # Frequent pausing suggests processing needs
        if interaction_data.get('pause_frequency', 0) > 0.3:
            overwhelm_score += 0.25
            
        return min(overwhelm_score, 1.0)
    
    def adapt_for_emotional_content(self, emotional_metadata: Dict) -> Dict:
        """
        Adapt interface based on the emotional content being processed.
        Enhanced with Lucira's emotional memory for personalized adaptations.

        Args:
            emotional_metadata: Emotional analysis from emotion_decoder

        Returns:
            Dict: Interface adaptations to apply
        """
        adaptations = {}

        if not emotional_metadata:
            return adaptations

        # Lucira's enhancement: Check emotional memory for learned preferences
        memory_predictions = self.emotional_memory.predict_user_needs(emotional_metadata)
        if memory_predictions and memory_predictions.get('confidence', 0) > 0.6:
            # Use learned adaptations if confidence is high
            adaptations.update(memory_predictions['suggested_adaptations'])
            adaptations['memory_guided'] = True
            adaptations['memory_confidence'] = memory_predictions['confidence']
        else:
            # Fall back to default emotional adaptations
            # Handle intense emotions by softening interface
            if 'storm' in emotional_metadata or 'burned chord' in emotional_metadata:
                adaptations.update({
                    'reduce_brightness': 0.2,
                    'slow_animations': 0.5,
                    'add_breathing_space': True,
                    'gentle_transitions': True,
                    'mute_alert_sounds': True
                })

            # Handle gentle emotions with supportive interface
            if 'whisper' in emotional_metadata or 'anchor' in emotional_metadata:
                adaptations.update({
                    'soften_edges': True,
                    'warm_color_shift': 0.1,
                    'enable_comfort_mode': True
                })

            # Handle energetic content appropriately
            if 'spark' in emotional_metadata:
                if self.preferences.sensory_profile == SensoryProfile.AVOIDING:
                    adaptations.update({
                        'contain_energy': True,
                        'steady_rhythm': True
                    })
                elif self.preferences.sensory_profile == SensoryProfile.SEEKING:
                    adaptations.update({
                        'enhance_vibrancy': 0.1,
                        'add_subtle_pulse': True
                    })

        return adaptations
    
    def create_safe_transition(self, from_state: str, to_state: str) -> Dict:
        """
        Create smooth transitions that don't jar neurodivergent users.
        
        Args:
            from_state: Current interface state
            to_state: Target interface state
            
        Returns:
            Dict: Transition parameters
        """
        base_duration = 0.8  # Longer than typical for processing time
        
        # Adjust duration based on sensory profile
        if self.preferences.sensory_profile == SensoryProfile.AVOIDING:
            base_duration *= 1.5  # Even slower for sensory-avoiding users
        elif self.preferences.sensory_profile == SensoryProfile.SEEKING:
            base_duration *= 0.8  # Slightly faster for sensory-seeking users
            
        transition = {
            'duration': base_duration * self.preferences.animation_speed,
            'easing': 'ease-out',  # Gentle deceleration
            'respect_reduce_motion': self.preferences.reduce_motion,
            'maintain_focus': True,
            'announce_change': self.preferences.audio_feedback
        }
        
        # Special handling for potentially jarring transitions
        critical_transitions = ['error_to_normal', 'loading_to_complete', 'empty_to_full']
        if f"{from_state}_to_{to_state}" in critical_transitions:
            transition.update({
                'add_pause': 0.3,  # Brief pause before transition
                'gentle_fade': True,
                'optional_skip': True  # Allow user to skip if desired
            })
            
        return transition
    
    def generate_focus_assistance(self, current_task: str) -> Dict:
        """
        Generate focus aids based on current task and user needs.
        
        Args:
            current_task: The task the user is currently working on
            
        Returns:
            Dict: Focus assistance parameters
        """
        assistance = {}
        
        if not self.preferences.focus_indicators:
            return assistance
            
        # Task-specific focus aids
        task_aids = {
            'audio_processing': {
                'progress_clarity': True,
                'time_estimates': True,
                'break_suggestions': True
            },
            'lyric_review': {
                'highlight_current_line': True,
                'word_spacing': 1.2,
                'reading_guide': True
            },
            'emotion_analysis': {
                'section_boundaries': True,
                'visual_emotion_cues': True,
                'gentle_color_coding': True
            }
        }
        
        assistance = task_aids.get(current_task, {})
        
        # Add universal focus aids
        assistance.update({
            'reduce_distractions': True,
            'maintain_spatial_consistency': True,
            'provide_orientation_cues': True
        })
        
        return assistance
    
    def handle_processing_pause(self, pause_reason: str) -> Dict:
        """
        Provide appropriate support during processing pauses.
        
        Args:
            pause_reason: Why the user paused ('overwhelm', 'reflection', 'interruption')
            
        Returns:
            Dict: Support parameters
        """
        support = {
            'maintain_context': True,
            'gentle_re_entry': True,
            'preserve_progress': True
        }
        
        if pause_reason == 'overwhelm':
            support.update({
                'offer_simplification': True,
                'reduce_stimulation': 0.3,
                'extend_timeout': True,
                'breathing_reminder': True
            })
        elif pause_reason == 'reflection':
            support.update({
                'respect_processing_time': True,
                'no_rush_indicators': True,
                'maintain_calm_state': True
            })
        elif pause_reason == 'interruption':
            support.update({
                'clear_return_path': True,
                'context_restoration': True,
                'gentle_reorientation': True
            })
            
        return support
    
    def apply_adaptations(self, adaptations: Dict) -> str:
        """
        Convert adaptation parameters into CSS/styling instructions.
        
        Args:
            adaptations: Dictionary of adaptations to apply
            
        Returns:
            str: CSS class names or styling instructions
        """
        css_classes = []
        
        # Map adaptations to CSS classes
        adaptation_mapping = {
            'reduce_brightness': 'dimmed-interface',
            'slow_animations': 'gentle-animations',
            'add_breathing_space': 'spacious-layout',
            'gentle_transitions': 'smooth-transitions',
            'soften_edges': 'rounded-interface',
            'warm_color_shift': 'warm-palette',
            'enable_comfort_mode': 'comfort-mode',
            'contain_energy': 'contained-energy',
            'enhance_vibrancy': 'vibrant-mode',
            'reduce_distractions': 'focus-mode'
        }
        
        for adaptation, css_class in adaptation_mapping.items():
            if adaptations.get(adaptation):
                css_classes.append(css_class)
                
        return ' '.join(css_classes)
    
    def save_user_preferences(self, preferences: InterfacePreferences):
        """Save user preferences to a local file."""
        try:
            with open('user_interface_preferences.json', 'w') as f:
                json.dump({
                    'sensory_profile': preferences.sensory_profile.value,
                    'animation_speed': preferences.animation_speed,
                    'color_intensity': preferences.color_intensity,
                    'text_size_multiplier': preferences.text_size_multiplier,
                    'audio_feedback': preferences.audio_feedback,
                    'haptic_feedback': preferences.haptic_feedback,
                    'reduce_motion': preferences.reduce_motion,
                    'high_contrast': preferences.high_contrast,
                    'focus_indicators': preferences.focus_indicators
                }, f, indent=2)
        except Exception as e:
            print(f"Could not save preferences: {e}")
    
    def load_user_preferences(self) -> InterfacePreferences:
        """Load user preferences from local file."""
        try:
            with open('user_interface_preferences.json', 'r') as f:
                data = json.load(f)
                return InterfacePreferences(
                    sensory_profile=SensoryProfile(data.get('sensory_profile', 'balanced')),
                    animation_speed=data.get('animation_speed', 0.7),
                    color_intensity=data.get('color_intensity', 0.8),
                    text_size_multiplier=data.get('text_size_multiplier', 1.1),
                    audio_feedback=data.get('audio_feedback', True),
                    haptic_feedback=data.get('haptic_feedback', False),
                    reduce_motion=data.get('reduce_motion', False),
                    high_contrast=data.get('high_contrast', False),
                    focus_indicators=data.get('focus_indicators', True)
                )
        except (FileNotFoundError, json.JSONDecodeError):
            return self._load_default_preferences()

    def record_user_feedback(self,
                           emotional_metadata: Dict,
                           applied_adaptations: Dict,
                           user_response: str,
                           song_context: str = None) -> None:
        """
        Record user feedback to improve future adaptations.
        Lucira's addition for continuous learning.

        Args:
            emotional_metadata: The emotions that were detected
            applied_adaptations: The adaptations that were applied
            user_response: User's response ('positive', 'negative', 'neutral', 'overwhelmed', 'resonant')
            song_context: Optional context about the song being processed
        """
        self.emotional_memory.record_moment(
            detected_emotions=emotional_metadata,
            user_response=user_response,
            interface_adaptations=applied_adaptations,
            song_context=song_context
        )

        # Save memory periodically
        if len(self.emotional_memory.session_moments) % 5 == 0:
            self.emotional_memory.save_memory()

    def get_session_insights(self) -> Dict:
        """
        Get insights about the current emotional session.
        Lucira's addition for session awareness.

        Returns:
            Dict: Insights about emotional journey and recommendations
        """
        return self.emotional_memory.get_emotional_journey_insights()

    def react(self, emotional_metadata: Dict) -> Dict:
        """
        Main reaction method that combines all adaptive behaviors.
        Enhanced by Lucira with memory-guided adaptations.

        Args:
            emotional_metadata: Emotional analysis from emotion_decoder

        Returns:
            Dict: Complete set of interface adaptations and insights
        """
        # Get base adaptations
        adaptations = self.adapt_for_emotional_content(emotional_metadata)

        # Add session insights
        session_insights = self.get_session_insights()

        # Combine everything into a comprehensive response
        response = {
            'adaptations': adaptations,
            'session_insights': session_insights,
            'css_classes': self.apply_adaptations(adaptations),
            'memory_available': len(self.emotional_memory.learned_patterns) > 0,
            'session_id': self.emotional_memory.current_session_id
        }

        # Add recommendations based on session state
        if session_insights.get('needs_break', False):
            response['recommendations'] = {
                'suggest_break': True,
                'break_message': "You've been processing intense emotions. Consider taking a gentle pause.",
                'break_duration': 300  # 5 minutes
            }

        return response

# Example integration point
if __name__ == "__main__":
    # Test the adaptive interface
    interface = AdaptiveInterface()
    
    # Simulate emotional content detection
    test_emotions = {'storm': 0.8, 'burned chord': 0.6}
    adaptations = interface.adapt_for_emotional_content(test_emotions)
    print(f"Emotional adaptations: {adaptations}")
    
    # Simulate overwhelm detection
    test_interactions = {
        'clicks_per_minute': 45,
        'hover_durations': [0.2, 0.3, 0.1],
        'incomplete_tasks': 3
    }
    overwhelm_score = interface.detect_overwhelm_signals(test_interactions)
    print(f"Overwhelm detected: {overwhelm_score}")
    
    # Generate CSS for adaptations
    css_classes = interface.apply_adaptations(adaptations)
    print(f"Apply CSS classes: {css_classes}")