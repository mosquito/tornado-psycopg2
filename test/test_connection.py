#!/usr/bin/env python
# encoding: utf-8
import logging
from tornado_psycopg2.connection import AsyncConnection
from tornado.testing import gen_test
from test import TestBase

log = logging.getLogger("tests")


class ConnectionTestCase(TestBase):
    @gen_test
    def test_cursor(self):
        cursor = yield self.connection.cursor()
        yield cursor.execute("SELECT 1")
        yield cursor.fetchall()
        log.debug

    def setUp(self):
        self.connection = AsyncConnection(self.DSN)
        print self.connection
