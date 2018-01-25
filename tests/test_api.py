import json
import unittest

from songs import app

class SongTestAPI(unittest.TestCase):

    def setUp(self):
        self.app = app.test_client()

    def test_get_songs(self):
        response = json.loads(self.app.get('/songs').get_data())
        self.assertEqual(len(response), 11)

    def test_get_avg_difficulty(self):
        response = json.loads(self.app.get('/songs/avg/difficulty').get_data())
        self.assertEqual(response['avg_difficulty'], round(10.3236363636, 2))

    def test_get_avg_difficulty_with_level(self):
        response = json.loads(self.app.get('/songs/avg/difficulty/13').get_data())
        self.assertEqual(response['avg_difficulty'], round(14.096, 2))

    def test_get_avg_difficulty_with_wrong_level(self):
        response_status = self.app.get('/songs/avg/difficulty/12343').status_code

        self.assertEqual(response_status, 404)


if __name__ == '__main__':
    unittest.main()
