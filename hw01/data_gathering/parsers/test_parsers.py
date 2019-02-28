import unittest

import os

from parsers.html_parser import HtmlParser


class TestHtmlParser(unittest.TestCase):

    def setUp(self):
        cur_dir = os.path.dirname(os.path.abspath(__file__))
        test_file = os.path.join(cur_dir, 'data', 'test.html')
        with open(test_file, 'rb') as f:
            self.data = f.read().decode('utf-8')

    def test_parse(self):
        test_data = {'Name': 'Peyj', 'Place': 1280, 'Total games': 1006, 'Win %': 52.8, 'Bruiser games': 81,
                     'Bruiser win %': 58.0, 'Ambusher games': 14, 'Ambusher win %': 57.1, 'Sustained Damage games': 562,
                     'Sustained Damage win %': 56.9, 'Siege games': 31, 'Siege win %': 51.6, 'Healer games': 111,
                     'Healer win %': 46.8, 'Tank games': 169, 'Tank win %': 43.8, 'Burst Damage games': 28,
                     'Burst Damage win %': 39.3, 'Support games': 8, 'Support win %': 37.5, 'Utility games': 2,
                     'Utility win %': 0.0}
        parser = HtmlParser()
        self.assertDictEqual(parser.parse(self.data), test_data)


if __name__ == '__main__':
    unittest.main()
