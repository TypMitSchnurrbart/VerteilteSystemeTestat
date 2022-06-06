"""
Unit tests for the functionalities in the Server
"""

import unittest
import blackboard_server_main as bb

class ServerTests(unittest.TestCase):

    def setUp(self):
        # blackboard host as basis for calling the blackboard functions locally
        self.blackboard_host = bb.BlackBoardHost()
        self.assertEqual(bb.boards, {})

    def tearDown(self):
        # cleanup after test
        self.blackboard_host.exposed_delete_all_blackboards()
        self.assertEqual(bb.boards, {})


class delete_create_test(ServerTests):

    def test_create_delete_blackboard(self):
        code, msg = self.blackboard_host.exposed_create_blackboard("test", 1)
        self.assertEqual(code, True)
        self.assertEqual(msg, "Successfully created Board test!")
        self.assertIsNotNone(bb.boards["test"])

        code, msg = self.blackboard_host.exposed_create_blackboard("", 1)
        self.assertEqual(code, True)

        code, msg = self.blackboard_host.exposed_create_blackboard("test", 1)
        self.assertEqual(code, False)

        code, msg = self.blackboard_host.exposed_create_blackboard("new", "test")
        self.assertEqual(code, False)
        self.assertRaises(KeyError, lambda : bb.boards["new"])

        code, msg = self.blackboard_host.exposed_delete_blackboard("new")
        self.assertEqual(code, False)

        code, msg = self.blackboard_host.exposed_delete_blackboard("test")
        self.assertEqual(code, True)
        self.assertRaises(KeyError, lambda : bb.boards["test"])


    def test_display_clear_blackboard(self):
        self.blackboard_host.exposed_create_blackboard("test", 1)
        self.blackboard_host.exposed_display_blackboard("test", "Testdata")
        self.assertEqual(bb.boards["test"]["data"], "Testdata")

        code, msg = self.blackboard_host.exposed_clear_blackboard("test")
        self.assertEqual(code, True)
        self.assertEqual(bb.boards["test"]["data"], "")


if __name__ == "__main__":
    unittest.main()
