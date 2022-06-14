"""
    lock_timeout:
    Contains a simple function which can be used to wait a maximum amount of time for acquiring a lock.
"""

# =====Imports=========================================
from threading import Lock
from contextlib import contextmanager


# =====Functions=======================================
@contextmanager
def lock_timeout(lock: Lock, timeout: float):
    """
    Contextmanager-function which can be used in with the with-statement to wait a maximum amount of time for acquiring
    a lock.

    param - {Lock} - lock - The lock which should be acquired
    param - {float} - timeout - The maximum time for acquiring the lock
    """
    result = lock.acquire(timeout=timeout)
    yield result
    if result:
        lock.release()
