import asyncio
import json
import multiprocessing
from multiprocessing import Queue
from worker import Worker
N_WORKERS = 3
WORKER_RESPONSES = {}


def broadcast_all(process_id: int, messages: list[str], total_messages: int, result_queue: Queue):
    worker = Worker(process_id, messages, total_messages)
    received = asyncio.run(worker.start_broadcast())
    responses = [json.loads(r)["text"] for r in received]
    result_queue.put((process_id, responses))

def main():
    print("Starting main...")
    messages = [f"msg_{i}" for i in range(10)]

    print(f"{messages}")

    messages_partitions = [messages[process_id::N_WORKERS] for process_id in range(N_WORKERS)]
    total = len(messages)

    result_queue = Queue()
    processes = [
        multiprocessing.Process(
            target=broadcast_all,
            args=(process_id, messages_partition, total, result_queue),
        )
        for process_id, messages_partition in enumerate(messages_partitions)
    ]
    for p in processes:
        p.start()
    for p in processes:
        p.join()

    for _ in range(N_WORKERS):
        process_id, responses = result_queue.get()
        WORKER_RESPONSES[process_id] = responses

    print(f"Worker responses: {json.dumps(WORKER_RESPONSES, indent=2)}")


if __name__ == "__main__":
    main()
