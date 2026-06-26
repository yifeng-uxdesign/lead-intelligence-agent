"""Queue for cross-layer handoff tasks."""

from __future__ import annotations

from collections import deque
from dataclasses import dataclass
from typing import Any, Deque, Dict, Optional


@dataclass
class HandoffTask:
    """Represents one task to transfer between agent layers."""

    lead_id: str
    source_layer: str
    target_layer: str
    payload: Dict[str, Any]


class HandoffQueue:
    """FIFO queue that buffers handoff tasks."""

    def __init__(self) -> None:
        self._queue: Deque[HandoffTask] = deque()

    def enqueue(self, task: HandoffTask) -> None:
        self._queue.append(task)

    def dequeue(self) -> Optional[HandoffTask]:
        if not self._queue:
            return None
        return self._queue.popleft()

    def size(self) -> int:
        return len(self._queue)
        # TODO: Add priority and retry semantics for failed handoffs.
