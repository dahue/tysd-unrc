import asyncio
import zmq
import zmq.asyncio
from config import PUSH_PULL_SOCKET, PUB_SUB_SOCKET

class Sequencer:
    def __init__(self):
        self.context = zmq.asyncio.Context()
        self.socket_receiver = self.context.socket(zmq.PULL)
        self.socket_receiver.bind(PUSH_PULL_SOCKET)
        self.socket_broadcast = self.context.socket(zmq.PUB)
        self.socket_broadcast.bind(PUB_SUB_SOCKET)

    async def run(self):
        print("Sequencer running...")
        while True:
            message = await self.socket_receiver.recv()
            print("Received message: %s" % message.decode("utf-8"))
            await self.socket_broadcast.send(message)


async def main():
    sequencer = Sequencer()
    await sequencer.run()

if __name__ == "__main__":
    asyncio.run(main())