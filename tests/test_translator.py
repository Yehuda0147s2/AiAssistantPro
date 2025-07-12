import unittest
import os
import tempfile
import shutil
from translator import translate_srt

class TestTranslator(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.srt_path = os.path.join(self.temp_dir, "test.srt")
        with open(self.srt_path, "w") as f:
            f.write("1\n00:00:01,000 --> 00:00:02,000\nHello")

    def tearDown(self):
        shutil.rmtree(self.temp_dir)

    def test_translate_srt(self):
        translated_srt_path = translate_srt(self.srt_path, "Spanish", self.temp_dir)
        self.assertTrue(os.path.exists(translated_srt_path))

if __name__ == "__main__":
    unittest.main()
