"""
    Testing the RPyC Module
    Hosting a Server

    TODO

        - maybe return dict everywhere instead of tuples!
"""

#=====Imports=========================================

import sys
import os
import time
import json
from threading import Lock
from datetime import datetime
import logger as Logger

# add custom library location to path
sys.path.append(str(os.path.dirname(os.path.abspath(__file__))) + "/RPyC/rpyc_main_folder")

import rpyc
from rpyc.utils.server import ThreadedServer

#=====Global == But may want to use JSON instead of global param!==
boards = {}

# Created lock, perhaps think of another solution than creating as "global" lock
board_lock = Lock()

#=====Server Class====================================
class BlackBoardHost(rpyc.Service):
    def __init__(self):
        # dict is needed because you can't get information from a closed socket
        self.socket_adress_dict = {}

    def on_connect(self, conn):
        self.socket_adress_dict[conn] = conn._channel.stream.sock.getpeername()
        Logger.write_in_log([datetime.now(), "Client-Connect", *self.socket_adress_dict[conn]])

    def on_disconnect(self, conn):
        Logger.write_in_log([datetime.now(), "Client-Disconnect", *self.socket_adress_dict[conn]])
        self.socket_adress_dict.pop(conn)

    def exposed_create_blackboard(self, name, valid_sec):
        """
        Create a new blackboard by adding it to the JSON Database? Dict in RAM?

        TODO
            - Decide storage technology

        param - {str} - name - Name of the new blackbox
        param - {float} - valid_sec - Time the Data in the blackbox shall be valid 

        return (Successful?, Message)
        """

        global boards

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
        if name in boards:
            return (False, f"[ERROR] Board Name '{name}' already exists")

        # Lock the dataframe
        with board_lock:
            # Init the new blackboard
            new_blackboard = {
                "name" : name,
                "valid_sec" : valid_sec,
                "entry_time" : time.time(),
                "is_valid" : True,
                "data" : ""
            }

            # Add to boards
            boards[name] = new_blackboard
                
        # TODO Delete for debug
        self.debug_print()

        return (True, f"[INFO] Successfully created Board {name}!")


    def exposed_display_blackboard(self, name, data):
        """
        Update the data of the blackboard and refresh the timestamp

        param - {str} - name - Name of the EXISTING Blackboard
        param - {str?} - data - Given data written to blackboard

        return (Successful?, Message)
        """

        global boards

        # Check if the blackboard exists
        if name not in boards:
            return (False, "[ERROR] Board does not exist!")

        # Lock the dataframe
        with board_lock:
            # Update the board information
            boards[name]["entry_time"] = time.time()
            boards[name]["data"] = data
            boards[name]["is_valid"] = True
            

        # TODO delete
        self.debug_print()

        return (True, "[INFO] Blackboard successfully updated!")
        

    def exposed_clear_blackboard(self, name):
        """
        Clear the given board data and set to invalid status!

        param - {str} - name - Unique name of the board

        return (Successful?, Message)
        """

        global boards

        # Check if the blackboard exists
        if name not in boards:
            return (False, "[ERROR] Board does not exist!")

        with board_lock:

            # Update the board information
            boards[name]["data"] = ""
            boards[name]["is_valid"] = False


        # TODO delete
        self.debug_print()

        return (True, "[INFO] Blackboard successfully cleared!")


    def exposed_read_blackboard(self, name):
        """
        Return the data and valid state of the given board

        param - {str} - name - Unique name of the board

        return (Successful?, data, is_valid, Message)
        """

        global boards

        # Check if the blackboard exists
        if name not in boards:
            return (False, "[ERROR] Board does not exist!")

        with board_lock:
            
            # Update valid state before returning
            if boards[name]["entry_time"] + boards[name]["valid_sec"] <= time.time():

                # Update valid state
                boards[name]["is_valid"] = False

                # Return the data but with invalid message
                return (True, boards[name]["data"], boards[name]["is_valid"], "[WARNING] Successfully read but Data is invalid!")

            # Data still valid
            else:

                # Check for empty data
                if boards[name]["data"] == "":
                    return (True, boards[name]["data"], boards[name]["is_valid"], "[WARNING] Successfully read but data is empty!")

                # Return Read with out problems!
                return (True, boards[name]["data"], boards[name]["is_valid"], "[INFO] Successfully read with valid data!")


    def exposed_get_blackboard_status(self, name):
        """
        Return current state of the given board

        param - {str} - name - Unique name of the board

        return (Successful?,  is_empty, entry_time, is_valid, Message)
        """

        global boards

        # Check if the blackboard exists
        if name not in boards:
            return (False, "[ERROR] Board does not exist!")

        with board_lock:
            
            # Check is the data is empty or not
            if boards[name]["data"] == "":
                is_empty = True
            else:
                is_empty = False

            # Update valid state before returning
            if boards[name]["entry_time"] + boards[name]["valid_sec"] <= time.time():

                # Update valid state
                boards[name]["is_valid"] = False

            # Return with the remaining information
            return (True, is_empty, boards[name]["entry_time"], boards[name]["is_valid"], "[INFO] Successfully read board status!")


    @staticmethod
    def exposed_list_blackboards():
        """
        Simply return a complete list of the blackboards
        
        param - {str} - name - Unique name of the board

        return (Successful?,  list_of_boards, Message)
        """

        global boards

        # Init the list
        list_of_boards = []

        # get all board names
        with board_lock:
            for name in boards:
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

        global boards

        # Check if the blackboard exists
        if name not in boards:
            return (False, "[ERROR] Board does not exist!")

        with board_lock:
                del boards[name]

        self.debug_print()

        return (True, "[INFO] Board successfully deleted.")


    def exposed_delete_all_blackboards(self):
        """
        Delete all existing blackboards!

        param - {str} - name - Unique name of the board

        return (Successful?,  Message)
        """

        global boards

        with board_lock:
            boards = {}

        self.debug_print()
        return (True, "[INFO] Successfully deleted all boards!")

    def log_call(self, ip, port, method, args, return_value):
        Logger.write_in_log([datetime.now(), "Method-Call", ip, port, method, str(args), str(return_value)])

    def debug_print(self):
        """
        TODO Delete
        """
        global boards
        print("\033c", end="")
        print(json.dumps(boards, indent=4, ensure_ascii=False))
        print("\n====================================================\n")
        print("[INFO] To stop the Server please use Ctrl+C")



#=====Main============================================
if __name__ == "__main__":

    # Init the server
    # TODO add port to chose maybe via argparse
    print("[INFO] Starting server...")
    server = ThreadedServer(BlackBoardHost, port=8080)

    Logger.write_in_log([datetime.now(), "Server-Start"])

    # Start the Server
    print("[INFO] Server started. To stop please use Ctrl+C")
    server.start()

    Logger.write_in_log([datetime.now(), "Server-Stop"])



