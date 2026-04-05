import zmq
from message import Message

class Worker:
    def __init__(self, id: int):
        self.id = id

    async def broadcast(self, msg: Message):
        serialized_msg = msg.serialize()
        context = zmq.Context()

        # Socket to talk to Sequencer (PUSH/PULL)
        socket_sender = context.socket(zmq.PUSH)
        socket_sender.connect("tcp://localhost:5555")
        socket_sender.send(serialized_msg)

        # Socket to listen to Sequencer broadcast (SUB)
        socket_receiver = context.socket(zmq.SUB)
        socket_receiver.setsockopt(zmq.SUBSCRIBE, b"")
        socket_receiver.connect("tcp://localhost:5556")
        response = socket_receiver.recv().decode('utf-8')
        # print(f"Process {self.id} received response: {response}")
        return response
