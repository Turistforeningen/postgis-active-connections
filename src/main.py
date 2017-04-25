import json
import os
import psycopg2
import re
import socket
import threading
import time

# Read secrets
print("Reading secrets...")
with open('/secrets/secrets.json') as f:
    secrets = json.loads(f.read())


def main():
    print("Initiating main loop...")
    while True:
        threading.Thread(target=report_active_connections).start()
        time.sleep(5)  # Report every this many seconds


def report_active_connections():
    connection = psycopg2.connect("host=%s dbname=%s user=%s password=%s" % (
        os.environ['DB_HOST'],
        os.environ['DB_DATABASE'],
        os.environ['DB_USER'],
        secrets['DB_PASSWORD'],
    ))
    cursor = connection.cursor()
    cursor.execute("select state from pg_stat_activity;")
    states = {
        'active': 0,
        'idle': 0,
        'idle_in_transaction': 0,
        'idle_in_transaction_aborted': 0,
        'fastpath_function_call': 0,
    }
    for row in cursor.fetchall():
        # Known states and librato metric name limitations:
        # https://www.postgresql.org/docs/9.6/static/monitoring-stats.html
        # https://www.librato.com/docs/kb/faq/best_practices/naming_convention_metrics_tags/
        key = row[0]
        key = re.sub(r'[()]', '', key)  # remove parentheses
        key = re.sub(r' ', '_', key)  # replace space with underscore
        states[key] += 1
    cursor.close()
    connection.close()

    statsd_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    for key, value in states.items():
        name = 'postgres.active_connections.%s' % key.lower().replace(' ', '_')
        message = ("%s:%s|g" % (name, value)).encode('utf-8')
        statsd_socket.sendto(message, (os.environ["STATSD_HOST"], 8125))

    print("Reported %s connections to librato" % sum(states.values()))


if __name__ == '__main__':
    main()
