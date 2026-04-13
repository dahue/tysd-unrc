import asyncio
import json
import multiprocessing
from multiprocessing import Queue

from worker import Worker

N_WORKERS = 3
N_MESSAGES = 10


def run_worker(worker_id: int, messages: list[str], total_messages: int, result_queue: Queue):
    worker = Worker(worker_id, messages, total_messages, n_workers=N_WORKERS)
    delivered = asyncio.run(worker.start_broadcast())
    messages = [json.loads(r)["message"] for r in delivered]
    result_queue.put((worker_id, messages))


def main():
    messages = [f"msg_{i}" for i in range(N_MESSAGES)]
    partitions = [messages[i::N_WORKERS] for i in range(N_WORKERS)]
    print(partitions)
    total = len(messages)

    result_queue =Queue()
    processes = [
        multiprocessing.Process(
            target=run_worker,
            args=(pid, partition, total, result_queue),
        )
        for pid, partition in enumerate(partitions)
    ]
    for p in processes:
        p.start()
    for p in processes:
        p.join()

    results = {}
    for _ in range(N_WORKERS):
        pid, messages = result_queue.get()
        results[pid] = messages

    print(json.dumps(results, indent=2))
    all_same = len(set(tuple(v) for v in results.values())) == 1
    print(f"All workers agree on order: {all_same}")


if __name__ == "__main__":
    main()
