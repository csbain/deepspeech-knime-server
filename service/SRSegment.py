
class SRSegment(object):
    order = None
    timestamp = None
    duration = None
    path = None
    content = None
    emotion = {
        "neutrality":None,
        "happiness":None,
        "sadness":None,
        "anger":None,
        "fear":None
    }

    def __init__(self, order, timestamp, duration, path):
        self.order = order
        self.timestamp = timestamp
        self.duration = duration
        self.path = path

    def get_dict_obj(self):
        return {
            "order":self.order,
            "timestamp":self.timestamp,
            "duration":self.duration,
            "content":self.content,
            "emotion":self.emotion
        }