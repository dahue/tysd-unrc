import random
import socket
from contextlib import closing

import pytest


def _free_port_block(n: int) -> int:
    """Find n consecutive free TCP ports and return the base."""
    for _ in range(100):
        base = 20000 + random.randint(0, 8000)
        if all(_can_bind(base + i) for i in range(n)):
            return base
    raise RuntimeError("could not find a free port block")


def _can_bind(port: int) -> bool:
    try:
        with closing(socket.socket(socket.AF_INET, socket.SOCK_STREAM)) as s:
            s.bind(("127.0.0.1", port))
            return True
    except OSError:
        return False


@pytest.fixture
def base_port(monkeypatch):
    """
    Unique BASE_PORT for each test so workers bind to free addresses.
    Patches the names imported into worker (from config).
    """
    base = _free_port_block(3)
    monkeypatch.setattr("worker.BASE_PORT", base)
    monkeypatch.setattr("worker.BASE_ADDRESS", "tcp://127.0.0.1")
    return base
