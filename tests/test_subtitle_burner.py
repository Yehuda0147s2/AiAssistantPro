import unittest
import os
import tempfile
import shutil
from subtitle_burner import burn_subtitles_to_video

class TestSubtitleBurner(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.video_path = os.path.join(self.temp_dir, "test.mp4")
        self.srt_path = os.path.join(self.temp_dir, "test.srt")
        with open(self.video_path, "w") as f:
            f.write("dummy video data")
        with open(self.srt_path, "w") as f:
            f.write("1\n00:00:01,000 --> 00:00:02,000\nHello")

    def tearDown(self):
        shutil.rmtree(self.temp_dir)

    @unittest.skipIf(not shutil.which("ffmpeg"), "ffmpeg not installed")
    def test_burn_subtitles_to_video(self):
        output_path = burn_subtitles_to_video(self.video_path, self.srt_path, self.temp_dir)
        self.assertTrue(os.path.exists(output_path))

if __name__ == "__main__":
    unittest.main()
