import unittest
import os
import tempfile
import shutil
from video_handler import get_video_info, extract_audio_from_video

class TestVideoHandler(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.video_path = os.path.join(self.temp_dir, "test.mp4")
        with open(self.video_path, "w") as f:
            f.write("dummy video data")

    def tearDown(self):
        shutil.rmtree(self.temp_dir)

    @unittest.skip("Skipping due to ffprobe dependency")
    def test_get_video_info(self):
        info = get_video_info(self.video_path)
        self.assertIsNotNone(info)

    @unittest.skip("Skipping due to ffmpeg dependency")
    def test_extract_audio_from_video(self):
        audio_path = extract_audio_from_video(self.video_path, self.temp_dir)
        self.assertTrue(os.path.exists(audio_path))

if __name__ == "__main__":
    unittest.main()
