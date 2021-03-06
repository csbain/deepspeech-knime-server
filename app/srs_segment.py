class SRSegment:
    order = None
    timestamp = None
    duration = None
    path = None
    content = None
    emotion = {
        "neutrality": None,
        "happiness": None,
        "sadness": None,
        "anger": None,
        "fear": None,
    }
    start_time = None
    end_time = None
    exception = None

    def __init__(self, order, timestamp, duration, path):
        self.order = order
        self.timestamp = timestamp
        self.duration = duration
        self.path = path

    def get_dict_obj(self):
        return {
            "order": self.order,
            "timestamp": self.timestamp,
            "duration": self.duration,
            "content": self.content,
            "emotion_neutrality": self.emotion['neutrality'],
            "emotion_happiness": self.emotion['happiness'],
            "emotion_sadness": self.emotion['sadness'],
            "emotion_anger": self.emotion['anger'],
            "emotion_fear": self.emotion['fear'],
            "start_time": self.start_time,
            "end_time": self.end_time,
            "exception": self.exception
        }
