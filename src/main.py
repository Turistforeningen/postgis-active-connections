import os
import psycopg2
import re
import socket
import sys
import threading
import time

from log import logger
from raven_client import client
from secrets import secrets


def main():
    logger.info("Starting thread cannon loop. Here we go!")
    while True:
        threading.Thread(target=report_active_connections).start()
        time.sleep(5)  # Report every this many seconds


def report_active_connections():
    try:
        connection_url = "host=%s dbname=%s user=%s password=%s" % (
            os.environ['DB_HOST'],
            os.environ['DB_DATABASE'],
            os.environ['DB_USER'],
            secrets['DB_PASSWORD'],
        )
        with psycopg2.connect(connection_url) as connection:
            connection.set_session(autocommit=True)
            with connection.cursor() as cursor:
                cursor.execute("select state from pg_stat_activity;")
                states = {
                    'active': 0,
                    'idle': 0,
                    'idle_in_transaction': 0,
                    'idle_in_transaction_aborted': 0,
                    'fastpath_function_call': 0,
                    'null': 0,
                }
                for row in cursor.fetchall():
                    # Known states and librato metric name limitations:
                    # https://www.postgresql.org/docs/9.6/static/monitoring-stats.html
                    # https://www.librato.com/docs/kb/faq/best_practices/naming_convention_metrics_tags/
                    key = row[0]

                    # Handle null values. Not sure why this occurs, see:
                    # https://sentry.io/turistforeningen/postgres-active-connections/issues/264700288/
                    if key is None:
                        key = 'null'

                    # Remove parentheses
                    key = re.sub(r'[()]', '', key)

                    # Replace space with underscore
                    key = re.sub(r' ', '_', key)

                    states[key] += 1

        statsd_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        for key, value in states.items():
            name = 'postgres.active_connections.%s' % (
                key.lower().replace(' ', '_'))
            message = ("%s:%s|g" % (name, value)).encode('utf-8')
            statsd_socket.sendto(message, (os.environ["STATSD_HOST"], 8125))

        logger.debug(
            "Reported %s connections to librato" % sum(states.values()))
    except Exception as e:
        client.captureException()
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        logger.error("%s:%s %s: %s" % (fname, exc_tb.tb_lineno, exc_type,
                                       str(e).strip()))


if __name__ == '__main__':
    main()
