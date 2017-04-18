import threading
import time


def main():
    while True:
        threading.Thread(target=report_active_connections).start()
        time.sleep(30)  # Report every 30 seconds


def report_active_connections():
    # TODO
    pass


if __name__ == '__main__':
    main()
