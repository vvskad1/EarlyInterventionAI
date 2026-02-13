"""
Utility functions for JSON repair and other helpers.
"""
import json
import re
from typing import Dict, Any


def extract_or_repair_json(text: str) -> Dict[str, Any]:
    """
    Attempt to extract or repair JSON from potentially malformed text.
    
    Strategy:
    1. Try direct JSON parsing
    2. Extract last {...} block with regex
    3. Final fallback: return empty structure with expected keys
    
    Args:
        text: Raw text that should contain JSON
        
    Returns:
        Parsed dictionary with at least the expected structure
    """
    # Strategy 1: Direct parse
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        pass
    
    # Strategy 2: Extract last JSON object using regex
    # Look for the last occurrence of {...} in the text
    json_pattern = r'\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\}'
    matches = list(re.finditer(json_pattern, text, re.DOTALL))
    
    if matches:
        # Try parsing from last to first match
        for match in reversed(matches):
            try:
                json_str = match.group(0)
                return json.loads(json_str)
            except json.JSONDecodeError:
                continue
    
    # Strategy 3: Try to find JSON-like content with quotes
    # This handles cases where JSON is embedded in markdown or other text
    json_block_pattern = r'```(?:json)?\s*(\{.*?\})\s*```'
    json_blocks = re.findall(json_block_pattern, text, re.DOTALL)
    
    for block in json_blocks:
        try:
            return json.loads(block)
        except json.JSONDecodeError:
            continue
    
    # Strategy 4: Final fallback - return minimal valid structure
    # Try to extract any text that looks like it could be values
    fallback = {
        "Goals": "",
        "Strategies": "",
        "Advice for Parents": ""
    }
    
    # Try to extract some content from the text if it exists
    if text.strip():
        # If text contains any of the expected keys, try to extract content
        for key in ["Goals", "Strategies", "Advice for Parents"]:
            # Look for patterns like "Goals: some text" or "Goals": "some text"
            pattern = rf'{key}["\s:]+([^,\}}]+)'
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                value = match.group(1).strip().strip('"').strip("'")
                fallback[key] = value
    
    return fallback


def ensure_json_keys(data: Dict[str, Any], required_keys: list) -> Dict[str, Any]:
    """
    Ensure a dictionary contains all required keys, adding empty strings if missing.
    
    Args:
        data: Dictionary to validate
        required_keys: List of required key names
        
    Returns:
        Dictionary with all required keys present
    """
    for key in required_keys:
        if key not in data:
            data[key] = ""
    return data
