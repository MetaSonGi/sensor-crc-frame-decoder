import importlib.util, json, threading, unittest, urllib.request, urllib.error
from pathlib import Path
ROOT=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location("app",ROOT/"main.py")
frames=importlib.util.module_from_spec(spec)
spec.loader.exec_module(frames)

class FrameTests(unittest.TestCase):
    def test_known_crc_vector(self): self.assertEqual(frames.crc16(b'123456789'),0x29B1)
    def test_all_split_points(self):
        raw=frames.encode(1,3,38.25,1.234)
        for split in range(len(raw)+1):
            d=frames.Decoder(); result=d.feed(raw[:split])+d.feed(raw[split:])
            self.assertEqual(len(result),1); self.assertEqual(result[0]['temperature_c'],38.25)
    def test_corruption_resync_duplicate(self):
        good=frames.encode(1,3,38.25,1.234); bad=bytearray(good); bad[7]^=1
        d=frames.Decoder(); result=d.feed(b'noise'+bad+good+good)
        self.assertEqual(d.crc_errors,1); self.assertEqual([r['accepted'] for r in result],[True,False])
    def test_noise_buffer_is_bounded(self):
        d=frames.Decoder(); self.assertEqual(d.feed(b'x'*10000),[]); self.assertLessEqual(len(d.buffer),1)

if __name__=="__main__": unittest.main()
