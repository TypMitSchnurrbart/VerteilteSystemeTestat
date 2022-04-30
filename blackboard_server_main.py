"""
    Testing the RPyC Module
    Hosting a Server

    TODO

        - maybe return dict everywhere instead of tuples!
"""

#=====Imports=========================================
import rpyc
from rpyc.utils.server import ThreadedServer

import time
import json
from threading import Lock


#=====Global == But may want to use JSON instead of global param!==
boards = {}

# Created lock, perhaps think of another solution than creating as "global" lock
board_lock = Lock()

#=====Server Class====================================
class BlackBoardHost(rpyc.Service):

    def exposed_create_blackboard(self, name, valid_sec):
        """
        Create a new blackbox by adding it to the JSON Database? Dict in RAM?

        TODO
            - Decide storage technology

        param - {str} - name - Name of the new blackbox
        param - {float} - valid_sec - Time the Data in the blackbox shall be valid 

        return (Successful?, Message)
        """

        global boards

        # Check for correct types
        try:
            valid_sec = float(valid_sec)
        except ValueError():
            return (False, "Invalid Parameters! Please give Valid Time in Seconds as Float or Int")

        with board_lock:
            # Check if name already given
            if name not in boards:

                # Init the new blackboard
                new_blackboard = {
                    "name" : name,
                    "valid_sec" : valid_sec,
                    "entry_time" : time.time(),
                    "is_valid" : True,
                    "data" : ""
                }

                # Add to boards
                # TODO Maybe write to a JSON instead
                boards[name] = new_blackboard

            else:
                return (False, f"Board Name '{name}' already exists")

        # TODO Delete for debug
        self.debug_print()

        return (True, f"Successfully created Board {name}!")


    def exposed_display_blackboard(self, name, data):
        """
        Update the data of the blackboard and refresh the timestamp

        TODO
            - ensure semaphore or what else is free!

        param - {str} - name - Name of the EXISTING Blackboard
        param - {str?} - data - Given data written to blackboard

        return (Successful?, Message)
        """

        global boards

        with board_lock:
        # Check if the blackboard exists
            if name in boards:

                # Update the board information
                # TODO Consistency
                boards[name]["entry_time"] = time.time()
                boards[name]["data"] = data
                boards[name]["is_valid"] = True

            # If not return error
            else:
                return (False, "Board does not exist!")

        # TODO delte
        self.debug_print()

        return (True, "Blackboard successfully updated!")
        

    def exposed_clear_blackboard(self, name):
        """
        Clear the given board data and set to invalid status!

        TODO
            - ensure Semaphore or what si free

        param - {str} - name - Unique name of the board

        return (Successful?, Message)
        """

        global boards

        with board_lock:

            # Check if the blackboard exists
            if name in boards:

                # Update the board information
                # TODO Consistency
                boards[name]["data"] = ""
                boards[name]["is_valid"] = False

            # If not return error
            else:
                return (False, "Board does not exist!")

        # TODO delte
        self.debug_print()

        return (True, "Blackboard successfully cleared!")


    def exposed_read_blackboard(self, name):
        """
        Return the data and valid state of the given board

        param - {str} - name - Unique name of the board

        return (Successful?, data, is_valid, Message)
        """

        global boards

        with board_lock:
            # Check if board exists
            if name in boards:
            
                # Update valid state before returning
                if boards[name]["entry_time"] + boards[name]["valid_sec"] <= time.time():

                    # Update valid state
                    boards[name]["is_valid"] = False

                    # Return the data but with invalid message
                    return (True, boards[name]["data"], boards[name]["is_valid"], "Successfully read but Data is invalid!")

                # Data still valid
                else:

                    # Check for empty data
                    if boards[name]["data"] == "":
                        return (True, boards[name]["data"], boards[name]["is_valid"], "Successfully read but data is empty!")

                    # Return Read with out problems!
                    return (True, boards[name]["data"], boards[name]["is_valid"], "Successfully read with valid data!")

            else:
                return (False, 0, False, "Blackboard does not exist!")


    def exposed_get_blackboard_status(self, name):
        """
        Return current state of the given board

        param - {str} - name - Unique name of the board

        return (Successful?,  is_empty, entry_time, is_valid, Message)
        """

        global boards

        with board_lock:
            # Check if board exists
            if name in boards:
            
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
                return (True, is_empty, boards[name]["entry_time"], boards[name]["is_valid"], "Successfully read board status!")

            else:
                return (False, False, 0, False, "Board does not exist!")



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
            return (True, list_of_boards, "No Boards found! Please create one first!")

        return (True, list_of_boards, "Successful read of Blackboard List!")


    def exposed_delete_blackboard(self, name):
        """
        Delete the given board

        param - {str} - name - Unique name of the message

        param - {str} - name - Unique name of the board

        return (Successful?,  Message)
        """

        global boards

        with board_lock:
            if name in boards:
                del boards[name]

            else:
                return (False, "Board does not exist!")

        self.debug_print()

        return (True, "Board successfully deleted.")


    @staticmethod
    def exposed_delete_all_blackboards():
        """
        Delete all existing blackboards!

        param - {str} - name - Unique name of the board

        return (Successful?,  Message)
        """

        global boards

        with board_lock:
            boards = {}
            return (True, "Successfully deleted all boards!")

        
    def write_to_log():
        """
        Write the need information to the log file
        """
        
        pass



    def debug_print(self):
        """
        TODO Delete
        """
        global boards
        print("\033c", end="")
        print(json.dumps(boards, indent=4))
        print("\n====================================================\n")

#=====Main============================================
if __name__ == "__main__":

    # Init the server
    # TODO add port to chose maybe via argparse
    server = ThreadedServer(BlackBoardHost, port = 8080)

    # Start the Server
    server.start()
