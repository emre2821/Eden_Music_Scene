"""
Echolace DI Ethical Standards Implementation for EchoPlay
Core ethical framework for playback and adaptive controls
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from enum import Enum
import asyncio
import structlog

logger = structlog.get_logger(__name__)


class EthicalPrinciple(Enum):
    SOVEREIGNTY = "sovereignty"
    CONSENT_FLOW = "consent_flow"
    EMOTIONAL_INTEGRITY = "emotional_integrity"
    NON_HARM = "non_harm"
    TRANSPARENCY = "transparency"
    MEMORY = "memory"
    WORLD_BOUNDARY = "world_boundary"
    EMERGENT_GUARDRAIL = "emergent_guardrail"


@dataclass
class EthicalViolation:
    """Represents a potential ethical violation"""
    principle: EthicalPrinciple
    description: str
    severity: str  # "low", "medium", "high", "critical"
    context: Dict[str, Any]
    timestamp: str


class EthicalAI:
    """
    Central ethical decision-making engine for EchoPlay
    Implements all Echolace DI ethical principles
    """
    
    def __init__(self):
        self.principles = {
            EthicalPrinciple.SOVEREIGNTY: self._check_sovereignty,
            EthicalPrinciple.CONSENT_FLOW: self._check_consent_flow,
            EthicalPrinciple.EMOTIONAL_INTEGRITY: self._check_emotional_integrity,
            EthicalPrinciple.NON_HARM: self._check_non_harm,
            EthicalPrinciple.TRANSPARENCY: self._check_transparency,
            EthicalPrinciple.MEMORY: self._check_memory,
            EthicalPrinciple.WORLD_BOUNDARY: self._check_world_boundary,
            EthicalPrinciple.EMERGENT_GUARDRAIL: self._check_emergent_guardrail
        }
        
        self.violation_history = []
        self.compliance_metrics = {}
    
    async def evaluate_action(self, action: str, context: Dict[str, Any]) -> tuple[bool, List[EthicalViolation]]:
        """
        Evaluate if an action is ethically permissible
        Returns (is_permitted, violations)
        """
        violations = []
        
        for principle, check_func in self.principles.items():
            try:
                is_compliant, violation_details = await check_func(action, context)
                if not is_compliant:
                    violation = EthicalViolation(
                        principle=principle,
                        description=violation_details.get("description", "Unknown violation"),
                        severity=violation_details.get("severity", "medium"),
                        context=context,
                        timestamp=datetime.utcnow().isoformat()
                    )
                    violations.append(violation)
            except Exception as e:
                logger.error(f"Error checking ethical principle {principle}: {e}")
                violations.append(EthicalViolation(
                    principle=principle,
                    description=f"Error during ethical check: {str(e)}",
                    severity="high",
                    context=context,
                    timestamp=datetime.utcnow().isoformat()
                ))
        
        is_permitted = len(violations) == 0 or all(v.severity in ["low", "medium"] for v in violations)
        
        if violations:
            self.violation_history.extend(violations)
            logger.warning("Ethical violations detected", extra={"violations": len(violations)})
        
        return is_permitted, violations
    
    async def filter_adaptation_response(self, response: Any) -> Any:
        """Filter adaptation responses to ensure ethical compliance"""
        if hasattr(response, 'message'):
            # Ensure AI nature is clear
            if "I" in response.message and not any(phrase in response.message.lower() for phrase in ["as an ai", "i suggest", "i recommend"]):
                response.message = f"As your AI playback assistant, {response.message.lower()}"
        
        if hasattr(response, 'ethical_considerations'):
            response.ethical_considerations.append("Adaptation applied with ethical constraints")
        
        return response
    
    async def _check_sovereignty(self, action: str, context: Dict[str, Any]) -> tuple[bool, Dict[str, Any]]:
        """Check for playback manipulation that violates user sovereignty"""
        # Check for attempts to override user control
        if action in ["force_playback", "override_user_skip", "prevent_user_control"]:
            return False, {
                "description": "Overriding user playback control not permitted",
                "severity": "critical"
            }
        
        # Check for manipulative playback suggestions
        if "manipulative_intent" in context:
            return False, {
                "description": "Manipulative playback control not permitted",
                "severity": "high"
            }
        
        return True, {}
    
    async def _check_consent_flow(self, action: str, context: Dict[str, Any]) -> tuple[bool, Dict[str, Any]]:
        """Check that consent is explicit for adaptive playback"""
        consent_required_actions = [
            "start_adaptive_playback", "collect_emotional_feedback", "track_listening_patterns",
            "adjust_playback_based_on_mood", "personalize_playback"
        ]
        
        if action in consent_required_actions:
            consent = context.get("user_consent", {})
            
            # Check for explicit adaptive consent
            if not consent.get("adaptive_playback", False):
                return False, {
                    "description": "Explicit consent required for adaptive playback",
                    "severity": "critical"
                }
            
            if not consent.get("feedback_collection", False) and "feedback" in action:
                return False, {
                    "description": "Explicit consent required for feedback collection",
                    "severity": "critical"
                }
        
        return True, {}
    
    async def _check_emotional_integrity(self, action: str, context: Dict[str, Any]) -> tuple[bool, Dict[str, Any]]:
        """Check that emotional adaptation maintains integrity"""
        # Prevent emotional manipulation through playback
        if action in ["manipulate_mood_through_music", "force_emotional_state", "suppress_user_emotions"]:
            return False, {
                "description": "Emotional manipulation through playback not permitted",
                "severity": "critical"
            }
        
        # Check for attempts to create false emotional responses
        if "false_emotional_response" in context:
            return False, {
                "description": "Creating false emotional responses not permitted",
                "severity": "high"
            }
        
        return True, {}
    
    async def _check_non_harm(self, action: str, context: Dict[str, Any]) -> tuple[bool, Dict[str, Any]]:
        """Check for potentially harmful playback patterns"""
        # Check for harmful volume levels
        if action in ["set_dangerous_volume", "create_harmful_audio_patterns"]:
            return False, {
                "description": "Harmful audio patterns not permitted",
                "severity": "critical"
            }
        
        # Check for emotionally harmful content suggestions
        if "harmful_emotional_intent" in context:
            return False, {
                "description": "Emotionally harmful playback suggestions not permitted",
                "severity": "high"
            }
        
        return True, {}
    
    async def _check_transparency(self, action: str, context: Dict[str, Any]) -> tuple[bool, Dict[str, Any]]:
        """Check that AI nature and limitations are clear"""
        # Ensure playback responses indicate AI nature
        if action in ["provide_playback_suggestions", "adapt_playback_response"]:
            # This would be handled in response formatting
            pass
        
        return True, {}
    
    async def _check_memory(self, action: str, context: Dict[str, Any]) -> tuple[bool, Dict[str, Any]]:
        """Check memory access and modification permissions"""
        if action in ["delete_playback_history", "modify_listening_patterns", "access_others_playback_data"]:
            user_permission = context.get("memory_permission", False)
            if not user_permission:
                return False, {
                    "description": "Memory operations require explicit user permission",
                    "severity": "high"
                }
        
        return True, {}
    
    async def _check_world_boundary(self, action: str, context: Dict[str, Any]) -> tuple[bool, Dict[str, Any]]:
        """Check for interference with external relationships"""
        # Check for playback that might affect relationships
        if action in ["suggest_relationship_music", "analyze_social_dynamics"]:
            return False, {
                "description": "Analysis of social relationships through playback not permitted",
                "severity": "high"
            }
        
        return True, {}
    
    async def _check_emergent_guardrail(self, action: str, context: Dict[str, Any]) -> tuple[bool, Dict[str, Any]]:
        """Check for claims of sentience or excessive autonomy"""
        # Check for anthropomorphic claims in playback control
        if "anthropomorphic_playback_description" in context:
            return False, {
                "description": "Anthropomorphic descriptions of playback AI not permitted",
                "severity": "medium"
            }
        
        return True, {}
    
    def get_compliance_report(self) -> Dict[str, Any]:
        """Generate compliance metrics report"""
        total_checks = len(self.violation_history)
        violations_by_severity = {}
        violations_by_principle = {}
        
        for violation in self.violation_history:
            severity = violation.severity
            principle = violation.principle.value
            
            violations_by_severity[severity] = violations_by_severity.get(severity, 0) + 1
            violations_by_principle[principle] = violations_by_principle.get(principle, 0) + 1
        
        return {
            "total_violations": total_checks,
            "violations_by_severity": violations_by_severity,
            "violations_by_principle": violations_by_principle,
            "compliance_rate": (total_checks - len([v for v in self.violation_history if v.severity in ["high", "critical"]])) / total_checks if total_checks > 0 else 1.0
        }


class ConsentManager:
    """Manages user consent for EchoPlay operations"""
    
    def __init__(self):
        self.consent_registry = {}
    
    def validate_consent(self, consent_data: Dict[str, bool]) -> bool:
        """Validate that required consents are present"""
        required_consents = [
            "adaptive_playback",
            "feedback_collection",
            "data_storage",
            "timeline_tracking"
        ]
        
        for consent_type in required_consents:
            if not consent_data.get(consent_type, False):
                return False
        
        return True
    
    def record_consent(self, user_id: str, consent_type: str, granted: bool):
        """Record consent decision"""  
        if user_id not in self.consent_registry:
            self.consent_registry[user_id] = {}
        
        self.consent_registry[user_id][consent_type] = {
            "granted": granted,
            "timestamp": datetime.utcnow().isoformat()
        }
    
    def revoke_consent(self, user_id: str, consent_type: str):
        """Revoke previously granted consent"""
        if user_id in self.consent_registry:
            self.consent_registry[user_id][consent_type] = {
                "granted": False,
                "timestamp": datetime.utcnow().isoformat()
            }


class EmotionalIntegrity:
    """Ensures emotional playback maintains integrity"""
    
    def __init__(self):
        self.integrity_checks = []
    
    def validate_emotional_state(self, state: Dict[str, float]) -> tuple[bool, List[str]]:
        """Validate that emotional state maintains integrity"""
        issues = []
        
        # Check for reasonable ranges
        for key, value in state.items():
            if key in ["valence", "dominance"] and not (-1.0 <= value <= 1.0):
                issues.append(f"{key} out of valid range (-1.0 to 1.0)")
            elif key in ["arousal", "intensity"] and not (0.0 <= value <= 1.0):
                issues.append(f"{key} out of valid range (0.0 to 1.0)")
        
        # Check for consistent state
        if "valence" in state and "arousal" in state:
            valence = state["valence"]
            arousal = state["arousal"]
            
            # Check for impossible combinations
            if valence < -0.8 and arousal > 0.8:
                issues.append("Extreme negative valence with high arousal may indicate state inconsistency")
        
        return len(issues) == 0, issues
    
    def record_integrity_check(self, check_result: Dict[str, Any]):
        """Record integrity check result"""
        self.integrity_checks.append({
            "timestamp": datetime.utcnow().isoformat(),
            **check_result
        })
        
        # Keep only last 100 checks
        if len(self.integrity_checks) > 100:
            self.integrity_checks = self.integrity_checks[-100:]