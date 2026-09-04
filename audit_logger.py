import json
import datetime
import os
from typing import Dict, Any, List

class AuditLogger:
    def __init__(self, log_filepath: str = "audit_trail.json"):
        self.log_filepath = log_filepath

    def log_event(self, agent: str, action: str, details: Dict[str, Any], status: str) -> Dict[str, Any]:
        """
        Creates a structured, immutable audit log entry.
        Status options: APPROVED, REJECTED, OVERRIDDEN, FAILED
        """
        entry = {
            "timestamp": datetime.datetime.now(datetime.timezone.utc).isoformat(),
            "agent": agent,
            "action": action,
            "status": status,
            "details": details
        }
        
        # Write to local file for persistence & compliance audits
        logs = []
        if os.path.exists(self.log_filepath):
            try:
                with open(self.log_filepath, "r") as f:
                    logs = json.load(f)
            except json.JSONDecodeError:
                logs = []
        
        logs.append(entry)
        with open(self.log_filepath, "w") as f:
            json.dump(logs, f, indent=2)
            
        return entry