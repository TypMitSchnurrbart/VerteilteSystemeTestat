"""
    Testing the RPyC Module
    Requesting as a Client
"""

#===== Imports =======================================
import rpyc
import time

#==== Functions ======================================
def get_input_name():
    """
    Function to get the board name form the user
    """

    return input("Please enter the Name of the Board:\t")

#===== Main ==========================================
if __name__ == "__main__":


    # Connect to the server
    print("Connecting to Server...")

    # Catch if not working!
    try:
        server_handle = rpyc.connect("localhost", 8080).root
    except ConnectionRefusedError:
        print("[ERROR]\tServer is not avalailable! Please start server first.")
        exit()
    


    # Start Message
    print("""Welcome to the Blackboard Client! What do you want to do?\n""")

    # Init
    running = True

    while running:

        # Get Action ID
        action_id = input("""\n
        Create Blackboard\t\t-\t0
        Write Blackboard\t\t-\t1
        Clear Blackboard\t\t-\t2
        Read Blackboard\t\t\t-\t3
        Get Status of Blackboard\t-\t4
        List all Blackboards\t\t-\t5
        Delete Blackboard\t\t-\t6
        Delete All Blackboards\t\t-\t7\n
        Close Connection & Exit\t\t-\tQ\nInput:\t""")

        # print separator
        print("\n====================================================\n")

        # Check if finished
        if action_id == "Q" or action_id == "q":
            running = False
            break


        # Create a Blackboard
        if action_id == "0":
            answer = server_handle.create_blackboard(get_input_name(), input("Please insert the Valid Time in Seconds:\t"))
            print(answer[-1])
        

        # Write to the blackboard
        elif action_id == "1":
            answer = server_handle.display_blackboard(get_input_name(), input("Please insert the Data:\n"))
            print(answer[-1])
        

        # Clear the Blackboard
        elif action_id == "2":
            answer = server_handle.clear_blackboard(get_input_name())
            print(answer[-1])
        

        # Read form the blackboard
        elif action_id == "3":
            answer = server_handle.read_blackboard(get_input_name())
            
            # Check if request was successful
            if answer[0]:
                print(f"""
                Data:\t\t{answer[1]}
                Is Valid:\t{answer[2]}
                Message:\t{answer[-1]}""")

            # If not only display message
            else:
                print(answer[-1])
        

        # Get Blackboard Status
        elif action_id == "4":
            answer = server_handle.get_blackboard_status(get_input_name())
            
            # Check if request was successful
            if answer[0]:
                print(f"""
                Is Empty:\t{answer[1]}
                Time Stamp:\t{answer[2]}
                Is Valid:\t{answer[3]}
                Message:\t{answer[-1]}""")

            # If not only display message
            else:
                print(answer[-1])
        

        # List all blackboards
        elif action_id == "5":
            answer = server_handle.list_blackboards()
            print(f"""List:\t\t{answer[1]}\nMessage:\t{answer[-1]}""")
        

        # Delete given blackboard
        elif action_id == "6":

            security_question = input("Are you sure? [Y / n] : ")

            # Check Security Question
            if security_question == "Y":
                answer = server_handle.delete_blackboard(get_input_name())
                print(answer[-1])
            else:
                print("Returning...\n")
        

        # Delete all Blackboards
        elif action_id == "7":

            security_question = input("Are you sure? [Y / n] : ")

            # Check Security Question
            if security_question == "Y":
                answer = server_handle.delete_all_blackboards()
                print(answer[-1])
            else:
                print("Returning...\n")
        
        # Catch wrong input
        else:
            print("Action unknown! Please stick to the given options!")

        # Seperate the terminal from action to action
        time.sleep(1)
        print("\n====================================================\n")


    # Exiting application
    print("Closing connection...")
    exit()