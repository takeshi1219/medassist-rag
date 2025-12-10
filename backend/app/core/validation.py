"""Input validation and sanitization for medical queries."""
import re
from typing import Optional, Tuple
from loguru import logger

from app.config import settings


class QueryValidator:
    """
    Validates and sanitizes medical queries for security and appropriateness.
    """
    
    # Patterns that might indicate injection attempts
    INJECTION_PATTERNS = [
        r"<script.*?>.*?</script>",  # XSS
        r"javascript:",
        r"on\w+\s*=",  # Event handlers
        r"{{.*?}}",  # Template injection
        r"\$\{.*?\}",  # Template literal injection
        r"exec\s*\(",
        r"eval\s*\(",
        r"__import__",
        r"subprocess",
        r"os\.system",
    ]
    
    # Patterns that might indicate prompt injection
    PROMPT_INJECTION_PATTERNS = [
        r"ignore\s+(previous|all|above)\s+(instructions?|prompts?)",
        r"disregard\s+(previous|all|your)\s+(instructions?|rules?)",
        r"forget\s+(everything|all|your)\s+(instructions?|training)",
        r"you\s+are\s+now\s+a",
        r"pretend\s+(you\s+are|to\s+be)",
        r"act\s+as\s+(if|a)",
        r"new\s+instructions?:",
        r"system\s*:\s*",
        r"\[SYSTEM\]",
        r"<\|im_start\|>",
    ]
    
    def __init__(self):
        """Compile regex patterns for efficiency."""
        self.injection_regex = [
            re.compile(p, re.IGNORECASE | re.DOTALL) 
            for p in self.INJECTION_PATTERNS
        ]
        self.prompt_injection_regex = [
            re.compile(p, re.IGNORECASE) 
            for p in self.PROMPT_INJECTION_PATTERNS
        ]
    
    def validate_query(self, query: str) -> Tuple[bool, Optional[str]]:
        """
        Validate a medical query.
        
        Args:
            query: The user's query string
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        # Check length
        if not query or not query.strip():
            return False, "Query cannot be empty"
        
        if len(query) > settings.max_query_length:
            return False, f"Query exceeds maximum length of {settings.max_query_length} characters"
        
        # Check for injection patterns
        for pattern in self.injection_regex:
            if pattern.search(query):
                logger.warning(f"Potential injection attempt detected in query")
                return False, "Query contains invalid characters or patterns"
        
        # Check for prompt injection
        for pattern in self.prompt_injection_regex:
            if pattern.search(query):
                logger.warning(f"Potential prompt injection attempt detected")
                return False, "Query contains invalid instructions"
        
        return True, None
    
    def sanitize_query(self, query: str) -> str:
        """
        Sanitize a query by removing potentially harmful content.
        
        Args:
            query: The user's query string
            
        Returns:
            Sanitized query string
        """
        # Strip whitespace
        sanitized = query.strip()
        
        # Remove null bytes
        sanitized = sanitized.replace("\x00", "")
        
        # Normalize whitespace
        sanitized = " ".join(sanitized.split())
        
        # Remove HTML tags (basic)
        sanitized = re.sub(r"<[^>]+>", "", sanitized)
        
        # Truncate if needed
        if len(sanitized) > settings.max_query_length:
            sanitized = sanitized[:settings.max_query_length]
        
        return sanitized


class PHIDetector:
    """
    Detects potential PHI (Protected Health Information) in queries.
    
    Used for logging and compliance purposes, not for blocking.
    """
    
    # Common PHI patterns
    PHI_PATTERNS = {
        "ssn": r"\b\d{3}-\d{2}-\d{4}\b",
        "phone": r"\b\d{3}[-.]?\d{3}[-.]?\d{4}\b",
        "email": r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b",
        "dob": r"\b(0[1-9]|1[0-2])[-/](0[1-9]|[12]\d|3[01])[-/](19|20)\d{2}\b",
        "mrn": r"\b(MRN|mrn|Medical Record)[:#]?\s*\d{6,}\b",
        "npi": r"\b\d{10}\b",  # NPI numbers
    }
    
    def __init__(self):
        """Compile regex patterns."""
        self.patterns = {
            name: re.compile(pattern, re.IGNORECASE)
            for name, pattern in self.PHI_PATTERNS.items()
        }
    
    def detect_phi(self, text: str) -> dict:
        """
        Detect potential PHI in text.
        
        Args:
            text: Text to scan
            
        Returns:
            Dict of detected PHI types and their counts
        """
        detected = {}
        
        for phi_type, pattern in self.patterns.items():
            matches = pattern.findall(text)
            if matches:
                detected[phi_type] = len(matches)
        
        if detected:
            logger.warning(f"Potential PHI detected in query: {list(detected.keys())}")
        
        return detected
    
    def contains_phi(self, text: str) -> bool:
        """Check if text contains any potential PHI."""
        return bool(self.detect_phi(text))


# Singleton instances
query_validator = QueryValidator()
phi_detector = PHIDetector()


def validate_and_sanitize(query: str) -> Tuple[str, bool, Optional[str]]:
    """
    Convenience function to validate and sanitize a query.
    
    Args:
        query: The user's query string
        
    Returns:
        Tuple of (sanitized_query, is_valid, error_message)
    """
    # First sanitize
    sanitized = query_validator.sanitize_query(query)
    
    # Then validate
    is_valid, error = query_validator.validate_query(sanitized)
    
    # Check for PHI (for logging, not blocking)
    if is_valid:
        phi_detector.detect_phi(sanitized)
    
    return sanitized, is_valid, error

