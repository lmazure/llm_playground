class LogEntry:

    def __init__(self, type, timestamp, message):
        self._type = type
        self._timestamp = timestamp
        self._message = message

    def type(self):
        return self._type
    
    def timestamp(self):
        return self._timestamp
    
    def message(self):
        return self._message
    
    def dto(self):
        return { 'type': self._type, 'timestamp': self._timestamp.isoformat(), 'message': self._message }
