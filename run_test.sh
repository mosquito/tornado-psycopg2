#!/bin/bash

# --with-coverage 
DB_USER=test DB_NAME=test_async_pg DB_PASSWORD=test LOG_LEVEL=debug nosetests --logging-format="%(asctime)s [%(name)s] %(levelname)-6s %(message)s"
