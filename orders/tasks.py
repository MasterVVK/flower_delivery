import asyncio
import threading
from .bot_utils import notify_new_order

task_queue = []

def add_task(coro):
    task_queue.append(coro)
    if len(task_queue) == 1:
        threading.Thread(target=process_queue).start()

def process_queue():
    while task_queue:
        coro = task_queue.pop(0)
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(coro)
        loop.close()
