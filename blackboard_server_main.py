"""
    Testing the RPyC Module
    Hosting a Server

    TODO DOCSTRING
    TODO Validity zu Beginn auf true???
"""

# =====Imports=========================================

import sys
import os
import time
import json
from threading import Lock
from datetime import datetime
import logger as Logger
import getopt

# add custom library location to path
sys.path.append(str(os.path.dirname(os.path.abspath(__file__))) + "/RPyC/rpyc_main_folder")

import rpyc
from rpyc.utils.server import ThreadedServer


# =====Server Class====================================
class BlackBoardHost(rpyc.Service):
    __boards = {}
    __board_lock = Lock()

    def __init__(self):
        """
        TODO
        """
        # dict is needed because you can't get information from a closed socket
        self.__client_address = {}

    def on_connect(self, conn):
        """
        TODO Docstring
        """
        self.__client_address = conn._channel.stream.sock.getpeername()
        Logger.write_in_log([datetime.now(), "Client-Connect", *self.__client_address])

    def on_disconnect(self, conn):
        """
        TODO Docstring
        """
        Logger.write_in_log([datetime.now(), "Client-Disconnect", *self.__client_address])

    def exposed_create_blackboard(self, name, valid_sec):
        """
        Create a new blackboard by adding it to the JSON Database? Dict in RAM?

        TODO Docstring

        param - {str} - name - Name of the new blackbox
        param - {float} - valid_sec - Time the Data in the blackbox shall be valid 

        return (Successful?, Message)
        """
        # Check for correct types
        # Convert valid_sec to float
        try:
            valid_sec = float(valid_sec)
        except ValueError:
            return (False, "[ERROR] Invalid Parameters! Please give Valid Time in Seconds as Float or Int")

        # Check if the valid time is bigger than zero!
        if valid_sec <= 0:
            return (False, f"[ERROR] The valid time must be greater than 0! Given value: {valid_sec}")

        # Check if name already given
        if name in self.__boards:
            return (False, f"[ERROR] Board Name '{name}' already exists")

        # Lock the dataframe
        with self.__board_lock:
            # Init the new blackboard
            new_blackboard = {
                "name": name,
                "valid_sec": valid_sec,
                "entry_time": time.time(),
                "is_valid": True,
                "data": ""
            }

            # Add to boards
            self.__boards[name] = new_blackboard
            self.__save_boards()

        return (True, f"[INFO] Successfully created Board {name}!")

    def exposed_display_blackboard(self, name, data):
        """
        Update the data of the blackboard and refresh the timestamp

        param - {str} - name - Name of the EXISTING Blackboard
        param - {str?} - data - Given data written to blackboard

        return (Successful?, Message)
        """
        # Check if the blackboard exists
        if name not in self.__boards:
            return (False, "[ERROR] Board does not exist!")

        # Lock the dataframe
        with self.__board_lock:
            # Update the board information
            self.__boards[name]["entry_time"] = time.time()
            self.__boards[name]["data"] = data
            self.__boards[name]["is_valid"] = True
            self.__save_boards()

        return (True, "[INFO] Blackboard successfully updated!")

    def exposed_clear_blackboard(self, name):
        """
        Clear the given board data and set to invalid status!

        param - {str} - name - Unique name of the board

        return (Successful?, Message)
        """
        # Check if the blackboard exists
        if name not in self.__boards:
            return (False, "[ERROR] Board does not exist!")

        with self.__board_lock:
            # Update the board information
            self.__boards[name]["data"] = ""
            self.__boards[name]["is_valid"] = False
            self.__save_boards()

        return (True, "[INFO] Blackboard successfully cleared!")

    def exposed_read_blackboard(self, name):
        """
        Return the data and valid state of the given board

        param - {str} - name - Unique name of the board

        return (Successful?, data, is_valid, Message)
        """

        # Check if the blackboard exists
        if name not in self.__boards:
            return (False, "[ERROR] Board does not exist!")

        with self.__board_lock:
            # Update valid state before returning
            if self.__boards[name]["entry_time"] + self.__boards[name]["valid_sec"] <= time.time():
                # Update valid state
                self.__boards[name]["is_valid"] = False
                self.__save_boards()
                # Return the data but with invalid message
                return (True, self.__boards[name]["data"], self.__boards[name]["is_valid"],
                        "[WARNING] Successfully read but Data is invalid!")

            # Data still valid
            else:
                # Check for empty data
                if self.__boards[name]["data"] == "":
                    return (True, self.__boards[name]["data"], self.__boards[name]["is_valid"],
                            "[WARNING] Successfully read but data is empty!")
                # Return Read without problems!
                return (True, self.__boards[name]["data"], self.__boards[name]["is_valid"],
                        "[INFO] Successfully read with valid data!")

    def exposed_get_blackboard_status(self, name):
        """
        Return current state of the given board

        param - {str} - name - Unique name of the board

        return (Successful?,  is_empty, entry_time, is_valid, Message)
        """
        # Check if the blackboard exists
        if name not in self.__boards:
            return (False, "[ERROR] Board does not exist!")

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
            return (
                True, is_empty, self.__boards[name]["entry_time"], self.__boards[name]["is_valid"],
                "[INFO] Successfully read board status!")

    def exposed_list_blackboards(self):
        """
        Simply return a complete list of the blackboards
        
        param - {str} - name - Unique name of the board

        return (Successful?,  list_of_boards, Message)
        """
        # Init the list
        list_of_boards = []

        # get all board names
        with self.__board_lock:
            for name in self.__boards:
                list_of_boards.append(name)

        # Check for empty list to return a different message
        if len(list_of_boards) == 0:
            return (True, list_of_boards, "[ERROR] No Boards found! Please create one first!")

        return (True, list_of_boards, "[INFO] Successful read of Blackboard List!")

    def exposed_delete_blackboard(self, name):
        """
        Delete the given board

        param - {str} - name - Unique name of the message

        param - {str} - name - Unique name of the board

        return (Successful?,  Message)
        """
        # Check if the blackboard exists
        if name not in self.__boards:
            return (False, "[ERROR] Board does not exist!")

        with self.__board_lock:
            del self.__boards[name]
            self.__save_boards()
        return (True, "[INFO] Board successfully deleted.")

    def exposed_delete_all_blackboards(self):
        """
        Delete all existing blackboards!

        param - {str} - name - Unique name of the board

        return (Successful?,  Message)
        """
        with self.__board_lock:
            self.__boards = {}
            self.__save_boards()
        return (True, "[INFO] Successfully deleted all boards!")

    @staticmethod
    def log_call(ip, port, method, args, return_value):
        """
        TODO Docstring
        """
        Logger.write_in_log([datetime.now(), "Method-Call", ip, port, method, str(args), str(return_value)])

    @staticmethod
    def load_boards():
        """
        TODO Docstring
        """
        try:
            with open('boards.json', 'r') as file:
                BlackBoardHost.__boards = json.load(file)
                print("[INFO] Successfully read boards")
        except Exception as e:
            if e is FileNotFoundError:
                print("[INFO] Found no board.json file")
            else:
                print("Hi")
                print(type(e))
                print("[ERROR] Error while loading board.json file")
            BlackBoardHost.__boards = {}

    @staticmethod
    def __save_boards():
        """
        TODO Docstring
        """
        try:
            with open('boards.json', 'w') as file:
                json.dump(BlackBoardHost.__boards, file, sort_keys=True, indent=4)
                print("[INFO] Successfully stored boards")
        except:
            print("[ERROR] Error while saving the boards")

        # Debug Print # TODO Remove
        print("\033c", end="")
        print(json.dumps(BlackBoardHost.__boards, indent=4, ensure_ascii=False))
        print("\n====================================================\n")
        print("[INFO] To stop the Server please use Ctrl+C")


