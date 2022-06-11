"""
    RPC-Server:
    Contains the service class, the main-function of the server and additional functions.
    To realize the RPC communication a modified version of the RPyC library is used.
"""

# =====Imports=========================================
import sys
import time
import json
import getopt
from threading import Lock
from datetime import datetime
from typing import Union  # for better type hints

import logger as logger

import rpyc
from rpyc.utils.server import ThreadedServer


# =====Service Class===================================
class BlackBoardHost(rpyc.Service):
    # static variables
    __boards = {}
    __board_lock = Lock()

    def __init__(self):
        """
        Initializes the BlackBoardHost (service) class.
        A BlackBoardHost instance is created for each connected client.
        """
        # storing the client address is needed because you can't get information from a closed socket
        self.__client_address = None

    def on_connect(self, conn: rpyc.core.protocol.Connection) -> None:
        """
        Called when the client connects.
        Saves the address of the connected client and writes a log entry.

        param - {rpyc.core.protocol.Connection} - conn - The connection with the client
        """
        # Access protected attribute. But can't be done otherwise without modifying the library.
        self.__client_address = conn._channel.stream.sock.getpeername()
        logger.write_in_log([datetime.now(), "Client-Connect", *self.__client_address])

    def on_disconnect(self, conn: rpyc.core.protocol.Connection):
        """
        Called when the client is disconnected.
        Writes a log entry.

        param - {rpyc.core.protocol.Connection} - conn - The (former) connection with the client
        """
        logger.write_in_log([datetime.now(), "Client-Disconnect", *self.__client_address])

    def exposed_create_blackboard(self, name: str, valid_sec: Union[float, int, str]) -> tuple:
        """
        Create a new empty blackboard.

        param - {str} - name - Name of the new blackboard
        param - {float or int or str} - valid_sec - Time the data in the blackboard shall be valid

        return (Successful?, Message)
        """
        # To be sure the string parameters are a string
        name = str(name)

        return_value = None

        # Convert valid_sec to float
        try:
            valid_sec = float(valid_sec)
        except ValueError:
            return_value = (False, "[ERROR] Invalid parameters! Please give valid time in seconds as Float or Int!")

        # Check if the valid time is bigger or equal to than zero!
        if return_value is None and valid_sec == 0:
            valid_sec = float("inf")
        if return_value is None and valid_sec <= 0:
            return_value = (False, f"[ERROR] The valid time must be greater or equal to 0! Given value: {valid_sec}.")

        # Check if name already given
        if return_value is None and name in self.__boards:
            return_value = (False, f"[ERROR] Board name '{name}' already exists!")

        if return_value is None:
            with self.__board_lock:
                # Init the new blackboard
                new_blackboard = {
                    "name": name,
                    "valid_sec": valid_sec,
                    "entry_time": time.time(),
                    "is_valid": False,
                    "data": ""
                }

                # Add to __boards
                self.__boards[name] = new_blackboard
                self.__save_boards()
            return_value = (True, f"[INFO] Successfully created board {name}!")

        self.log_call("exposed_create_blackboard", (name, valid_sec), return_value)
        return return_value

    def exposed_display_blackboard(self, name: str, data: str) -> tuple:
        """
        Update the data of the blackboard and refresh the timestamp.

        param - {str} - name - Name of the existing blackboard
        param - {str} - data - Given data written to the blackboard

        return (Successful?, Message)
        """
        # To be sure the string parameters are a string
        name = str(name)
        data = str(data)

        return_value = None

        # Check if the blackboard exists
        if name not in self.__boards:
            return_value = (False, "[ERROR] Board does not exist!")

        if return_value is None:
            with self.__board_lock:
                # Update the board information
                self.__boards[name]["entry_time"] = time.time()
                self.__boards[name]["data"] = data
                self.__boards[name]["is_valid"] = True
                self.__save_boards()
            return_value = (True, "[INFO] Board successfully updated!")

        self.log_call("exposed_display_blackboard", (name, data), return_value)
        return return_value

    def exposed_clear_blackboard(self, name: str) -> tuple:
        """
        Clear the given blackboard data and set to invalid status.

        param - {str} - name - Unique name of the blackboard

        return (Successful?, Message)
        """
        # To be sure the string parameters are a string
        name = str(name)

        return_value = None

        # Check if the blackboard exists
        if name not in self.__boards:
            return_value = (False, "[ERROR] Board does not exist!")

        if return_value is None:
            with self.__board_lock:
                # Update the board information
                self.__boards[name]["data"] = ""
                self.__boards[name]["is_valid"] = False
                self.__save_boards()
            return_value = (True, "[INFO] Board successfully cleared!")

        self.log_call("exposed_clear_blackboard", (name,), return_value)
        return return_value

    def exposed_read_blackboard(self, name: str) -> tuple:
        """
        Return the data and valid state of the given blackboard.

        param - {str} - name - Unique name of the blackboard

        return (Successful?, data, is_valid, Message)
        """
        # To be sure the string parameters are a string
        name = str(name)

        return_value = None

        # Check if the blackboard exists
        if name not in self.__boards:
            return_value = (False, "[ERROR] Board does not exist!")

        if return_value is None:
            with self.__board_lock:
                # Update valid state before returning
                if self.__boards[name]["entry_time"] + self.__boards[name]["valid_sec"] <= time.time():
                    # Update valid state
                    self.__boards[name]["is_valid"] = False
                    self.__save_boards()
                    # Return the data but with invalid message
                    return_value = (True, self.__boards[name]["data"], self.__boards[name]["is_valid"],
                                    "[WARNING] Successfully read but data is invalid!")

                # Data still valid
                else:
                    # Check for empty data
                    if self.__boards[name]["data"] == "":
                        return_value = (True, self.__boards[name]["data"], self.__boards[name]["is_valid"],
                                        "[WARNING] Successfully read but data is empty!")
                    else:
                        # Return Read without problems!
                        return_value = (True, self.__boards[name]["data"], self.__boards[name]["is_valid"],
                                        "[INFO] Successfully read with valid data!")

        self.log_call("exposed_read_blackboard", (name,), return_value)
        return return_value

    def exposed_get_blackboard_status(self, name: str) -> tuple:
        """
        Return current state of the given blackboard.

        param - {str} - name - Unique name of the blackboard

        return (Successful?, is_empty, entry_time, is_valid, Message)
        """
        # To be sure the string parameters are a string
        name = str(name)

        return_value = None

        # Check if the blackboard exists
        if name not in self.__boards:
            return_value = (False, "[ERROR] Board does not exist!")

        if return_value is None:
            with self.__board_lock:
                # Check is the data is empty or not
                if self.__boards[name]["data"] == "":
                    is_empty = True
                else:
                    is_empty = False
                # Update valid state before returning
                if self.__boards[name]["entry_time"] + self.__boards[name]["valid_sec"] <= time.time():
                    # Update valid state
                    self.__boards[name]["is_valid"] = False
                    self.__save_boards()
                # Return with the remaining information
            return_value = (True, is_empty, self.__boards[name]["entry_time"], self.__boards[name]["is_valid"],
                            "[INFO] Successfully read board status!")

        self.log_call("exposed_get_blackboard_status", (name,), return_value)
        return return_value

    def exposed_list_blackboards(self) -> tuple:
        """
        Return a complete list of the blackboards.

        return (Successful?, list_of_boards, Message)
        """
        # Init the list
        list_of_boards = []

        # get all board names
        with self.__board_lock:
            for name in self.__boards:
                list_of_boards.append(name)

        # Check for empty list to return a different message
        if len(list_of_boards) == 0:
            return_value = (True, list_of_boards, "[ERROR] No boards found! Please create one first!")
        else:
            return_value = (True, list_of_boards, "[INFO] Successful read of board list!")

        self.log_call("exposed_list_blackboards", (), return_value)
        return return_value

    def exposed_delete_blackboard(self, name: str) -> tuple:
        """
        Delete the given blackboard.

        param - {str} - name - Unique name of the blackboard

        return (Successful?,  Message)
        """
        # To be sure the string parameters are a string
        name = str(name)

        return_value = None

        # Check if the blackboard exists
        if name not in self.__boards:
            return_value = (False, "[ERROR] Board does not exist!")

        if return_value is None:
            # Delete board
            with self.__board_lock:
                del self.__boards[name]
                self.__save_boards()
            return_value = (True, "[INFO] Board successfully deleted!")

        self.log_call("exposed_delete_blackboard", (name,), return_value)
        return return_value

    def exposed_delete_all_blackboards(self) -> tuple:
        """
        Delete all existing blackboards.

        param - {str} - name - Unique name of the blackboard

        return (Successful?,  Message)
        """
        with self.__board_lock:
            self.__boards = {}
            self.__save_boards()
        return_value = (True, "[INFO] Successfully deleted all boards!")

        self.log_call("exposed_delete_all_blackboards", (), return_value)
        return return_value

    def log_call(self, method: str, args: tuple, return_value: tuple):
        """
        TODO Docstring
        """
        # Convert the args to a pretty string
        if len(args) == 0:
            args = "()"
        elif len(args) == 1:
            args = "(" + str(args[0]) + ")"
        else:
            args = str(args)

        # Simple conversion of the return value -> Length always >= 2
        return_value = str(return_value)

        # Log
        logger.write_in_log([datetime.now(), "Method-Call", *self.__client_address, method, args, return_value])

    @staticmethod
    def load_boards() -> None:
        """
        Load all boards from the board.json file.
        If no such file exist a new one is created.
        If an error occurs while reading an exiting board.json file the server is resumed with an empty board
        dictionary and the old file is overwritten with the first __save_boards call.
        """
        try:
            with open('boards.json', 'r') as file:
                BlackBoardHost.__boards = json.load(file)
                print("[INFO] Successfully read boards.")
        except Exception as e:
            if isinstance(e, FileNotFoundError):
                BlackBoardHost.__save_boards()
                print("[WARNING] Found no existing board.json file. Created a new one.")
            else:
                print("[ERROR] Error while loading board.json file.")
            BlackBoardHost.__boards = {}

    @staticmethod
    def __save_boards() -> None:
        """
        Stores all boards in the board.json file.
        If no such file exist a new one is created.
        """
        try:
            with open('boards.json', 'w') as file:
                json.dump(BlackBoardHost.__boards, file, sort_keys=True, indent=4)
                print("[INFO] Successfully stored boards.")
        except:
            print("[ERROR] Error while saving the boards.")


