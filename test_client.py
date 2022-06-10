"""
    Testing the RPyC Module
    Requesting as a Client
    TODO Docstring
"""

# ===== Imports =======================================
import sys
import os
import time

# add custom library location to path
sys.path.append(str(os.path.dirname(os.path.abspath(__file__))) + "/RPyC/rpyc_main_folder")

import rpyc


# ==== Functions ======================================
def get_input_name():
    """
    Function to get the board name form the user
    """
    return input("Please enter the Name of the Board:\t")


# ===== Main ==========================================
if __name__ == "__main__":

    # TODO Add argparse for port and address!!! Please add "localhost" as default

    # Connect to the server
    print("Connecting to Server...")

    # Catch if server is already started.
    try:
        server_handle = rpyc.connect("localhost", 8080).root
    except ConnectionRefusedError:
        print("[ERROR]\tServer is not available! Please start server first.")
        exit()

    # Start Message
    print("Welcome to the Blackboard Client! What do you want to do?")

    # Init
    running = True
    while running:

        # Get Action ID
        action_id = input(
            "0\t-\tCreate Blackboard\n"
            "1\t-\tWrite Blackboard\n"
            "2\t-\tClear Blackboard\n"
            "3\t-\tRead Blackboard\n"
            "4\t-\tGet Status of Blackboard\n"
            "5\t-\tList all Blackboards\n"
            "6\t-\tDelete Blackboard\n"
            "7\t-\tDelete All Blackboards\n\n"
            "Q\t-\tClose Connection & Exit\n\n"
            "Input:\t"
        )

        # print separator
        print("\n====================================================\n")

        # Check if finished
        if action_id == "Q" or action_id == "q":
            running = False
            break

        # Create a Blackboard
        if action_id == "0":
            answer = server_handle.create_blackboard(get_input_name(), input("Insert the Valid Time in Seconds:\t"))
            print(
                "\n"
                f"Message:\t{answer[-1]}"
            )

        # Write to the blackboard
        elif action_id == "1":
            answer = server_handle.display_blackboard(get_input_name(), input("Please insert the Data:\t"))
            print(
                "\n"
                f"Message:\t{answer[-1]}"
            )

        # Clear the Blackboard
        elif action_id == "2":
            answer = server_handle.clear_blackboard(get_input_name())
            print(
                "\n"
                f"Message:\t{answer[-1]}"
            )

        # Read form the blackboard
        elif action_id == "3":
            answer = server_handle.read_blackboard(get_input_name())
            # Check if request was successful
            if answer[0]:
                print(
                    "\n"
                    f"Data:\t\t{answer[1]}\n"
                    f"Is Valid:\t{answer[2]}\n"
                    f"Message:\t{answer[-1]}"
                )
            # If not only display message
            else:
                print(
                    "\n"
                    f"Message:\t{answer[-1]}"
                )

        # Get Blackboard Status
        elif action_id == "4":
            answer = server_handle.get_blackboard_status(get_input_name())
            # Check if request was successful
            if answer[0]:
                print(
                    "\n"
                    f"Is Empty:\t{answer[1]}\n"
                    f"Time Stamp:\t{answer[2]}\n"
                    f"Is Valid:\t{answer[3]}\n"
                    f"Message:\t{answer[-1]}"
                )
            # If not only display message
            else:
                print(
                    "\n"
                    f"Message:\t{answer[-1]}"
                )

        # List all blackboards
        elif action_id == "5":
            answer = server_handle.list_blackboards()
            blackboard_list = ", ".join(answer[1])
            print(
                f"Board-List:\t{blackboard_list}\n"
                f"Message:\t{answer[-1]}"
            )

        # Delete given blackboard
        # TODO Eventuell zuerst prüfen ob es das Blackboard gibt
        elif action_id == "6":
            # Get board name and ask for certanity
            board_name = get_input_name()
            security_question = input(f"Are you sure you want to delete '{board_name}'?\n[Y / N] : ")
            # Check Security Question
            if security_question == "Y":
                answer = server_handle.delete_blackboard(board_name)
                print(
                    "\n"
                    f"Message:\t{answer[-1]}"
                )
            else:
                print(
                    "\n"
                    "Returning..."
                )

        # Delete all Blackboards
        elif action_id == "7":
            security_question = input("Are you sure you want to delete ALL blackboards?\n[Y / n] : ")
            # Check Security Question
            if security_question == "Y":
                answer = server_handle.delete_all_blackboards()
                print(
                    "\n"
                    f"Message:\t{answer[-1]}"
                )
            else:
                print(
                    "\n"
                    "Returning..."
                )

        # Catch wrong input
        else:
            print("Action unknown! Please stick to the given options!")

        # Seperate the terminal from action to action
        # with small delay to make it more understandable for the Human Eye
        time.sleep(0.8)
        print("\n====================================================\n")

    # Exiting application
    print("Closing connection...")
    exit()
