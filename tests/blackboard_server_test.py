import unittest
from blackboard_server import BlackBoardHost
import time
import os


class ServerTest(unittest.TestCase):
    filename = 'log.csv'
    backup_filename = 'log_backup.csv'
    backup_exists = False

    @classmethod
    def setUpClass(cls):
        # Remove random backup file
        if os.path.isfile(cls.backup_filename):
            os.remove(cls.backup_filename)

        # Save Log
        cls.backup_exists = os.path.isfile(cls.filename)
        if cls.backup_exists:
            os.rename(cls.filename, cls.backup_filename)

    @classmethod
    def tearDownClass(cls):
        # Restore Log
        os.remove(cls.filename)
        if cls.backup_exists:
            os.rename(cls.backup_filename, cls.filename)

    def setUp(self):
        self.host = BlackBoardHost()
        self.host._BlackBoardHost__client_address = ('123.123.123.123', 52321)

    def tearDown(self):
        self.host.exposed_delete_all_blackboards()

    def test_on_connect(self):
        pass

    def test_on_disconnect(self):
        pass

    def test_exposed_create_blackboard(self):
        # Valid Testcase
        result = self.host.exposed_create_blackboard("TestBlackboard", 1000)
        self.assertTrue(result[0])
        self.assertEqual("[INFO] Successfully created Board 'TestBlackboard'!", result[1])

        # Doubled Creation
        result = self.host.exposed_create_blackboard("TestBlackboard", 1000)
        self.assertFalse(result[0])
        self.assertEqual("[ERROR] Board name 'TestBlackboard' already exists!", result[1])

        # No valid time
        result = self.host.exposed_create_blackboard(123, "Hallo")
        self.assertFalse(result[0])
        self.assertEqual("[ERROR] Invalid parameters! Please give valid time in seconds as Float or Int!", result[1])

        # Negative Time
        result = self.host.exposed_create_blackboard("Hallo", -500)
        self.assertFalse(result[0])
        self.assertEqual("[ERROR] The valid time must be greater or equal to 0! Given value: -500.0.", result[1])

    def test_exposed_display_blackboard(self):
        self.host.exposed_create_blackboard("TestBoard", 1000)

        # Existing Blackboard
        result = self.host.exposed_display_blackboard("TestBoard", "DataString")
        self.assertTrue(result[0])
        self.assertEqual("[INFO] Board successfully updated!", result[1])

        # Not existing Blackboard
        result = self.host.exposed_display_blackboard("NotExistingBlackboard", "DataString")
        self.assertFalse(result[0])
        self.assertEqual("[ERROR] Board does not exist!", result[1])

    def test_exposed_clear_blackboard(self):
        self.host.exposed_create_blackboard("TestBoard", 1000)
        self.host.exposed_display_blackboard("TestBoard", "DataString")

        # Existing Blackboard
        result = self.host.exposed_clear_blackboard("TestBoard")
        self.assertTrue(result[0])
        self.assertEqual("[INFO] Board successfully cleared!", result[1])

        # Not existing Blackboard
        result = self.host.exposed_clear_blackboard("NotExistingBlackboard")
        self.assertFalse(result[0])
        self.assertEqual("[ERROR] Board does not exist!", result[1])

    def test_exposed_read_blackboard(self):
        self.host.exposed_create_blackboard("TestBoard", 1000)
        self.host.exposed_display_blackboard("TestBoard", "DataString")

        self.host.exposed_create_blackboard("EmptyBlackboard", 1000)

        self.host.exposed_create_blackboard("InvalidBlackboard", 1)
        self.host.exposed_display_blackboard("InvalidBlackboard", "SomeData")
        time.sleep(2)

        result = self.host.exposed_read_blackboard("TestBoard")
        self.assertTrue(result[0])
        # Data
        self.assertEqual("DataString", result[1])
        # Validity
        self.assertTrue(result[2])
        # Message
        self.assertEqual("[INFO] Successfully read with valid data!", result[3])

        result = self.host.exposed_read_blackboard("EmptyBlackboard")
        self.assertTrue(result[0])
        # Data
        self.assertEqual(None, result[1])
        # Validity -> Empty Blackboards are considered to be invalid
        self.assertFalse(result[2])
        # Message
        self.assertEqual("[WARNING] Successfully read but data is empty!", result[3])

        result = self.host.exposed_read_blackboard("InvalidBlackboard")
        self.assertTrue(result[0])
        # Data
        self.assertEqual("SomeData", result[1])
        # Validity
        self.assertFalse(result[2])
        # Message
        self.assertEqual("[WARNING] Successfully read but data is invalid!", result[3])

        result = self.host.exposed_read_blackboard("NotExistingBlackboard")
        self.assertFalse(result[0])
        self.assertEqual("[ERROR] Board does not exist!", result[1])

    def test_exposed_get_blackboard_status(self):
        self.host.exposed_create_blackboard("TestBoard", 1000)
        self.host.exposed_display_blackboard("TestBoard", "DataString")
        self.host.exposed_create_blackboard("Empty", 0.001)

        time.sleep(0.1)
        result = self.host.exposed_get_blackboard_status("Empty")
        # Emptiness
        self.assertTrue(result[1])
        # Invalidity
        self.assertFalse(result[3])

        result = self.host.exposed_get_blackboard_status("TestBoard")
        self.assertTrue(result[0])
        # Emptiness
        self.assertFalse(result[1])
        # Validity
        self.assertTrue(result[3])
        self.assertEqual("[INFO] Successfully read Board status!", result[4])

        result = self.host.exposed_get_blackboard_status("NotExistingBlackboard")
        self.assertFalse(result[0])
        self.assertEqual("[ERROR] Board does not exist!", result[1])

    def test_exposed_list_blackboards(self):
        self.host.exposed_delete_all_blackboards()
        result = self.host.exposed_list_blackboards()

        self.assertTrue(result[0])
        self.assertEqual("[WARNING] No Boards found! Please create one first!", result[2])

        self.host.exposed_create_blackboard("TestBoard", 1000)
        self.host.exposed_create_blackboard("AnotherTestBoard", 1000)

        result = self.host.exposed_list_blackboards()
        self.assertTrue(result[0])
        self.assertEqual("[INFO] Successful read of Board list!", result[2])

    def test_exposed_delete_blackboard(self):
        self.host.exposed_create_blackboard("TestBoard", 1000)
        self.host.exposed_display_blackboard("TestBoard", "DataString")

        result = self.host.exposed_delete_blackboard("TestBoard")
        self.assertTrue(result[0])
        self.assertEqual("[INFO] Board successfully deleted!", result[1])

        # Not sure whether it's a good practice to check additionally
        result = self.host.exposed_get_blackboard_status("TestBoard")
        self.assertFalse(result[0])
        self.assertEqual("[ERROR] Board does not exist!", result[1])

        result = self.host.exposed_delete_blackboard("NotExistingBlackboard")
        self.assertFalse(result[0])
        self.assertEqual("[ERROR] Board does not exist!", result[1])

    def test_exposed_delete_all_blackboards(self):
        self.host.exposed_create_blackboard("TestBoard", 1000)
        self.host.exposed_display_blackboard("TestBoard", "DataString")

        self.host.exposed_create_blackboard("AnotherTestBoard", 1000)

        result = self.host.exposed_delete_all_blackboards()
        self.assertTrue(result[0])

        self.assertEqual("[INFO] Successfully deleted all Boards!", result[1])

        # Additional check
        result = self.host.exposed_get_blackboard_status("TestBoard")
        self.assertFalse(result[0])
        self.assertEqual("[ERROR] Board does not exist!", result[1])

    def test_log_call(self):
        pass

    def test_load_boards(self):
        pass

    def test_save_boards(self):
        pass


if __name__ == "__main__":
    unittest.main()
