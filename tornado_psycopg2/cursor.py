# encoding: utf-8
import functools
from tornado.ioloop import IOLoop
from tornado.gen import coroutine, Return


class AsyncCursor(object):

    def __init__(self, connection, thread_pool, waiter, on_open=None, on_close=None, **kwargs):
        self.__cursor = connection.cursor(**kwargs)
        self.__thread_pool = thread_pool
        self.__on_open = on_open
        self.__on_close = on_close
        self.__io_loop = IOLoop.current()
        self.__wait = waiter

        if callable(on_open):
            on_open(self)

        for prop in ('fetchall', 'fetchone', 'execute', 'fetchmany', 'callproc'):
            setattr(self, prop, self.__futurize(
                getattr(self.__cursor, prop),
            ))

    def __futurize(self, func):
        @functools.wraps(func)
        @coroutine
        def wrap(*args, **kwargs):
            yield self.__wait()
            result = yield self.__thread_pool.submit(func, *args, **kwargs)
            raise Return(result)
        return wrap

    def close(self):
        @coroutine
        def closer():
            yield self.__wait()
            self.__cursor.close()
            if callable(self.__on_close):
                self.__on_close(self)

        self.__io_loop.add_callback(closer)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

    def __getattr__(self, item):
        return getattr(self.__cursor, item)
