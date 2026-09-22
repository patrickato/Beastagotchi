import unittest
from beastcore.util import parse_iw_dev, channel_to_band

IW = '''phy#0
\tInterface wlan0mon
\t\tifindex 17
\t\taddr 00:00:00:00:00:00
\t\ttype monitor
\t\tchannel 10 (2457 MHz), width: 20 MHz, center1: 2457 MHz
\tInterface wlan0
\t\taddr aa:bb:cc:dd:ee:ff
\t\ttype managed
\t\tchannel 10 (2457 MHz), width: 20 MHz, center1: 2457 MHz
'''
class ParserTests(unittest.TestCase):
    def test_iw(self):
        x = parse_iw_dev(IW)
        self.assertEqual(x[0]['name'],'wlan0mon'); self.assertEqual(x[0]['channel'],10); self.assertEqual(x[0]['frequency_mhz'],2457)
    def test_band(self):
        self.assertEqual(channel_to_band(10,2457),'2.4GHz'); self.assertEqual(channel_to_band(153,5765),'5GHz')
if __name__ == '__main__': unittest.main()
