"""
HTTP Submission Tool with retry and submission tracking.
"""

import requests
import json
import time
from typing import Dict, Any, Optional

_submission_history = []

def reset_submission_tracking():
    """Reset submission history."""
    global _submission_history
    _submission_history.clear()

def post_request(url: str, payload: Dict[str, Any], headers: Optional[Dict[str, str]] = None) -> Dict[str, Any]:
    """
    Submit answers to target endpoint with timing and verification.
    """
    if headers is None:
        headers = {"Content-Type": "application/json"}
    
    start_time = time.time()
    try:
        response = requests.post(url, json=payload, headers=headers, timeout=30)
        elapsed = round(time.time() - start_time, 2)
        
        try:
            data = response.json()
        except Exception:
            data = {"text": response.text}
            
        result = {
            "status_code": response.status_code,
            "response": data,
            "elapsed_seconds": elapsed
        }
        _submission_history.append({"url": url, "payload": payload, "result": result})
        return result
    except Exception as e:
        return {
            "status_code": 500,
            "error": str(e),
            "elapsed_seconds": round(time.time() - start_time, 2)
        }
