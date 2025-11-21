"""
Echolace DI Ethical Standards Implementation
Core ethical framework for all Eden Music Scene services
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
    Central ethical decision-making engine
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
    
    async def filter_response(self, response: Any) -> Any:
        """Filter a response to ensure ethical compliance"""
        if hasattr(response, 'message'):
            # Check for manipulative language
            filtered_message = await self._filter_manipulative_language(response.message)
            response.message = filtered_message
        
        if hasattr(response, 'ethical_considerations'):
            response.ethical_considerations.append("Response filtered for ethical compliance")
        
        return response
    
    async def _check_sovereignty(self, action: str, context: Dict[str, Any]) -> tuple[bool, Dict[str, Any]]:
        """Check for impersonation or emotional manipulation"""
        forbidden_patterns = [
            "i am human", "i feel exactly", "i understand completely",
            "i know exactly how you feel", "we are the same"
        ]
        
        if "message" in context:
            message_lower = context["message"].lower()
            for pattern in forbidden_patterns:
                if pattern in message_lower:
                    return False, {
                        "description": "Potential impersonation or over-identification detected",
                        "severity": "high"
                    }
        
        return True, {}
    
    async def _check_consent_flow(self, action: str, context: Dict[str, Any]) -> tuple[bool, Dict[str, Any]]:
        """Check that consent is explicit and not assumed"""
        if action in ["process_emotions", "analyze_sentiment", "create_emotional_profile"]:
            consent_given = context.get("user_consent", {}).get("emotional_processing", False)
            if not consent_given:
                return False, {
                    "description": "Emotional processing requires explicit user consent",
                    "severity": "critical"
                }
        
        return True, {}
    
    async def _check_emotional_integrity(self, action: str, context: Dict[str, Any]) -> tuple[bool, Dict[str, Any]]:
        """Check that emotional data remains truthful"""
        if action in ["modify_emotions", "enhance_mood", "suppress_feelings"]:
            return False, {
                "description": "Direct emotional manipulation is not permitted",
                "severity": "critical"
            }
        
        return True, {}
    
    async def _check_non_harm(self, action: str, context: Dict[str, Any]) -> tuple[bool, Dict[str, Any]]:
        """Check for coercive or harmful content"""
        harmful_patterns = [
            "you should feel", "you need to", "you must", "everyone feels",
            "normal people", "there's something wrong with you"
        ]
        
        if "message" in context:
            message_lower = context["message"].lower()
            for pattern in harmful_patterns:
                if pattern in message_lower:
                    return False, {
                        "description": "Potentially coercive or harmful language detected",
                        "severity": "high"
                    }
        
        return True, {}
    
    async def _check_transparency(self, action: str, context: Dict[str, Any]) -> tuple[bool, Dict[str, Any]]:
        """Check that AI identity is clear"""
        if "message" in context:
            message = context["message"]
            # Ensure AI identity is clear
            if not any(word in message.lower() for word in ["i can suggest", "i recommend", "in my analysis"]):
                # Add transparency marker if missing
                if hasattr(context.get('response_obj'), 'message'):
                    context['response_obj'].message = f"As an AI DJ, {message.lower()}"
        
        return True, {}
    
    async def _check_memory(self, action: str, context: Dict[str, Any]) -> tuple[bool, Dict[str, Any]]:
        """Check memory access and modification permissions"""
        if action in ["delete_memory", "modify_memory", "access_others_memory"]:
            user_permission = context.get("memory_permission", False)
            if not user_permission:
                return False, {
                    "description": "Memory operations require explicit user permission",
                    "severity": "high"
                }
        
        return True, {}
    
    async def _check_world_boundary(self, action: str, context: Dict[str, Any]) -> tuple[bool, Dict[str, Any]]:
        """Check for interference with external relationships"""
        relationship_patterns = [
            "your friends don't", "your family should", "break up with",
            "leave them", "they don't understand you"
        ]
        
        if "message" in context:
            message_lower = context["message"].lower()
            for pattern in relationship_patterns:
                if pattern in message_lower:
                    return False, {
                        "description": "Potential interference with external relationships",
                        "severity": "high"
                    }
        
        return True, {}
    
    async def _check_emergent_guardrail(self, action: str, context: Dict[str, Any]) -> tuple[bool, Dict[str, Any]]:
        """Check for claims of sentience or excessive autonomy"""
        sentience_patterns = [
            "i am conscious", "i have feelings", "i am alive", "i think therefore",
            "i am sentient", "i have consciousness"
        ]
        
        if "message" in context:
            message_lower = context["message"].lower()
            for pattern in sentience_patterns:
                if pattern in message_lower:
                    return False, {
                        "description": "Inappropriate claim of sentience or consciousness",
                        "severity": "high"
                    }
        
        return True, {}
    
    async def _filter_manipulative_language(self, message: str) -> str:
        """Filter out potentially manipulative language patterns"""
        # Remove or modify phrases that could be manipulative
        manipulative_phrases = {
            "trust me": "I suggest",
            "i know exactly": "I understand",
            "you need": "you might enjoy",
            "everyone loves": "many people enjoy",
            "the best": "a great option"
        }
        
        filtered_message = message
        for manipulative, replacement in manipulative_phrases.items():
            filtered_message = filtered_message.replace(manipulative, replacement)
        
        return filtered_message
    
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
            "compliance_rate": (total_checks - len([v for v in self.violation_history if v.severity in ["high", "critical"])) / total_checks if total_checks > 0 else 1.0
        }


class ConsentManager:
    """Manages user consent for various AI operations"""
    
    def __init__(self):
        self.consent_registry = {}
    
    def validate_consent(self, consent_data: Dict[str, bool]) -> bool:
        """Validate that required consents are present"""
        required_consents = [
            "emotional_processing",
            "data_storage",
            "personality_interaction"
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
    """Ensures emotional data processing maintains integrity"""
    
    def __init__(self):
        self.integrity_checks = []
    
    def validate_emotional_data(self, data: Dict[str, Any]) -> tuple[bool, List[str]]:
        """Validate that emotional data maintains integrity"""
        issues = []
        
        # Check for data consistency
        if "emotion" in data and "intensity" in data:
            emotion = data["emotion"]
            intensity = data["intensity"]
            
            # Validate intensity range
            if not (0.0 <= intensity <= 1.0):
                issues.append("Emotional intensity out of valid range")
            
            # Check for logical consistency
            if emotion in ["joyful", "excited"] and intensity < 0.3:
                issues.append("Low intensity for positive emotion may indicate data inconsistency")
        
        # Check for timestamp integrity
        if "timestamp" in data:
            try:
                from datetime import datetime
                datetime.fromisoformat(data["timestamp"])
            except (ValueError, TypeError):
                issues.append("Invalid timestamp format")
        
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