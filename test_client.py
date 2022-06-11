"""
    Testing the RPyC Module
    Requesting as a Client
    TODO Docstring
"""

# ===== Imports =======================================
import socket
import sys
import os
import time
import getopt
import ipaddress

# add custom library location to path
sys.path.insert(0, (str(os.path.dirname(os.path.abspath(__file__))) + "/RPyC/rpyc_main_folder"))

import rpyc


# ==== Functions ======================================
def get_input_name():
    """
    Function to get the board name form the user
    """
    return input("Please enter the Name of the Board:\t")


def show_help():
    """
    TODO Docstring
    """
    print("BlackBoardClient v0.1")
    print("Arguments:")
    print("-s / --server: Set the server ip address and port (default=localhost:8080)")
    print("-h / --help: Show this text")


# ===== Main ==========================================
if __name__ == "__main__":
    try:
        # parse arguments
        try:
            opts, args = getopt.getopt(sys.argv[1:], "s:h", ["server=", "help"])
        except getopt.GetoptError as err:
            print("[Error] Invalid arguments.")
            sys.exit()
        port = 8080
        ip = "localhost"
        if len(args) != 0:
            print("[Error] Invalid arguments.")

        for o, a in opts:
            if o in ("-h", "--help"):
                show_help()
                exit()
            elif o in ("-s", "--server"):
                try:
                    ip, port = a.split(":")
                except:
                    print("[Error] Invalid server address.")
                    exit()
                # validate ip
                try:
                    if ip != "localhost":
                        ipaddress.ip_address(ip)
                except:
                    print("[Error] Invalid server ip address.")
                    exit()
                # validate port
                try:
                    port = int(port)
                except:
                    print("[Error] Invalid server port number.")
                    exit()
                if port < 0 or port > 49151:
                    print("[Error] Server port number out of range.")
                    exit()

        # Connect to the server
        print("[INFO] Connecting to Server...")
        server_handle = rpyc.connect(ip, port).root


        # Start Message
        print("Welcome to the Blackboard Client! What do you want to do?")

        # Init
        running = True

    except Exception as e:
        if isinstance(e, ConnectionRefusedError) or isinstance(e, socket.timeout):
            print("[ERROR] Server is not available! Please start server first.")
            exit()
        else:
            print("[ERROR] An unknown error occurred. Closing the application.")
            exit()
    except KeyboardInterrupt:
        print("[INFO] Stopped connection process.")
        exit()

    try:
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
            # TODO Eventuell zuerst prüfen, ob es das Blackboard gibt
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

    except Exception as e:
        if isinstance(e, EOFError) and e.args[0].args[0] == 10054:
            print("[ERROR] Server closed the connection! Please restart the server. Closing the application.")
            exit()
        else:
            print("[ERROR] An unknown error occurred. Closing the application.")
            exit()
    print("[INFO] Closing connection...")