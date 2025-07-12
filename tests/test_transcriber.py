import unittest
import os
import tempfile
import shutil
from transcriber import transcribe_video

class TestTranscriber(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.audio_path = os.path.join(self.temp_dir, "test.wav")
        with open(self.audio_path, "w") as f:
            f.write("dummy audio data")

    def tearDown(self):
        shutil.rmtree(self.temp_dir)

    @unittest.skip("Skipping due to OpenAI API key dependency")
    def test_transcribe_video(self):
        srt_path = transcribe_video(self.audio_path, self.temp_dir)
        self.assertTrue(os.path.exists(srt_path))

if __name__ == "__main__":
    unittest.main()
