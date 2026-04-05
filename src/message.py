import json

class Message:
    def __init__(self, text: str):
        self.text = text

    def __str__(self):
        return json.dumps({
            "text": self.text
        })

    def serialize(self):
        return self.__str__().encode('utf-8')
