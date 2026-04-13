import json


class Message:
    DATA = "data"
    SENTINEL = "sentinel"

    def __init__(self, message: str = "", timestamp: int = 0, sender_id: int = 0, msg_type: str = DATA):
        self.message = message
        self.timestamp = timestamp
        self.sender_id = sender_id
        self.msg_type = msg_type

    def serialize(self) -> bytes:
        return json.dumps({
            "message": self.message,
            "timestamp": self.timestamp,
            "sender_id": self.sender_id,
            "msg_type": self.msg_type,
        }).encode("utf-8")

    @classmethod
    def deserialize(cls, raw: bytes) -> "Message":
        d = json.loads(raw.decode("utf-8"))
        return cls(
            message=d.get("message", ""),
            timestamp=d["timestamp"],
            sender_id=d["sender_id"],
            msg_type=d.get("msg_type", d.get("type", cls.DATA)),
        )

    def __str__(self) -> str:
        return self.serialize().decode("utf-8")
