"""
Secure validation utilities for generative agents.
Provides safe parsing and validation for API responses.
"""
import ast
import json
import re
from typing import Any, List, Dict, Union, Optional
from logger_config import get_logger, log_security_event

logger = get_logger('validation')

def safe_literal_eval(expression: str, allowed_types: tuple = (dict, list, tuple, str, int, float, bool)) -> Any:
    """
    Safely evaluate a literal expression with type restrictions.
    
    Args:
        expression: String expression to evaluate
        allowed_types: Tuple of allowed return types
        
    Returns:
        Evaluated expression if safe, None otherwise
        
    Raises:
        ValueError: If expression is unsafe or invalid type
    """
    try:
        # First, basic security checks
        if not isinstance(expression, str):
            raise ValueError("Expression must be a string")
        
        if len(expression) > 10000:  # Prevent DOS attacks
            log_security_event("LARGE_EXPRESSION", f"Expression too large: {len(expression)} chars")
            raise ValueError("Expression too large")
        
        # Check for suspicious patterns
        suspicious_patterns = [
            r'__.*__',  # Dunder methods
            r'import\s+',  # Import statements
            r'exec\s*\(',  # Exec calls
            r'eval\s*\(',  # Eval calls
            r'open\s*\(',  # File operations
            r'subprocess',  # Subprocess calls
            r'os\.',  # OS module calls
        ]
        
        for pattern in suspicious_patterns:
            if re.search(pattern, expression, re.IGNORECASE):
                log_security_event("SUSPICIOUS_EXPRESSION", f"Pattern {pattern} found in: {expression[:100]}...")
                raise ValueError(f"Suspicious pattern detected: {pattern}")
        
        # Use ast.literal_eval which is safer than eval
        result = ast.literal_eval(expression)
        
        # Validate return type
        if not isinstance(result, allowed_types):
            raise ValueError(f"Result type {type(result)} not in allowed types {allowed_types}")
        
        logger.debug(f"Successfully evaluated expression of type {type(result)}")
        return result
        
    except (ValueError, SyntaxError, TypeError) as e:
        logger.warning(f"Failed to evaluate expression: {str(e)}")
        log_security_event("EVAL_FAILURE", f"Expression: {expression[:100]}..., Error: {str(e)}")
        return None

def safe_json_parse(json_string: str, max_depth: int = 10) -> Optional[Dict]:
    """
    Safely parse JSON with depth and size limits.
    
    Args:
        json_string: JSON string to parse
        max_depth: Maximum nesting depth allowed
        
    Returns:
        Parsed JSON as dict if valid, None otherwise
    """
    try:
        if not isinstance(json_string, str):
            return None
            
        if len(json_string) > 50000:  # Prevent DOS attacks
            log_security_event("LARGE_JSON", f"JSON too large: {len(json_string)} chars")
            return None
        
        # Parse JSON
        result = json.loads(json_string)
        
        # Check depth
        def check_depth(obj, current_depth=0):
            if current_depth > max_depth:
                raise ValueError(f"JSON depth exceeds maximum of {max_depth}")
            
            if isinstance(obj, dict):
                for value in obj.values():
                    check_depth(value, current_depth + 1)
            elif isinstance(obj, list):
                for item in obj:
                    check_depth(item, current_depth + 1)
        
        check_depth(result)
        logger.debug(f"Successfully parsed JSON with {len(str(result))} characters")
        return result
        
    except (json.JSONDecodeError, ValueError) as e:
        logger.warning(f"Failed to parse JSON: {str(e)}")
        log_security_event("JSON_PARSE_FAILURE", f"JSON: {json_string[:100]}..., Error: {str(e)}")
        return None

def validate_gpt_response(response: str, expected_format: str = "string") -> bool:
    """
    Validate GPT response format and content.
    
    Args:
        response: GPT response string
        expected_format: Expected format (string, json, list)
        
    Returns:
        True if response is valid, False otherwise
    """
    try:
        if not isinstance(response, str):
            return False
        
        if len(response.strip()) == 0:
            return False
        
        # Check for obvious errors
        error_indicators = [
            "error", "failed", "exception", "traceback",
            "chatgpt error", "api error", "rate limit"
        ]
        
        response_lower = response.lower()
        for indicator in error_indicators:
            if indicator in response_lower:
                log_security_event("GPT_ERROR_RESPONSE", f"Error indicator '{indicator}' in response")
                return False
        
        # Format-specific validation
        if expected_format == "json":
            return safe_json_parse(response) is not None
        elif expected_format == "list":
            return safe_literal_eval(response, (list, tuple)) is not None
        elif expected_format == "string":
            return len(response.strip()) > 0
        
        return True
        
    except Exception as e:
        logger.error(f"Error validating GPT response: {str(e)}")
        return False

def sanitize_input(text: str, max_length: int = 1000) -> str:
    """
    Sanitize user input to prevent injection attacks.
    
    Args:
        text: Input text to sanitize
        max_length: Maximum allowed length
        
    Returns:
        Sanitized text
    """
    if not isinstance(text, str):
        return ""
    
    # Truncate if too long
    if len(text) > max_length:
        text = text[:max_length]
        logger.warning(f"Input truncated to {max_length} characters")
    
    # Remove or escape dangerous characters
    # Keep alphanumeric, spaces, and common punctuation
    sanitized = re.sub(r'[^\w\s\.,\-\(\)\[\]\'\"!?:;]', '', text)
    
    return sanitized.strip()

def validate_persona_name(name: str) -> bool:
    """Validate persona name format."""
    if not isinstance(name, str) or len(name.strip()) == 0:
        return False
    
    # Allow letters, spaces, hyphens, apostrophes
    pattern = r'^[a-zA-Z\s\-\']{1,50}$'
    return bool(re.match(pattern, name.strip()))

def validate_file_path(path: str, allowed_extensions: List[str] = None) -> bool:
    """Validate file path for security."""
    if not isinstance(path, str):
        return False
    
    # Check for path traversal attempts
    if '..' in path or path.startswith('/'):
        log_security_event("PATH_TRAVERSAL", f"Suspicious path: {path}")
        return False
    
    # Check allowed extensions
    if allowed_extensions:
        extension = path.split('.')[-1].lower()
        if extension not in allowed_extensions:
            return False
    
    return True