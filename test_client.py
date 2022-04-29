"""
    Testing the RPyC Module
    Requesting as a Client
"""

import rpyc

server_handle = rpyc.connect("localhost", 8080)

print(server_handle.root.create_blackboard("test_name_juergen", 17))
print(server_handle.root.display_blackboard("test_name_juergen", "Hallo!"))