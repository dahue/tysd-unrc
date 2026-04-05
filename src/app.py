import asyncio
import json
import multiprocessing
from multiprocessing import Queue
from worker import Worker
from message import Message

N_WORKERS = 3
WORKER_RESPONSES = {}


async def broadcast_all(process_id: int, messages: list[str]):
    worker = Worker(process_id)
    responses: list[str] = []
    for text in messages:
        response = await worker.broadcast(Message(text=text))
        responses.append(json.loads(response)["text"])
    return responses


def worker_process_main(process_id: int, messages: list[str], result_queue: Queue):
    responses = asyncio.run(broadcast_all(process_id, messages))
    result_queue.put((process_id, responses))


async def main():
    print("Starting main...")
    messages = [f"msg_{i}" for i in range(10)]

    print(f"{messages}")

    chunks = [messages[process_id::N_WORKERS] for process_id in range(N_WORKERS)]

    result_queue = Queue()
    processes = [
        multiprocessing.Process(
            target=worker_process_main,
            args=(process_id, chunk, result_queue),
        )
        for process_id, chunk in enumerate(chunks)
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
    asyncio.run(main())
