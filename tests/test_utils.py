import unittest
import os
import tempfile
import shutil
from utils import create_temp_dir, cleanup_temp_files, format_time

class TestUtils(unittest.TestCase):
    def test_create_temp_dir(self):
        temp_dir = create_temp_dir()
        self.assertTrue(os.path.isdir(temp_dir))
        shutil.rmtree(temp_dir)

    def test_cleanup_temp_files(self):
        temp_dir = tempfile.mkdtemp()
        cleanup_temp_files([temp_dir])
        self.assertFalse(os.path.exists(temp_dir))

    def test_format_time(self):
        self.assertEqual(format_time(61), "01:01")
        self.assertEqual(format_time(3661), "01:01:01")

if __name__ == "__main__":
    unittest.main()
