import unittest
import time
from blackboard_server_main import BlackBoardHost

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


if __name__=="__main__":
    unittest.main()