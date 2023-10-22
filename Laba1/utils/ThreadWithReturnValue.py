import sys
import threading


class ThreadWithReturnValue(threading.Thread):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._result = None

    def run(self):
        if self._target is None:
            return
        try:
            self._result = self._target(*self._args, **self._kwargs)
        except Exception as e:
            print(f"{type(e).__name__}: {e}", file=sys.stderr)

    def join(self, *args, **kwargs):
        super().join(*args, **kwargs)
        return self._result