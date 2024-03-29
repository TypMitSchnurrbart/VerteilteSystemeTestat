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
import rpyc
from rpyc.utils.server import ThreadedServer
from typing import Union  # for better type hints

import src.logger as logger
from src.lock_timeout import lock_timeout


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
        Create a new empty Blackboard.

        param - {str} - name - Name of the new Blackboard
        param - {float or int or str} - valid_sec - Time the data in the Blackboard shall be valid

        return (successful?, message)
        """
        # To be sure the string parameters are a string
        name = str(name)

        # Initialize return_value variable
        return_value = None

        # Convert valid_sec to float
        try:
            valid_sec = float(valid_sec)
            if valid_sec == 0:
                valid_sec = float("inf")
        except ValueError:
            return_value = (False, "[ERROR] Invalid parameters! Please give valid time in seconds as Float or Int!")

        # Check if the valid time is lower to than zero
        if return_value is None and valid_sec <= 0:
            return_value = (False, f"[ERROR] The valid time must be greater or equal to 0! Given value: {valid_sec}.")

        if return_value is None:
            with lock_timeout(self.__board_lock, 10) as acquired:
                if acquired:
                    if name in self.__boards:
                        # Blackboard name already used
                        return_value = (False, f"[ERROR] Board name '{name}' already exists!")
                    else:
                        # Create new Blackboard
                        new_blackboard = {
                            "valid_sec": valid_sec,
                            "entry_time": time.time(),
                            "data": None
                        }
                        # Add to __boards
                        self.__boards[name] = new_blackboard
                        self.__save_boards()
                        return_value = (True, f"[INFO] Successfully created Board '{name}'!")
                else:
                    # Timeout
                    return_value = (False, "[TIMEOUT] The server is too busy. Board not created. Try again later.")

        # Log and return
        self.log_call("exposed_create_blackboard", (name, valid_sec), return_value)
        return return_value

    def exposed_display_blackboard(self, name: str, data: str) -> tuple:
        """
        Update the data of the Blackboard and refresh the timestamp.

        param - {str} - name - Name of the existing Blackboard
        param - {str} - data - Given data written to the Blackboard

        return (successful?, message)
        """
        # To be sure the string parameters are a string
        name = str(name)
        data = str(data)

        with lock_timeout(self.__board_lock, 10) as acquired:
            if acquired:
                if name in self.__boards:
                    # Update the Blackboard information
                    self.__boards[name]["entry_time"] = time.time()
                    self.__boards[name]["data"] = data
                    self.__save_boards()
                    return_value = (True, "[INFO] Board successfully updated!")
                else:
                    # Blackboard does not exist
                    return_value = (False, "[ERROR] Board does not exist!")
            else:
                # Timeout
                return_value = (False, "[TIMEOUT] The server is too busy. Board not updated. Try again later.")

        # Log and return
        self.log_call("exposed_display_blackboard", (name, data), return_value)
        return return_value

    def exposed_clear_blackboard(self, name: str) -> tuple:
        """
        Clear the given Blackboard data and set to invalid status.

        param - {str} - name - Unique name of the Blackboard

        return (successful?, message)
        """
        # To be sure the string parameters are a string
        name = str(name)

        with lock_timeout(self.__board_lock, 10) as acquired:
            if acquired:
                if name in self.__boards:
                    # Update the Blackboard information
                    self.__boards[name]["data"] = None
                    self.__save_boards()
                    return_value = (True, "[INFO] Board successfully cleared!")
                else:
                    # Blackboard does not exist
                    return_value = (False, "[ERROR] Board does not exist!")
            else:
                # Timeout
                return_value = (False, "[TIMEOUT] The server is too busy. Board not cleared. Try again later.")

        # Log and return
        self.log_call("exposed_clear_blackboard", (name,), return_value)
        return return_value

    def exposed_read_blackboard(self, name: str) -> tuple:
        """
        Return the data and valid state of the given Blackboard.

        param - {str} - name - Unique name of the Blackboard

        return (True, data, is_valid, message) OR (False, message)
        """
        # To be sure the string parameters are a string
        name = str(name)

        with lock_timeout(self.__board_lock, 10) as acquired:
            if acquired:
                if name in self.__boards:
                    # Read Blackboard
                    is_valid = self.__board_is_valid(name)
                    if self.__boards[name]["data"] is None:
                        # Return value with empty data (always invalid)
                        return_value = (True, self.__boards[name]["data"], False,
                                        "[WARNING] Successfully read but data is empty!")
                    elif not is_valid:
                        # Return value with invalid data
                        return_value = (True, self.__boards[name]["data"], is_valid,
                                        "[WARNING] Successfully read but data is invalid!")
                    else:
                        # Return value with valid data
                        return_value = (True, self.__boards[name]["data"], is_valid,
                                        "[INFO] Successfully read with valid data!")
                else:
                    # Blackboard does not exist
                    return_value = (False, "[ERROR] Board does not exist!")
            else:
                # Timeout
                return_value = (False, "[TIMEOUT] The server is too busy. Board not read. Try again later.")

        # Log and return
        self.log_call("exposed_read_blackboard", (name,), return_value)
        return return_value

    def exposed_get_blackboard_status(self, name: str) -> tuple:
        """
        Return current state of the given Blackboard.

        param - {str} - name - Unique name of the Blackboard

        return (True, is_empty, entry_time, is_valid, message) OR (False, message)
        """
        # To be sure the string parameters are a string
        name = str(name)

        with lock_timeout(self.__board_lock, 10) as acquired:
            if acquired:
                if name in self.__boards:
                    # Get Blackboard state
                    if self.__boards[name]["data"] is None:
                        is_empty = True
                    else:
                        is_empty = False
                    is_valid = self.__board_is_valid(name)
                    return_value = (True, is_empty, self.__boards[name]["entry_time"], is_valid and not is_empty,
                                    "[INFO] Successfully read Board status!")
                else:
                    # Blackboard does not exist
                    return_value = (False, "[ERROR] Board does not exist!")
            else:
                # Timeout
                return_value = (False, "[TIMEOUT] The server is too busy. Board not read. Try again later.")

        # Log and return
        self.log_call("exposed_get_blackboard_status", (name,), return_value)
        return return_value

    def exposed_list_blackboards(self) -> tuple:
        """
        Return a complete list of the Blackboards.

        return (True, list_of_boards, message) or (False, list_of_boards, message)
        """
        # Initialize the list
        list_of_boards = []

        # Initialize return_value variable
        return_value = None

        with lock_timeout(self.__board_lock, 10) as acquired:
            if acquired:
                # Get all Blackboard names
                for name in self.__boards:
                    list_of_boards.append(name)
            else:
                # Timeout
                return_value = (False,
                                "[TIMEOUT] The server is too busy. Could not list existing boards. Try again later.")

        if return_value is None:
            # Check for empty list to return a different message
            if len(list_of_boards) == 0:
                return_value = (True, list_of_boards, "[WARNING] No Boards found! Please create one first!")
            else:
                return_value = (True, list_of_boards, "[INFO] Successful read of Board list!")

        # Log and return
        self.log_call("exposed_list_blackboards", (), return_value)
        return return_value

    def exposed_delete_blackboard(self, name: str) -> tuple:
        """
        Delete the given Blackboard.

        param - {str} - name - Unique name of the Blackboard

        return (successful?, message)
        """
        # To be sure the string parameters are a string
        name = str(name)

        with lock_timeout(self.__board_lock, 10) as acquired:
            if acquired:
                if name in self.__boards:
                    # Delete Blackboard
                    del self.__boards[name]
                    self.__save_boards()
                    return_value = (True, "[INFO] Board successfully deleted!")
                else:
                    # Blackboard does not exist
                    return_value = (False, "[ERROR] Board does not exist!")
            else:
                # Timeout
                return_value = (False, "[TIMEOUT] The server is too busy. Board not deleted. Try again later.")

        # Log and return
        self.log_call("exposed_delete_blackboard", (name,), return_value)
        return return_value

    def exposed_delete_all_blackboards(self) -> tuple:
        """
        Delete all existing Blackboards.

        return (successful?,  message)
        """
        with lock_timeout(self.__board_lock, 10) as acquired:
            if acquired:
                # Delete all Blackboards
                self.__boards.clear()
                self.__save_boards()
                return_value = (True, "[INFO] Successfully deleted all Boards!")
            else:
                # Timeout
                return_value = (False, "[TIMEOUT] The server is too busy. Boards not deleted. Try again later.")

        # Log and return
        self.log_call("exposed_delete_all_blackboards", (), return_value)
        return return_value

    def log_call(self, method: str, args: tuple, return_value: tuple) -> None:
        """
        Log a method call from a client.

        param - {str} - name - The name of the called method
        param - {tuple} - name - The call arguments
        param - {tuple} - name - The return_value of the method
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
        Load all Boards from the board.json file.
        If no such file exist a new one is created.
        If an error occurs while reading an exiting board.json file the server is resumed with an empty Board
        dictionary and the old file is overwritten with the first __save_boards call.
        """
        try:
            with open('boards.json', 'r') as file:
                BlackBoardHost.__boards = json.load(file)
                print("[INFO] Successfully read Boards.")
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
        Stores all Boards in the board.json file.
        If no such file exist a new one is created.
        """
        try:
            with open('boards.json', 'w') as file:
                json.dump(BlackBoardHost.__boards, file, sort_keys=True, indent=4)
                print("[INFO] Successfully stored Boards.")
        except:
            print("[ERROR] Error while saving the Boards.")

    @staticmethod
    def __board_is_valid(name: str) -> bool:
        """
        Return true, if the data on the board is valid.
        Else it returns false.

        param - {str} - name - Unique name of the Blackboard

        return valid?
        """
        return BlackBoardHost.__boards[name]["entry_time"] + BlackBoardHost.__boards[name]["valid_sec"] >= time.time()


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
    Afterward the server the existing Blackboards form the board.json file are loaded and the server is started.
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

    # Initialize the server
    print("[INFO] Starting server on port " + str(port) + "...")
    server = None
    try:
        server = ThreadedServer(BlackBoardHost, port=port)
    except Exception as e:
        if isinstance(e, OSError):
            print("[ERROR] Server could not be started on port " + str(port) + ". Maybe this port is already used.")
            exit()
        else:
            print("[ERROR] An unknown error occurred. Closing the application.")
            exit()

    # Start the Server
    try:
        logger.write_in_log([datetime.now(), "Server-Start"])
        BlackBoardHost.load_boards()
        print("[INFO] Server started. To stop please use Ctrl+C.")
        server.start()
    except KeyboardInterrupt:
        pass
    except:
        print("[ERROR] An unknown error occurred. Closing the application.")

    logger.write_in_log([datetime.now(), "Server-Stop"])


if __name__ == "__main__":
    main(sys.argv[1:])
