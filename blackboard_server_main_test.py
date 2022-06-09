import unittest
import time
from blackboard_server_main import BlackBoardHost
import blackboard_server_main as bb


"""
unittests checking correct return values
"""
class ServerTest(unittest.TestCase):
    

    def test_exposed_create_blackboard(self):
        testhost = BlackBoardHost()

        #Valid Testcase
        result = testhost.exposed_create_blackboard("TestBlackboard", 1000)
        self.assertTrue(result[0])
        self.assertEqual("[INFO] Successfully created Board TestBlackboard!", result[1])

        # Doubled Creation
        result = testhost.exposed_create_blackboard("TestBlackboard", 1000)
        self.assertFalse(result[0])
        self.assertEqual("[ERROR] Board Name 'TestBlackboard' already exists", result[1])

        # no valid time
        result = testhost.exposed_create_blackboard(123, "Hallo")
        self.assertFalse(result[0])
        self.assertEqual("[ERROR] Invalid Parameters! Please give Valid Time in Seconds as Float or Int",result[1])

        # negative Time
        result = testhost.exposed_create_blackboard("Hallo", -500)
        self.assertFalse(result[0])
        self.assertEqual("[ERROR] The valid time must be greater than 0! Given value: -500.0",result[1])

    def test_exposed_display_blackboard(self):
        testhost = BlackBoardHost()

        testhost.exposed_create_blackboard("TestBoard", 1000)

        # Existing Blackboard
        result = testhost.exposed_display_blackboard("TestBoard", "DataString")
        self.assertTrue(result[0])
        self.assertEqual("[INFO] Blackboard successfully updated!",result[1])

        # Not existing Blackboard
        result = testhost.exposed_display_blackboard("NotExistingBlackboard", "DataString")
        self.assertFalse(result[0])
        self.assertEqual("[ERROR] Board does not exist!", result[1])


    def test_exposed_clear_blackboard(self):
        testhost = BlackBoardHost()

        test = testhost.exposed_create_blackboard("TestBoard", 1000)
        testhost.exposed_display_blackboard("TestBoard", "DataString")


        # Existing Blackboard
        result = testhost.exposed_clear_blackboard("TestBoard")
        self.assertTrue(result[0])
        self.assertEqual("[INFO] Blackboard successfully cleared!",result[1])

        # Not existing Blackboard
        result = testhost.exposed_clear_blackboard("NotExistingBlackboard")
        self.assertFalse(result[0])
        self.assertEqual("[ERROR] Board does not exist!", result[1])

    def test_exposed_read_blackboard(self):
        testhost = BlackBoardHost()
        testhost.exposed_delete_all_blackboards()
        testhost.exposed_create_blackboard("TestBoard", 1000)
        testhost.exposed_display_blackboard("TestBoard", "DataString")

        testhost.exposed_create_blackboard("EmptyBlackboard", 1000)

        testhost.exposed_create_blackboard("InvalidBlackboard", 1)
        testhost.exposed_display_blackboard("InvalidBlackboard", "SomeData")
        time.sleep(2)

        result = testhost.exposed_read_blackboard("TestBoard")
        self.assertTrue(result[0])
        #Data
        self.assertEqual("DataString", result[1])
        #Validity
        self.assertTrue(result[2])
        #Message
        self.assertEqual("[INFO] Successfully read with valid data!", result[3])

        result = testhost.exposed_read_blackboard("EmptyBlackboard")
        self.assertTrue(result[0])
        #Data
        self.assertEqual("", result[1])
        #Validity
        self.assertTrue(result[2])
        #Message
        self.assertEqual("[WARNING] Successfully read but data is empty!", result[3])

        result = testhost.exposed_read_blackboard("InvalidBlackboard")
        self.assertTrue(result[0])
        #Data
        self.assertEqual("SomeData", result[1])
        #Validity
        self.assertFalse(result[2])
        #Message
        self.assertEqual("[WARNING] Successfully read but Data is invalid!", result[3])

        result = testhost.exposed_read_blackboard("NotExistingBlackboard")
        self.assertFalse(result[0])
        self.assertEqual("[ERROR] Board does not exist!", result[1])

    def test_exposed_get_blackboard_status(self):
        testhost = BlackBoardHost()
        testhost.exposed_create_blackboard("TestBoard", 1000)
        testhost.exposed_display_blackboard("TestBoard", "DataString")

        result = testhost.exposed_get_blackboard_status("TestBoard")
        self.assertTrue(result[0])
        #Emptyness
        self.assertFalse(result[1])
        #Validity
        self.assertTrue(result[3])
        self.assertEqual("[INFO] Successfully read board status!", result[4])

        result = testhost.exposed_get_blackboard_status("NotExistingBlackboard")
        self.assertFalse(result[0])
        self.assertEqual("[ERROR] Board does not exist!", result[1])

    def test_exposed_list_blackboards(self):
        testhost = BlackBoardHost()
        testhost.exposed_delete_all_blackboards()
        result = testhost.exposed_list_blackboards()
        result2 = testhost.exposed_list_blackboards()

        self.assertTrue(result[0])
        self.assertEqual("[ERROR] No Boards found! Please create one first!", result[2])

        testhost.exposed_create_blackboard("TestBoard", 1000)
        testhost.exposed_create_blackboard("AnotherTestBoard", 1000)

        result = testhost.exposed_list_blackboards()
        self.assertTrue(result[0])
        self.assertEqual("[INFO] Successful read of Blackboard List!", result[2])


    def test_exposed_delete_blackboard(self):
        testhost = BlackBoardHost()
        testhost.exposed_create_blackboard("TestBoard", 1000)
        testhost.exposed_display_blackboard("TestBoard", "DataString")

        result = testhost.exposed_delete_blackboard("TestBoard")
        self.assertTrue(result[0])
        self.assertEqual("[INFO] Board successfully deleted.", result[1])

        result = testhost.exposed_delete_blackboard("NotExistingBlackboard")
        self.assertFalse(result[0])
        self.assertEqual("[ERROR] Board does not exist!", result[1])

    def test_exposed_delete_all_blackboards(self):
        testhost = BlackBoardHost()
        testhost.exposed_create_blackboard("TestBoard", 1000)
        testhost.exposed_display_blackboard("TestBoard", "DataString")

        testhost.exposed_create_blackboard("AnotherTestBoard", 1000)
        
        result = testhost.exposed_delete_all_blackboards()
        self.assertTrue(result[0])

        self.assertEqual("[INFO] Successfully deleted all boards!", result[1])

    def test_write_to_log(self):
        pass

    def test_debug_print(self):
        pass


"""
Test cases focussing on checking the consistency of the global state of the blackboard
"""

class StateConsistencyTest(unittest.TestCase):

    def setUp(self):
        # blackboard host as basis for calling the blackboard functions locally
        self.blackboard_host = BlackBoardHost()
        self.blackboard_host.exposed_delete_all_blackboards()
        self.assertEqual(bb.boards, {})

    def tearDown(self):
        # cleanup after test
        self.blackboard_host.exposed_delete_all_blackboards()
        self.assertEqual(bb.boards, {})


    def test_create_delete_blackboard(self):
        code, msg = self.blackboard_host.exposed_create_blackboard("test", 1)
        self.assertEqual(code, True)
        self.assertEqual(msg, "[INFO] Successfully created Board test!")
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

if __name__=="__main__":
    unittest.main()
