import asyncio
import heapq
import json

import zmq
import zmq.asyncio

from message import Message
from config import BASE_ADDRESS, BASE_PORT


class Worker:
    def __init__(self, worker_id: int, messages: list[str], total_messages: int, n_workers: int):
        self.id = worker_id
        self.messages = messages
        self.total_messages = total_messages
        self.n_workers = n_workers

        # Timestamp state
        self.timestamp: int = 0
        self.workers_last_timestamp = [0] * n_workers  # last received timestamp per worker

        # Delivery buffer: priority queue of (timestamp, worker_id, message)
        self.priority_queue = [] # priority queue of messages to deliver
        self.delivered = []

        # ZMQ setup
        self.context = zmq.asyncio.Context()

        self.pub = self.context.socket(zmq.PUB)
        self.pub.bind(f"{BASE_ADDRESS}:{BASE_PORT + worker_id}")

        self.sub = self.context.socket(zmq.SUB)
        self.sub.setsockopt(zmq.SUBSCRIBE, b"")
        for i in range(n_workers):
            self.sub.connect(f"{BASE_ADDRESS}:{BASE_PORT + i}")


    def _send_event(self) -> int:
        """Increment clock for a local send event; return the new clock."""
        self.timestamp += 1
        return self.timestamp

    def _recv_event(self, incoming: int) -> None:
        """Update clock on receive: clock = max(local, incoming) + 1."""
        self.timestamp = max(self.timestamp, incoming) + 1


    def _try_deliver(self) -> None:
        """Deliver every stable message at the head of the priority queue."""
        while self.priority_queue:
            timestamp, _, raw = self.priority_queue[0] # (timestamp, pid, message)
            # A message is stable when every worker has sent at least one
            # message with timestamp >= this message's timestamp.
            if min(self.workers_last_timestamp) >= timestamp:
                heapq.heappop(self.priority_queue)
                self.delivered.append(raw)
            else:
                break


    async def receiver(self) -> None:
        """Receive until all DATA broadcasts and one SENTINEL per peer are seen."""
        data_received = 0
        sentinels_received = 0

        while data_received < self.total_messages or sentinels_received < self.n_workers:
            raw = await self.sub.recv()
            msg = Message.deserialize(raw)

            self._recv_event(msg.timestamp)
            self.workers_last_timestamp[msg.sender_id] = max(
                self.workers_last_timestamp[msg.sender_id], msg.timestamp
            )

            if msg.msg_type == Message.DATA:
                heapq.heappush(self.priority_queue, (msg.timestamp, msg.sender_id, raw))
                data_received += 1
            else:
                sentinels_received += 1

            self._try_deliver()


    async def start_broadcast(self) -> list[bytes]:
        recv_task = asyncio.create_task(self.receiver())

        await asyncio.sleep(1)

        for message in self.messages:
            ts = self._send_event()
            msg = Message(
                message=message,
                timestamp=ts,
                sender_id=self.id,
                msg_type=Message.DATA,
            )
            await self.pub.send(msg.serialize())

        ts = self._send_event()
        sentinel = Message(
            timestamp=ts,
            sender_id=self.id,
            msg_type=Message.SENTINEL,
        )
        await self.pub.send(sentinel.serialize())

        await recv_task

        self.pub.close(linger=0)
        self.sub.close(linger=0)
        self.context.term()

        return self.delivered

async def main():
    pid = 0
    messages = ["test_msg_0", "test_msg_1", "test_msg_2"]
    n_workers = 1
    worker = Worker(pid, messages, len(messages), n_workers)
    delivered = await worker.start_broadcast()
    result = [Message.deserialize(r) for r in delivered]
    rows = [
        {
            "message": m.message,
            "timestamp": m.timestamp,
            "sender_id": m.sender_id,
            "msg_type": m.msg_type,
        }
        for m in result
    ]
    print(f'Received messages in process {pid}: {json.dumps(rows, indent=2)}')

if __name__ == "__main__":
    asyncio.run(main())