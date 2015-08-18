# encoding: utf-8
import functools
from tornado.gen import coroutine, Return


class AsyncCursor(object):
    def __init__(self, connection, thread_pool):
        self.__cursor = connection.cursor()
        self.__thread_pool = thread_pool

        for prop in ('fetchall', 'execute', 'fetchmany', 'callproc'):
            setattr(self, prop, self.__futurize(getattr(self.__cursor, prop)))

    def __futurize(self, func):
        @functools.wraps(func)
        @coroutine
        def wrap(*args, **kwargs):
            result = yield self.__thread_pool.submit(func, *args, **kwargs)
            raise Return(result)
        return wrap

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        return self.__cursor.__exit__(exc_type, exc_val, exc_tb)

    def __getattr__(self, item):
        return getattr(self.__cursor, item)