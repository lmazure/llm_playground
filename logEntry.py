class LogEntry:

    def __init__(self, type, timestamp, message):
        self._type = type
        self._timestamp = timestamp
        self._message = message
    
    def dto(self):
        return { 'type': self._type, 'timestamp': self._timestamp.isoformat(), 'message': self._message }
