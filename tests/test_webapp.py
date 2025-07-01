import os
import threading
import unittest
import urllib.request

from app import flyai
from app import webapp
from http.server import HTTPServer


class WebAppTest(unittest.TestCase):
    def setUp(self):
        self.temp_file = os.path.join(os.path.dirname(__file__), 'web_test_data.json')
        flyai.DATA_FILE = self.temp_file
        if os.path.exists(self.temp_file):
            os.remove(self.temp_file)
        flyai.save_data({'user': None, 'bookings': []})

        self.server = HTTPServer(('localhost', 0), webapp.FlyAIHandler)
        self.server.data = flyai.load_data()
        self.server.pending = {}
        self.port = self.server.server_address[1]
        self.thread = threading.Thread(target=self.server.serve_forever)
        self.thread.daemon = True
        self.thread.start()

    def tearDown(self):
        self.server.shutdown()
        self.server.server_close()
        self.thread.join()
        if os.path.exists(self.temp_file):
            os.remove(self.temp_file)

    def test_register_page(self):
        url = f'http://localhost:{self.port}/register'
        with urllib.request.urlopen(url) as resp:
            html = resp.read().decode('utf-8')
        self.assertIn('उपयोगकर्ता पंजीकरण', html)


if __name__ == '__main__':
    unittest.main()