# =====Functions=======================================
def show_help() -> None:
    """
    Print a help text on the console.
    """
    print("BlackBoardServer v0.1")
    print("Arguments:")
    print("-p / --port: Set the used port (default=8080)")
    print("-h / --help: Show this text")


# =====Main============================================
def main(argv: list) -> None:
    """
    The main-function of the server.
    Parses the given arguments to determine the server port (default: 8080).
    Afterward the server the existing blackboards form the board.json file are loaded and the server is started.
    It also logs the start and stop of the server.

    param - {str} - argv - A list of the arguments
    """
    # Parse arguments:
    try:
        opts, args = getopt.getopt(argv, "p:h", ["port=", "help"])
    except getopt.GetoptError as err:
        print("[ERROR] Invalid arguments.")
        sys.exit()
    port = 8080

    if len(args) != 0:
        print("[ERROR] Invalid arguments.")

    for o, a in opts:
        if o in ("-h", "--help"):
            show_help()
            exit()
        elif o in ("-p", "--port"):
            try:
                port = int(a)
            except:
                print("[ERROR] Invalid Port number.")
                exit()
            if port < 0 or port > 49151:
                print("[ERROR] Port number out of range.")
                exit()

    # Start the server
    print("[INFO] Starting server on port " + str(port) + "...")
    server = ThreadedServer(BlackBoardHost, port=port)

    BlackBoardHost.load_boards()
    logger.write_in_log([datetime.now(), "Server-Start"])

    # Start the Server
    print("[INFO] Server started. To stop please use Ctrl+C.")
    server.start()

    logger.write_in_log([datetime.now(), "Server-Stop"])


if __name__ == "__main__":
    main(sys.argv[1:])
