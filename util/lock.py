import time


class LockException(Exception):
    pass


class Lock:
    def __init__(self, timeout: float = 60.0):
        self.locks = {}
        self.timeout = timeout

    def gain_lock(self, key: str):
        lock = self.locks.get(key)

        now = time.time()

        if not lock or lock < (time.time() - self.timeout):
            self.locks[key] = now
            return

        raise LockException()

    def release_lock(self, key: str):
        self.locks.pop(key, None)
