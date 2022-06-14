"""
    RPC Client:
    Contains the main-function of the client and smaller additional functions.
"""

# ===== Imports =======================================
import socket
import sys
import time
import getopt
import ipaddress
import rpyc


# ==== Functions ======================================
def get_input_name() -> str:
    """
    Function to get the Blackboard name form the user.
    return blackboard_name
    """
    return input("Please enter the name of the Board:\t")


def show_help() -> None:
    """
    Print a help text on the console.
    """
    print("BlackBoardClient v0.1")
    print("Arguments:")
    print("-s / --server: Set the server ip address and port (default=localhost:8080)")
    print("-h / --help: Show this text")


# ===== Main ==========================================
def main(argv: list) -> None:
    """
    The main-function of the client.
    Parses the given arguments to determine the server ip-address and port (default: localhost:8080).
    Afterward it is tried to establish a connection to the server.
    If the connection is established the user can use the server functions freely via console inputs.
    If the connection can't be established, the connection is lost or the client is stopped with Ctrl+C the program
    is stopped with a corresponding message.

    param - {str} - argv - A list of the arguments
    """
    connection = None

    try:
        # parse arguments
        try:
            opts, args = getopt.getopt(argv, "s:h", ["server=", "help"])
        except getopt.GetoptError as err:
            print("[ERROR] Invalid arguments.")
            sys.exit()
        port = 8080
        ip = "localhost"
        if len(args) != 0:
            print("[ERROR] Invalid arguments.")

        for o, a in opts:
            if o in ("-h", "--help"):
                show_help()
                exit()
            elif o in ("-s", "--server"):
                try:
                    ip, port = a.split(":")
                except:
                    print("[ERROR] Invalid server address.")
                    exit()
                # validate ip
                try:
                    if ip != "localhost":
                        ipaddress.ip_address(ip)
                except:
                    print("[ERROR] Invalid server ip address.")
                    exit()
                # validate port
                try:
                    port = int(port)
                except:
                    print("[ERROR] Invalid server port number.")
                    exit()
                if port < 0 or port > 49151:
                    print("[ERROR] Server port number out of range.")
                    exit()

        # Connect to the server
        print("[INFO] Connecting to Server...")
        connection = rpyc.connect(ip, port).root

        # Start message
        print("Welcome to the Blackboard client! What do you want to do?")

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

    # Init
    running = True
    try:
        while running:

            # Get action id
            action_id = input(
                "0\t-\tCreate Blackboard\n"
                "1\t-\tWrite Blackboard\n"
                "2\t-\tClear Blackboard\n"
                "3\t-\tRead Blackboard\n"
                "4\t-\tGet status of Blackboard\n"
                "5\t-\tList all Blackboards\n"
                "6\t-\tDelete Blackboard\n"
                "7\t-\tDelete all Blackboards\n\n"
                "Q\t-\tClose connection & exit\n\n"
                "Input:\t"
            )

            # Print separator
            print("\n====================================================\n")

            # Check if finished
            if action_id in ("Q", "q"):
                running = False
                break

            # Create a Blackboard
            if action_id == "0":
                answer = connection.create_blackboard(get_input_name(), input("Insert the valid time in seconds:\t"))
                print(
                    "\n"
                    f"Message:\t{answer[-1]}"
                )

            # Write to the Blackboard
            elif action_id == "1":
                answer = connection.display_blackboard(get_input_name(), input("Please insert the data:\t"))
                print(
                    "\n"
                    f"Message:\t{answer[-1]}"
                )

            # Clear the Blackboard
            elif action_id == "2":
                answer = connection.clear_blackboard(get_input_name())
                print(
                    "\n"
                    f"Message:\t{answer[-1]}"
                )

            # Read form the Blackboard
            elif action_id == "3":
                answer = connection.read_blackboard(get_input_name())
                # Check if request was successful
                if answer[0]:
                    if answer[1] is None:
                        data = ""
                    else:
                        data = answer[1]
                    print(
                        "\n"
                        f"Data:\t\t{data}\n"
                        f"Is valid:\t{answer[2]}\n"
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
                answer = connection.get_blackboard_status(get_input_name())
                # Check if request was successful
                if answer[0]:
                    print(
                        "\n"
                        f"Is empty:\t{answer[1]}\n"
                        f"Time stamp:\t{answer[2]}\n"
                        f"Is valid:\t{answer[3]}\n"
                        f"Message:\t{answer[-1]}"
                    )
                # If not only display message
                else:
                    print(
                        "\n"
                        f"Message:\t{answer[-1]}"
                    )

            # List all Blackboards
            elif action_id == "5":
                answer = connection.list_blackboards()
                # Check if request was successful
                if answer[0]:
                    blackboard_list = ", ".join(answer[1])
                    print(
                        f"Board list:\t{blackboard_list}\n"
                        f"Message:\t{answer[-1]}"
                    )
                else:
                    print(
                        "\n"
                        f"Message:\t{answer[-1]}"
                    )

            # Delete given Blackboard
            elif action_id == "6":
                # Get Board name and ask for certainty
                board_name = get_input_name()
                security_question = input(f"Are you sure you want to delete '{board_name}'?\n[Y / N] : ")
                # Check Security Question
                if security_question in ("Y", "y"):
                    answer = connection.delete_blackboard(board_name)
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
                security_question = input("Are you sure you want to delete ALL Blackboards?\n[Y / N] : ")
                # Check Security Question
                if security_question in ("Y", "y"):
                    answer = connection.delete_all_blackboards()
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

            # Separate the terminal from action to action
            # with small delay making it more understandable for the Human Eye
            time.sleep(0.8)
            print("\n====================================================\n")

    except Exception as e:
        if isinstance(e, EOFError):
            print("[ERROR] Server closed the connection! Please restart the server. Closing the application.")
            exit()
        elif isinstance(e, TimeoutError):
            print("[ERROR] Timeout! Closing the application.")
            exit()
        elif isinstance(e, AttributeError):
            print("[ERROR] The Server does not implement the blackboard functions. Please ensure the server address "
                  "is correct.")
            exit()
        else:
            print("[ERROR] An unknown error occurred. Closing the application.")
            exit()
    except KeyboardInterrupt:
        # Print separator
        print("\n\n====================================================\n")
    print("[INFO] Closing connection...")


if __name__ == "__main__":
    main(sys.argv[1:])
