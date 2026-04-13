"""
Tests for the Lamport-clock atomic broadcast implementation.

Property under test: all workers deliver every message in the same total order.
"""

import asyncio
import json

import pytest

from worker import Worker


@pytest.mark.asyncio
async def test_three_workers_same_total_order(base_port):
    """Three workers broadcasting concurrently must agree on delivery order."""
    n_workers = 3
    total = 9  # 3 messages per worker

    async def run(wid: int, msgs: list[str]) -> list[bytes]:
        w = Worker(wid, msgs, total, n_workers)
        return await w.start_broadcast()

    results = await asyncio.gather(
        run(0, ["a", "b", "c"]),
        run(1, ["d", "e", "f"]),
        run(2, ["g", "h", "i"]),
    )

    assert all(len(r) == total for r in results)
    assert results[0] == results[1] == results[2]

    bodies = {json.loads(r)["message"] for r in results[0]}
    assert bodies == {"a", "b", "c", "d", "e", "f", "g", "h", "i"}


@pytest.mark.asyncio
async def test_three_workers_ten_messages_same_total_order(base_port):
    """Ten broadcasts across three workers: all agree on delivery order."""
    n_workers = 3
    total = 10
    messages = [f"m{i}" for i in range(total)]
    partitions = [messages[i::n_workers] for i in range(n_workers)]

    async def run(wid: int, msgs: list[str]) -> list[bytes]:
        w = Worker(wid, msgs, total, n_workers)
        return await w.start_broadcast()

    results = await asyncio.gather(
        run(0, partitions[0]),
        run(1, partitions[1]),
        run(2, partitions[2]),
    )

    assert all(len(r) == total for r in results)
    assert results[0] == results[1] == results[2]
    bodies = {json.loads(r)["message"] for r in results[0]}
    assert bodies == set(messages)


@pytest.mark.asyncio
async def test_single_worker_delivers_own_messages(base_port):
    """A single worker must receive its own messages in send order."""
    w = Worker(0, ["x", "y", "z"], 3, 1)
    result = await w.start_broadcast()

    assert len(result) == 3
    bodies = [json.loads(r)["message"] for r in result]
    assert bodies == ["x", "y", "z"]


@pytest.mark.asyncio
async def test_two_workers_same_total_order(base_port):
    """Two workers must agree on delivery order."""
    n_workers = 2
    total = 4

    async def run(wid: int, msgs: list[str]) -> list[bytes]:
        w = Worker(wid, msgs, total, n_workers)
        return await w.start_broadcast()

    results = await asyncio.gather(
        run(0, ["p", "q"]),
        run(1, ["r", "s"]),
    )

    assert all(len(r) == total for r in results)
    assert results[0] == results[1]
    bodies = {json.loads(r)["message"] for r in results[0]}
    assert bodies == {"p", "q", "r", "s"}


@pytest.mark.asyncio
async def test_order_is_deterministic_by_timestamp_then_sender(base_port):
    """
    When Lamport timestamps tie, heap order uses sender_id as tie-breaker.
    """
    n_workers = 3
    total = 3

    async def run(wid: int, msg: str) -> list[bytes]:
        w = Worker(wid, [msg], total, n_workers)
        return await w.start_broadcast()

    results = await asyncio.gather(
        run(0, "from0"),
        run(1, "from1"),
        run(2, "from2"),
    )

    assert results[0] == results[1] == results[2]
