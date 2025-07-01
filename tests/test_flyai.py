import os
import json
import unittest

from app import flyai

class FlyAITest(unittest.TestCase):
    def setUp(self):
        self.temp_file = os.path.join(os.path.dirname(__file__), 'test_data.json')
        flyai.DATA_FILE = self.temp_file
        if os.path.exists(self.temp_file):
            os.remove(self.temp_file)

    def tearDown(self):
        if os.path.exists(self.temp_file):
            os.remove(self.temp_file)

    def test_save_and_load(self):
        data = {'user': {'phone': '123', 'language': 'hi'}, 'bookings': []}
        flyai.save_data(data)
        loaded = flyai.load_data()
        self.assertEqual(data, loaded)

    def test_create_booking(self):
        data = {'user': {'phone': '123', 'language': 'hi'}, 'bookings': []}
        flyai.DATA_FILE = self.temp_file
        flyai.save_data(data)
        # simulate booking creation without user input using monkeypatch of input
        inputs = iter(['धान', '1', 'दिल्ली', '2024-01-01 10:00'])
        def mock_input(prompt=''):
            return next(inputs)
        original_input = __builtins__["input"]
        __builtins__["input"] = mock_input
        try:
            flyai.create_booking(data)
        finally:
            __builtins__["input"] = original_input
        self.assertEqual(len(data['bookings']), 1)
        b = data['bookings'][0]
        self.assertEqual(b['crop'], 'धान')
        self.assertEqual(b['field_size'], '1')
        self.assertEqual(b['region'], 'दिल्ली')
        self.assertEqual(b['datetime'], '2024-01-01 10:00')
        self.assertEqual(b['status'], 'Scheduled')

if __name__ == '__main__':
    unittest.main()
