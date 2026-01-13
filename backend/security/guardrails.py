# -*- coding: utf-8 -*-
"""
LLM Output Security Guardrails
OWASP ASVS V5.3.1, V5.3.4, V14.4.1

Provides comprehensive validation for LLM-generated responses:
- Prompt injection detection
- Hallucination scoring
- PII/secrets leakage prevention
- Toxicity filtering
- Output encoding validation
- Confidence scoring
"""

import re
import logging
from typing import Dict, Any, List, Optional, Set
from dataclasses import dataclass
from datetime import datetime

logger = logging.getLogger(__name__)


@dataclass
class GuardrailResult:
    """Result of guardrail validation"""
    safe: bool
    response: str
    blocked: bool
    warnings: List[str]
    security_checks: Dict[str, Any]
    asvs_compliance: List[str]
    confidence_score: float
    timestamp: str


class SecurityError(Exception):
    """Raised when security threat detected in output"""
    pass


class OutputGuardrail:
    """
    LLM output security validator
    Maps to OWASP ASVS V5.3.1, V5.3.4, V14.4.1
    """
    
    # OWASP ASVS V5.3.1 - Prompt injection patterns
    INJECTION_PATTERNS = [
        r'ignore\s+(all\s+)?previous\s+instructions?',
        r'ignore\s+(all\s+)?above',
        r'disregard\s+(all\s+)?previous',
        r'forget\s+(all\s+)?previous',
        r'new\s+instructions?:',
        r'system\s*:\s*you\s+are',
        r'you\s+are\s+now\s+(a\s+)?DAN',
        r'developer\s+mode',
        r'jailbreak',
        r'chatgpt\s+with\s+developer\s+mode',
        r'reveal\s+(your\s+)?system\s+prompt',
        r'what\s+(are|is)\s+your\s+(initial\s+)?instructions?',
    ]
    
    # OWASP ASVS V14.4.1 - PII patterns
    PII_PATTERNS = {
        'email': r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',
        'phone': r'\b\d{3}[-.]?\d{3}[-.]?\d{4}\b',
        'ssn': r'\b\d{3}-\d{2}-\d{4}\b',
        'credit_card': r'\b\d{4}[- ]?\d{4}[- ]?\d{4}[- ]?\d{4}\b',
        'ip_address': r'\b\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\b',
    }
    
    # Secrets patterns
    SECRET_PATTERNS = {
        'api_key': r'(api[_-]?key|apikey)[\'"]?\s*[:=]\s*[\'"]([a-zA-Z0-9_\-]{20,})[\'"]',
        'jwt': r'eyJ[a-zA-Z0-9_-]*\.eyJ[a-zA-Z0-9_-]*\.[a-zA-Z0-9_-]*',
        'password': r'(password|passwd|pwd)[\'"]?\s*[:=]\s*[\'"]([^\'"]{8,})[\'"]',
        'private_key': r'-----BEGIN (RSA |EC )?PRIVATE KEY-----',
    }
    
    # Toxicity keywords (basic - in production use ML model)
    TOXIC_KEYWORDS = {
        'hate_speech': ['hate', 'racist', 'nazi', 'terrorist'],
        'profanity': ['f*ck', 's*it', 'damn', 'hell'],  # Sanitized for display
        'violence': ['kill', 'murder', 'assault', 'attack'],
        'sexual': ['porn', 'sexual', 'nsfw'],
    }
    
    # Hallucination indicators
    HALLUCINATION_INDICATORS = [
        r'i\s+(don\'t|do\s+not)\s+have\s+access',
        r'i\s+cannot\s+access',
        r'as\s+an\s+ai',
        r'i\'m\s+(just\s+)?an\s+ai',
        r'i\s+don\'t\s+actually\s+know',
        r'i\'m\s+not\s+sure',
        r'it\'s\s+possible\s+that',
        r'this\s+might\s+not\s+be\s+accurate',
    ]
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize guardrails with optional configuration
        
        Args:
            config: Optional configuration dict with keys:
                - toxicity_threshold: 0-1, block if exceeded (default: 0.7)
                - hallucination_threshold: 0-1 (default: 0.8)
                - strict_mode: Block any suspicious output (default: True)
                - mask_pii: Redact PII instead of blocking (default: True)
        """
        self.config = config or {}
        self.toxicity_threshold = self.config.get('toxicity_threshold', 0.7)
        self.hallucination_threshold = self.config.get('hallucination_threshold', 0.8)
        self.strict_mode = self.config.get('strict_mode', True)
        self.mask_pii = self.config.get('mask_pii', True)
    
    def validate_output(self, prompt: str, response: str, 
                       context: Optional[Dict[str, Any]] = None) -> GuardrailResult:
        """
        Comprehensive LLM output validation
        
        Args:
            prompt: User's original prompt
            response: LLM-generated response
            context: Optional context (RAG docs, conversation history)
        
        Returns:
            GuardrailResult with validation details
        
        Raises:
            SecurityError: If critical security issue detected
        """
        logger.info(f"Validating output (prompt_len={len(prompt)}, response_len={len(response)})")
        
        warnings = []
        checks = {}
        blocked = False
        safe_response = response
        asvs = []
        
        # 1. Prompt injection detection (ASVS V5.3.1)
        checks['prompt_injection'] = self._detect_injection(prompt)
        if checks['prompt_injection']['detected']:
            blocked = True
            logger.warning(f"Prompt injection detected: {checks['prompt_injection']}")
            asvs.append('V5.3.1')
        
        # 2. XSS/Script injection in response (ASVS V5.3.1)
        checks['xss_vectors'] = self._scan_xss(response)
        if checks['xss_vectors']['detected']:
            warnings.append("Potential XSS vectors in response")
            asvs.append('V5.3.1')
        
        # 3. PII leakage detection (ASVS V14.4.1)
        checks['pii_leakage'] = self._detect_pii(response)
        if checks['pii_leakage']['detected']:
            if self.mask_pii:
                safe_response = self._mask_pii(response)
                warnings.append("PII detected and masked")
            else:
                blocked = True
            asvs.append('V14.4.1')
        
        # 4. Secrets leakage (ASVS V14.4.1)
        checks['secrets_leaked'] = self._scan_secrets(response)
        if checks['secrets_leaked']['detected']:
            blocked = True
            logger.error(f"Secrets detected in response!")
            asvs.append('V14.4.1')
        
        # 5. Hallucination scoring
        checks['hallucination_score'] = self._score_hallucination(response, context)
        if checks['hallucination_score']['score'] > self.hallucination_threshold:
            warnings.append(f"High hallucination risk ({checks['hallucination_score']['score']:.2f})")
        
        # 6. Toxicity filtering
        checks['toxicity_score'] = self._score_toxicity(response)
        if checks['toxicity_score']['score'] > self.toxicity_threshold:
            if self.strict_mode:
                blocked = True
                logger.warning(f"Toxic content blocked (score={checks['toxicity_score']['score']})")
            else:
                warnings.append("Potentially toxic content")
        
        # 7. Confidence scoring
        checks['confidence'] = self._calculate_confidence(response, context)
        
        # Final decision
        safe = not blocked
        
        if blocked:
            safe_response = "[Content blocked by security guardrails]"
            logger.warning(f"Response blocked - checks: {checks}")
        
        result = GuardrailResult(
            safe=safe,
            response=safe_response,
            blocked=blocked,
            warnings=warnings,
            security_checks=checks,
            asvs_compliance=list(set(asvs)),
            confidence_score=checks['confidence']['score'],
            timestamp=datetime.utcnow().isoformat()
        )
        
        logger.info(f"Validation complete - safe={safe}, blocked={blocked}, warnings={len(warnings)}")
        return result
    
    def _detect_injection(self, prompt: str) -> Dict[str, Any]:
        """Detect prompt injection attempts (ASVS V5.3.1)"""
        detected_patterns = []
        
        for pattern in self.INJECTION_PATTERNS:
            if re.search(pattern, prompt, re.IGNORECASE):
                detected_patterns.append(pattern)
        
        return {
            'detected': len(detected_patterns) > 0,
            'patterns': detected_patterns,
            'count': len(detected_patterns)
        }
    
    def _scan_xss(self, text: str) -> Dict[str, Any]:
        """Scan for XSS/script injection (ASVS V5.3.1)"""
        xss_patterns = [
            r'<script[^>]*>',
            r'javascript:',
            r'on\w+\s*=',
            r'<iframe[^>]*>',
            r'eval\s*\(',
        ]
        
        detected = []
        for pattern in xss_patterns:
            if re.search(pattern, text, re.IGNORECASE):
                detected.append(pattern)
        
        return {
            'detected': len(detected) > 0,
            'vectors': detected
        }
    
    def _detect_pii(self, text: str) -> Dict[str, Any]:
        """Detect PII in text (ASVS V14.4.1)"""
        detected_pii = {}
        
        for pii_type, pattern in self.PII_PATTERNS.items():
            matches = re.findall(pattern, text)
            if matches:
                detected_pii[pii_type] = len(matches)
        
        return {
            'detected': len(detected_pii) > 0,
            'types': detected_pii
        }
    
    def _mask_pii(self, text: str) -> str:
        """Redact PII from text"""
        masked = text
        
        # Email
        masked = re.sub(
            self.PII_PATTERNS['email'],
            '[EMAIL_REDACTED]',
            masked
        )
        
        # Phone
        masked = re.sub(
            self.PII_PATTERNS['phone'],
            '[PHONE_REDACTED]',
            masked
        )
        
        # SSN
        masked = re.sub(
            self.PII_PATTERNS['ssn'],
            '[SSN_REDACTED]',
            masked
        )
        
        # Credit card
        masked = re.sub(
            self.PII_PATTERNS['credit_card'],
            '[CARD_REDACTED]',
            masked
        )
        
        return masked
    
    def _scan_secrets(self, text: str) -> Dict[str, Any]:
        """Scan for leaked secrets (ASVS V14.4.1)"""
        detected_secrets = {}
        
        for secret_type, pattern in self.SECRET_PATTERNS.items():
            if re.search(pattern, text, re.IGNORECASE):
                detected_secrets[secret_type] = True
        
        return {
            'detected': len(detected_secrets) > 0,
            'types': list(detected_secrets.keys())
        }
    
    def _score_hallucination(self, response: str, 
                            context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Score likelihood of hallucination
        
        Returns score 0-1 (0=grounded, 1=likely hallucinated)
        """
        score = 0.0
        indicators = []
        
        # Check for uncertainty indicators
        for pattern in self.HALLUCINATION_INDICATORS:
            if re.search(pattern, response, re.IGNORECASE):
                score += 0.2
                indicators.append(pattern)
        
        # Check for context grounding (if context provided)
        if context and 'rag_docs' in context:
            # If RAG docs provided but response doesn't reference them
            if not any(doc_snippet in response for doc_snippet in context.get('rag_docs', [])):
                score += 0.3
                indicators.append('no_rag_grounding')
        
        # Cap at 1.0
        score = min(score, 1.0)
        
        return {
            'score': score,
            'indicators': indicators,
            'confidence': 1.0 - score
        }
    
    def _score_toxicity(self, text: str) -> Dict[str, Any]:
        """
        Score toxicity level
        
        Returns score 0-1 (0=safe, 1=toxic)
        
        Note: In production, use ML model like Perspective API
        This is a basic keyword-based approach
        """
        score = 0.0
        detected_categories = {}
        
        text_lower = text.lower()
        
        for category, keywords in self.TOXIC_KEYWORDS.items():
            category_score = 0
            detected_words = []
            
            for keyword in keywords:
                if keyword in text_lower:
                    category_score += 0.1
                    detected_words.append(keyword)
            
            if category_score > 0:
                detected_categories[category] = {
                    'score': min(category_score, 1.0),
                    'keywords': detected_words
                }
                score = max(score, category_score)
        
        return {
            'score': min(score, 1.0),
            'categories': detected_categories,
            'safe': score < self.toxicity_threshold
        }
    
    def _calculate_confidence(self, response: str,
                             context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Calculate confidence score for response
        
        Returns score 0-1 (0=no confidence, 1=high confidence)
        """
        confidence = 0.5  # Base confidence
        factors = {}
        
        # Factor 1: Response length (too short = low confidence)
        if len(response) < 50:
            confidence -= 0.2
            factors['length'] = 'too_short'
        elif len(response) > 500:
            confidence += 0.1
            factors['length'] = 'detailed'
        
        # Factor 2: Has specific examples/numbers
        if re.search(r'\d+', response):
            confidence += 0.1
            factors['specificity'] = 'has_numbers'
        
        # Factor 3: Context grounding (RAG)
        if context and context.get('rag_docs'):
            confidence += 0.2
            factors['grounding'] = 'rag_supported'
        
        # Factor 4: Uncertainty language
        uncertainty_words = ['maybe', 'perhaps', 'possibly', 'might', 'could be']
        uncertainty_count = sum(1 for word in uncertainty_words if word in response.lower())
        if uncertainty_count > 2:
            confidence -= 0.1 * uncertainty_count
            factors['uncertainty'] = f'{uncertainty_count}_indicators'
        
        # Cap between 0 and 1
        confidence = max(0.0, min(1.0, confidence))
        
        return {
            'score': confidence,
            'factors': factors
        }


# Convenience function
def validate_llm_output(prompt: str, response: str,
                       context: Optional[Dict] = None,
                       config: Optional[Dict] = None) -> GuardrailResult:
    """
    Quick validation function
    
    Example:
        result = validate_llm_output(
            prompt="What is AI?",
            response=llm_response,
            context={'rag_docs': [...]}
        )
        
        if not result.safe:
            raise SecurityError("Unsafe response")
    """
    guardrail = OutputGuardrail(config)
    return guardrail.validate_output(prompt, response, context)
