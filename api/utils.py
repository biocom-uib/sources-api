import time
from contextlib import ContextDecorator

from api.config import config


class timing(ContextDecorator):
    def __init__(self, log, msg):
        self.log = log
        self.start = None
        self.msg = msg

    def __enter__(self):
        self.start = time.time()
        return self

    def __exit__(self, *exc):
        if config['TRACING_ENABLED']:
            self.log.info('%s. Time spent %s', self.msg, time.time() - self.start)
