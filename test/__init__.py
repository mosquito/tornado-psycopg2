#!/usr/bin/env python
# encoding: utf-8
import os
import logging
from tornado.ioloop import IOLoop
from tornado.testing import AsyncTestCase
from tornado.log import enable_pretty_logging


logging.getLogger().setLevel(getattr(logging, os.getenv('LOG_LEVEL', 'INFO').upper(), logging.INFO))
enable_pretty_logging(logger=logging.getLogger())


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
