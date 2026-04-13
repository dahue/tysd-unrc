from message import Message


def test_serialize_round_trip():
    m = Message(message="hello", timestamp=7, sender_id=2)
    raw = m.serialize()
    m2 = Message.deserialize(raw)
    assert m2.message == "hello"
    assert m2.timestamp == 7
    assert m2.sender_id == 2
    assert m2.msg_type == Message.DATA


def test_sentinel_round_trip():
    m = Message(timestamp=3, sender_id=1, msg_type=Message.SENTINEL)
    m2 = Message.deserialize(m.serialize())
    assert m2.msg_type == Message.SENTINEL
    assert m2.timestamp == 3
    assert m2.message == ""


def test_distinct_messages_differ():
    a = Message(message="a", timestamp=1, sender_id=0).serialize()
    b = Message(message="b", timestamp=1, sender_id=0).serialize()
    assert a != b
