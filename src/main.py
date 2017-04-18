import socket
import os
import psycopg2
import threading
import time


def main():
    while True:
        threading.Thread(target=report_active_connections).start()
        time.sleep(30)  # Report every 30 seconds


def report_active_connections():
    connection = psycopg2.connect("host=%s dbname=%s user=%s password=%s" % (
        os.environ['DB_HOST'],
        os.environ['DB_DATABASE'],
        os.environ['DB_USER'],
        'password',  # TODO
    ))
    cursor = connection.cursor()
    cursor.execute("select state from pg_stat_activity;")
    states = {}
    for row in cursor.fetchall():
        if row[0] not in states:
            states[row[0]] = 1
        else:
            states[row[0]] += 1

    statsd_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    for key, value in states.items():
        name = 'postgres.active_connections.%s' % key.lower().replace(' ', '_')
        message = ("%s:1|c" % (name)).encode('utf-8')
        statsd_socket.sendto(message, (os.environ["STATSD_HOST"], 8125))


if __name__ == '__main__':
    main()
