import asyncio
import random
import zmq
import zmq.asyncio
from message import Message
from config import PUSH_PULL_SOCKET, PUB_SUB_SOCKET

class Worker:
    def __init__(self, id: int, messages: list[str], total_messages: int):
        self.id = id
        self.messages = messages
        self.total_messages = total_messages
        self.context = zmq.asyncio.Context()
        self.socket_sender = self.context.socket(zmq.PUSH)
        self.socket_sender.connect(PUSH_PULL_SOCKET)
        self.socket_receiver = self.context.socket(zmq.SUB)
        self.socket_receiver.setsockopt(zmq.SUBSCRIBE, b"")
        self.socket_receiver.connect(PUB_SUB_SOCKET)
        self.received = []

    async def broadcast(self, msg: bytes):
        await self.socket_sender.send(msg)

    async def receiver(self, total_messages: int):
        while len(self.received) < total_messages:
            raw = await self.socket_receiver.recv()
            self.received.append(raw.decode("utf-8"))

    async def start_broadcast(self):
        try:
            print(f"Starting receiver in process {self.id}...")
            receiver_task = asyncio.create_task(self.receiver(self.total_messages))
            await asyncio.sleep(5)
            print(f"Receiver in process {self.id} started")
            
            print(f"Process {self.id} broadcasting messages...")
            for message in self.messages:
                await asyncio.sleep(random.uniform(0.0, 0.5))
                await self.broadcast(Message(text=message).serialize())

            await receiver_task
        finally:
            self.socket_receiver.close(linger=0)
            self.socket_sender.close(linger=0)
            self.context.term()
        return self.received


async def main():
    worker = Worker(0, ["test_msg_0", "test_msg_1", "test_msg_2"], 3)
    received = await worker.start_broadcast()
    print(f'Received messages in process {worker.id}: {received}')

if __name__ == "__main__":
    asyncio.run(main())