import unittest
import os
import src.logger as logger

class LoggerTest(unittest.TestCase):
    
    def setUp(self):
        self.filename = 'log.csv'
        if os.path.isfile(self.filename):
            os.remove(self.filename)

        fileExists = os.path.isfile(self.filename)
        self.assertFalse(fileExists)

    def tearDown(self):
        fileExists = os.path.isfile(self.filename)
        self.assertTrue(fileExists)
    

    def test_write_in_log(self):
        testitems = ["Hallo", "Welt"]    
        logger.write_in_log(testitems)
        fileExists = os.path.isfile(self.filename)
        self.assertTrue(fileExists)

        fileSize1 = os.path.getsize(self.filename)

        logger.write_in_log(testitems)
        fileSize2 = os.path.getsize(self.filename)

        self.assertTrue(fileSize1 < fileSize2)

if __name__=="__main__":
    unittest.main()

        

    
    