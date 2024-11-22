import unittest
from unittest.mock import patch, MagicMock
import os
import json
from FileBackup import save_config, upload_to_s3, config_file


class TestFileBackupSystem(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        
        cls.test_directory = "test_directory"
        cls.test_config = {
            "directory": cls.test_directory,
            "interval": 1,
            "email_notifications": True,
        }
        cls.config_path = config_file

        # Create a temporary directory for testing
        os.makedirs(cls.test_directory, exist_ok=True)

        # Create test files
        cls.test_file = os.path.join(cls.test_directory, "test_file.txt")
        with open(cls.test_file, "w") as f:
            f.write("This is a test file.")

    @classmethod
    def tearDownClass(cls):
        
        # Remove the test directory and files
        if os.path.exists(cls.test_directory):
            for root, dirs, files in os.walk(cls.test_directory, topdown=False):
                for name in files:
                    os.remove(os.path.join(root, name))
                for name in dirs:
                    os.rmdir(os.path.join(root, name))
            os.rmdir(cls.test_directory)

        # Remove test config file if created
        if os.path.exists(cls.config_path):
            os.remove(cls.config_path)

    def test_save_config(self):
        
        save_config(**self.test_config)
        self.assertTrue(os.path.exists(self.config_path))

        with open(self.config_path, "r") as f:
            config = json.load(f)

        self.assertEqual(config, self.test_config)

    @patch("boto3.client")
    def test_upload_to_s3(self, mock_boto3_client):
        
        mock_s3 = MagicMock()
        mock_boto3_client.return_value = mock_s3

        file_counter = [0]
        upload_to_s3(self.test_file, email_notifications=False, file_counter=file_counter)

        mock_s3.upload_file.assert_called_once_with(
            self.test_file, "", os.path.basename(self.test_file)
        )
        self.assertEqual(file_counter[0], 1)


if __name__ == "__main__":
    unittest.main()