# =====Help============================================
def show_help():
    """
    TODO Docstring
    """
    print("BlackBoardServer v0.1")
    print("Arguments:")
    print("-p / --port: Set the used port (default=8080)")
    print("-h / --help: Show this text")


# =====Main============================================
if __name__ == "__main__":
    """
    TODO Docstring
    """
    # Parse arguments:
    try:
        opts, args = getopt.getopt(sys.argv[1:], "p:h", ["port=", "help"])
    except getopt.GetoptError as err:
        print("[Error] Invalid arguments.")
        sys.exit()
    port = 8080

    if len(args) != 0:
        print("[Error] Invalid arguments.")

    for o, a in opts:
        if o in ("-h", "--help"):
            show_help()
            sys.exit()
        elif o in ("-p", "--port"):
            try:
                port = int(a)
            except:
                print("[Error] Invalid Port number")
                sys.exit()
            if port < 0 or port > 49151:
                print("[Error] Port number out of range")
                sys.exit()

    # Start the server
    print("[INFO] Starting server on port " + str(port) + "...")
    server = ThreadedServer(BlackBoardHost, port=port)

    BlackBoardHost.load_boards()
    Logger.write_in_log([datetime.now(), "Server-Start"])

    # Start the Server
    print("[INFO] Server started. To stop please use Ctrl+C")
    server.start()

    Logger.write_in_log([datetime.now(), "Server-Stop"])
