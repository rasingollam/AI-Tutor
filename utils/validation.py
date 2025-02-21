import json
from typing import Dict

def validate_json_structure(data: Dict, required_keys: list) -> bool:
    """Validate JSON structure contains required keys."""
    return all(key in data for key in required_keys)

def safe_json_loads(json_str: str) -> Dict:
    """Safely parse JSON with error handling."""
    try:
        return json.loads(json_str)
    except json.JSONDecodeError:
        return {
            "error": "Invalid JSON format",
            "original_content": json_str
        }
