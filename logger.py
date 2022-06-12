"""
    RPC-Server logger:
    Contains a simple logger function to log events in a csv file.
"""


# =====Imports========================================
import os
import csv
from threading import Lock

from VerteilteSystemeTestat.lock_timeout import lock_timeout


# =====Logger=========================================
logging_lock = Lock()


def write_in_log(items: list) -> None:
    """
    Write the given items into a new row of the logging csv file (log.csv).
    If no such file exist a new one is created and a header line is added.
    The Logs are also printed on the console.
    """
    with lock_timeout(logging_lock, 10) as acquired:
        if acquired:
            try:
                # Convert everything to a string (to improve the print on the console)
                for i in range(0, len(items)):
                    items[i] = str(items[i])

                # Write to file
                if not os.path.isfile('log.csv') or os.stat('log.csv').st_size == 0:
                    with open('log.csv', 'w', encoding='UTF8', newline='') as file:
                        writer = csv.writer(file)
                        # write the header
                        writer.writerow(["Timestamp", "Event", "IP", "Port", "Method", "Arguments", "Return"])
                with open('log.csv', 'a', encoding='UTF8', newline='') as file:
                    writer = csv.writer(file)
                    # write the data
                    writer.writerow(items)

                # Write to console
                print("[LOG] " + str(items)[1:-1])
            except:
                print('[WARNING] Could not write the log.')
        else:
            print('[WARNING] Timeout occurred while waiting for the log access. Log was not created.')
