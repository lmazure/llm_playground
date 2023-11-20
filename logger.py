import datetime
from logEntry import LogEntry

class Logger:

    def __init__(self):
        self._logs = []

    def log(self, type, message):
        timestamp = datetime.datetime.now()
        self._logs.append(LogEntry(type, timestamp, message))

    def lastLogIndex(self):
        return len(self._logs) - 1
    
    def logs(self, indexFirst, indexLast):
        print(self._logs[indexFirst:indexLast+1])
        return [ log.dto() for log in self._logs[indexFirst:indexLast+1]]
    