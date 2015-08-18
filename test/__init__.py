#!/usr/bin/env python
# encoding: utf-8
import os
from tornado.ioloop import IOLoop
from tornado.testing import AsyncTestCase
from tornado_psycopg2.connection import AsyncConnection


class TestBase(AsyncTestCase):
    DSN = "host={host} dbname={db_name} user={user} password=\"{password}\"".format(
        host=os.getenv("DB_HOST", 'localhost'),
        user=os.getenv("DB_USER", 'postgres'),
        password=os.getenv("DB_PASSWORD", 'postgres'),
        db_name=os.getenv("DB_NAME", 'postgres'),
    )

    @property
    def io_loop(self):
        return IOLoop.current()

    def setUp(self):
        self.connection = AsyncConnection(self.DSN)

    def tearDown(self):
        self.connection.close()
