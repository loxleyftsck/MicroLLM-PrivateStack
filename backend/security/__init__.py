# -*- coding: utf-8 -*-
"""
Security module for MicroLLM-PrivateStack

Provides enterprise-grade security validators and guardrails:
- Data ingestion validation (OWASP ASVS V5.1, V5.2, V8.3)
- LLM output guardrails (OWASP ASVS V5.3, V14.4)

OWASP ASVS Level 2 Compliance:
- V5.1.1: Input validation whitelist
- V5.2.1: Content sanitization
- V5.2.8: Malware scanning
- V5.3.1: Output encoding & validation
- V8.3.4: Encryption at rest
- V14.4.1: Sensitive data protection
"""

from .validators import (
    DataIngestionValidator,
    ValidationError,
    SecurityError as ValidatorSecurityError,
    validate_file_upload
)

from .guardrails import (
    OutputGuardrail,
    GuardrailResult,
    SecurityError as GuardrailSecurityError,
    validate_llm_output
)

__version__ = '1.1.0'
__all__ = [
    'DataIngestionValidator',
    'OutputGuardrail',
    'ValidationError',
    'ValidatorSecurityError',
    'GuardrailSecurityError',
    'GuardrailResult',
    'validate_file_upload',
    'validate_llm_output',
]
