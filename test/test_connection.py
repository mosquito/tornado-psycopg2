#!/usr/bin/env python
# encoding: utf-8
import logging
from random import choice, randint
from tornado.gen import coroutine
from tornado.testing import gen_test
from test import TestBase


log = logging.getLogger("tests")


class ConnectionTestCase(TestBase):
    @gen_test
    def test_001_cursor(self):
        cursor = yield self.connection.cursor()
        yield cursor.execute("SELECT 1 as test")
        r = yield cursor.fetchone()
        self.assertEqual(r, (1,))
        cursor.close()

    @gen_test
    def test_002_cancel(self):
        for _ in range(randint(1, 20)):
            with (yield self.connection.cursor()) as cursor:
                yield cursor.execute('SELECT pg_sleep(60)')
                yield self.connection.cancel()

    @gen_test
    def test_003_multiple_cursors(self):
        for x in range(randint(100, 200)):
            with (yield self.connection.cursor()) as cursor:
                yield cursor.execute("SELECT %s as test" % x)
                r = yield cursor.fetchone()
                self.assertEqual(r, (x,))

    @gen_test
    def test_004_parallel_multiple_cursors(self):
        connection = self.connection

        @coroutine
        def test1():
            with (yield connection.cursor()) as cursor:
                yield cursor.execute("SELECT 100 as test")
                self.assertEqual((yield cursor.fetchone()), (100,))

        @coroutine
        def test2():
            with (yield connection.cursor()) as cursor:
                yield cursor.execute("SELECT 200 as test")
                self.assertEqual((yield cursor.fetchone()), (200,))

        yield [choice((test1, test2))() for _ in range(randint(100, 200))]

    @gen_test
    def test_005_get_backend_pid(self):
        self.assertTrue((yield self.connection.get_backend_pid()) > 0)

    @gen_test
    def test_006_get_parameter_status(self):
        result = yield self.connection.get_parameter_status('TIME ZONE')
        self.assertTrue(result is None)
