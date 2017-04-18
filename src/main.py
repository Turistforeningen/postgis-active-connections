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
        os.environ['HOST'],
        os.environ['DATABASE'],
        os.environ['USER'],
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

    # TODO: Report to librato


if __name__ == '__main__':
    main()
