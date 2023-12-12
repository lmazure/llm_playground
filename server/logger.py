import datetime
from logEntry import LogEntry
from typing import Dict, List

class Logger:

    def __init__(self) -> None:
        self._logs = []

    def log(self, type: str, message: str) -> None:
        timestamp = datetime.datetime.now()
        self._logs.append(LogEntry(type, timestamp, message))

    def lastLogIndex(self) -> None:
        return len(self._logs) - 1
    
    def logs(self, indexFirst: int, indexLast: int) -> List[Dict[str, str]]:
        return [ log.dto() for log in self._logs[indexFirst:indexLast+1]]
