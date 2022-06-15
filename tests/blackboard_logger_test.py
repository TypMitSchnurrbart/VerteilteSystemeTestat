import unittest
import os
import src.logger as logger


class LoggerTest(unittest.TestCase):
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


if __name__ == "__main__":
    unittest.main()
