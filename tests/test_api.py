import unittest
from bson.json_util import loads
import codecs

from songs import create_app
from songs.models import mongo

# Load data once
data = []
with codecs.open('tests/fixtures/songs.json','rU','utf-8') as f:
    for line in f:
       data.append(loads(line))

class SongTestAPI(unittest.TestCase):

    def setUp(self):
        db_name = 'yousician-andres-test'
        self.songs_app = create_app(db_name)

        with self.songs_app.app_context():
            mongo.db.songs.insert_many(data)

        self.app = self.songs_app.test_client()

    def tearDown(self):
        with self.songs_app.app_context():
            mongo.db.songs.drop()

    def test_get_songs(self):
        response = loads(self.app.get('/songs').get_data())
        self.assertEqual(len(response), 11)

    def test_get_avg_difficulty(self):
        response = loads(self.app.get('/songs/avg/difficulty').get_data())
        self.assertEqual(response['avg_difficulty'], round(10.3236363636, 2))

    def test_get_avg_difficulty_with_level(self):
        response = loads(self.app.get('/songs/avg/difficulty?level=13').get_data())
        self.assertEqual(response['avg_difficulty'], round(14.096, 2))

    def test_get_avg_difficulty_with_non_existent_level(self):
        response_status = self.app.get('/songs/avg/difficulty?level=12343').status_code
        self.assertEqual(response_status, 400)

    def test_get_avg_difficulty_with_wrong_level(self):
        response_status = self.app.get('/songs/avg/difficulty?level=asdf').status_code

        self.assertEqual(response_status, 400)

    def test_search_songs_no_message(self):
        response = loads(self.app.get('/songs/search').get_data())
        self.assertEqual(len(response), 0)

    def test_search_songs_yousician_message(self):
        response = loads(self.app.get('/songs/search?message=yousician').get_data())
        self.assertEqual(len(response), 10)

if __name__ == '__main__':
    unittest.main()
