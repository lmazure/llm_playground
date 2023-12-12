import datetime
from typing import Dict

class LogEntry:

    def __init__(self, type: str, timestamp: datetime, message: str) -> None:
        self._type = type
        self._timestamp = timestamp
        self._message = message
    
    def dto(self) -> Dict[str, str]:
        return { 'type': self._type,
                 'timestamp': self._timestamp.isoformat(),
                 'message': self._message
               }
