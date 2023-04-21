import asyncio
# from inspect import Traceback
# from typing import Any, AsyncGenerator
from asyncio.tasks import Task


class TaskPoolExecutor:
    def __init__(self, max_rate: int):
        self.max_rate = max_rate

        self.is_running = False

        self._queue = asyncio.Queue()
        self._scheduler_task: asyncio.Task | None = None
        self._sem = asyncio.Semaphore(max_rate)
        self._stop_event = asyncio.Event()

    async def _worker(self, task: Task):
        async with self._sem:
            await task
        self._queue.task_done()

        if not self.is_running and not self.locked():
            self._stop_event.set()

    def locked(self):
        return self._sem.locked()

    async def _scheduler(self):
        while self.is_running:
            for _ in range(self.max_rate):
                async with self._sem:
                    task = await self._queue.get()
                asyncio.create_task(self._worker(asyncio.create_task(task)))
            await asyncio.sleep(0)

    async def put(self, task: Task):
        async with self._sem:
            await self._queue.put(task)

    def start(self):
        self.is_running = True
        self._scheduler_task = asyncio.create_task(self._scheduler())

    # async def join(self):
    #     await self._queue.join()

    async def stop(self):
        self.is_running = False
        self._scheduler_task.cancel()

        if self.locked():
            await self._stop_event.wait()

    async def __aenter__(self):
        self.start()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.stop()
