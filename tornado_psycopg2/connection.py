#!/usr/bin/env python
# encoding: utf-8
import functools
import logging
from psycopg2._psycopg import QueryCanceledError
from concurrent import futures
from psycopg2 import connect
import psycopg2

from tornado.ioloop import IOLoop
from tornado.gen import Future, coroutine, sleep, Return
from tornado.process import cpu_count
from tornado.queues import Queue
from tornado_psycopg2.cursor import AsyncCursor

log = logging.getLogger("psycopg.async.connection")


class AsyncConnection(object):

    def __init__(self, *args, **kwargs):
        kwargs['async'] = True

        if "thread_pool" in kwargs:
            self.__thread_pool = kwargs.pop('thread_pool')
        else:
            self.__thread_pool = futures.ThreadPoolExecutor(cpu_count())

        self.__connection = connect(*args, **kwargs)

        self.__io_loop = IOLoop.current()
        self.__connected = False

        log.debug("Trying to connect to postgresql")
        f = self.__wait()
        self.__io_loop.add_future(f, self.__on_connect)
        self.__queue = Queue()
        self.__has_active_cursor = False

        for method in ('get_backend_pid', 'get_parameter_status'):
            setattr(self, method, self.__futurize(method))

    def __on_connect(self, result):
        log.debug("Connection establishment")
        self.__connected = True
        self.__io_loop.add_callback(self._loop)

    @coroutine
    def _loop(self):
        log.debug("Starting queue loop")
        while self.__connected:
            while self.__has_active_cursor or self.__connection.isexecuting():
                yield sleep(0.001)

            func, future = yield self.__queue.get()
            result = func()
            if isinstance(result, Future):
                result = yield result

            self.__io_loop.add_callback(future.set_result, result)
            yield self.__wait()

    @coroutine
    def __wait(self):
        log.debug("Waiting for events")
        while not (yield sleep(0.001)):
            try:
                state = self.__connection.poll()
            except QueryCanceledError:
                yield sleep(0.1)
                continue

            f = Future()

            def resolve(fileno, io_op):
                if f.running():
                    f.set_result(True)
                self.__io_loop.remove_handler(fileno)

            if state == psycopg2.extensions.POLL_OK:
                raise Return(True)

            elif state == psycopg2.extensions.POLL_READ:
                self.__io_loop.add_handler(self.__connection.fileno(), resolve, IOLoop.READ)
                yield f

            elif state == psycopg2.extensions.POLL_WRITE:
                self.__io_loop.add_handler(self.__connection.fileno(), resolve, IOLoop.WRITE)
                yield f

    def __on_cursor_open(self, cursor):
        self.__has_active_cursor = True
        log.debug('Opening cursor')

    def __on_cursor_close(self, cursor):
        self.__has_active_cursor = False
        log.debug('Closing active cursor')

    def cursor(self, **kwargs):
        f = Future()
        self.__io_loop.add_callback(
            self.__queue.put,
            (functools.partial(
                AsyncCursor,
                self.__connection,
                self.__thread_pool,
                self.__wait,
                on_open=self.__on_cursor_open,
                on_close=self.__on_cursor_close,
                **kwargs
            ), f)
        )
        return f

    def cancel(self):
        return self.__thread_pool.submit(self.__connection.cancel)

    def close(self):
        self.__has_active_cursor = True

        @coroutine
        def closer():
            while not (yield self.__queue.empty()):
                func, future = yield self.__queue.get()
                future.set_exception(psycopg2.Error("Connection closed"))

            self.__io_loop.add_callback(self.__connection.close)

    def __futurize(self, item):
        attr = getattr(self.__connection, item)

        @functools.wraps(attr)
        def wrap(*args, **kwargs):
            f = Future()
            self.__io_loop.add_callback(
                self.__queue.put,
                (functools.partial(attr, *args, **kwargs), f)
            )
            return f
        return wrap
