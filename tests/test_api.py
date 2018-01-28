import codecs
import urllib
import unittest
import os
from bson.json_util import loads
from bson.objectid import ObjectId

from songs import create_app
from songs.models import mongo, SONGS_PER_PAGE

DB_URI = os.environ.get('SONGS_DB_URI',
                        default='mongodb://localhost/yousician-andres-test')

# Load data from file once
data = []
with codecs.open('tests/fixtures/songs.json', 'rU', 'utf-8') as f:
    for line in f:
        data.append(loads(line))


class SongTestAPI(unittest.TestCase):

    def setUp(self):
        self.songs_app = create_app(DB_URI)

        with self.songs_app.app_context():
            # We add songs to the test database
            self.total_songs = len(data)
            # We keep one _id to be used in tests
            self.song = data.pop()
            # We insert the rest of the data
            mongo.db.songs.insert_many(data)
            # We insert the single song last
            result = mongo.db.songs.insert_one(self.song)
            self.song_id = result.inserted_id


        self.app = self.songs_app.test_client()

    def tearDown(self):
        with self.songs_app.app_context():
            mongo.db.songs.drop()
            data.append(self.song)

    def test_get_songs(self):
        response = loads(self.app.get('/songs').get_data())
        self.assertEqual(len(response), 11)

    def test_get_third_page_of_songs(self):
        response = loads(self.app.get('/songs?page=3').get_data())
        self.assertEqual(len(response), 1)

    def test_get_next_page_of_songs(self):
        query = '/songs?last_id=' + str(self.song_id)
        response = loads(self.app.get(query).get_data())
        self.assertEqual(len(response), SONGS_PER_PAGE)

    def test_get_avg_difficulty(self):
        response = loads(self.app.get('/songs/avg/difficulty').get_data())
        self.assertEqual(response['avg'], round(10.3236363636, 2))

    def test_get_avg_difficulty_with_level(self):
        response = loads(self.app.get('/songs/avg/difficulty?level=13').get_data())
        self.assertEqual(response['avg'], round(14.096, 2))

    def test_get_avg_difficulty_with_non_existent_level(self):
        response_status = self.app.get('/songs/avg/difficulty?level=12343').status_code
        self.assertEqual(response_status, 400)

    def test_get_avg_difficulty_with_wrong_level(self):
        response_status = self.app.get('/songs/avg/difficulty?level=asdf').status_code

        self.assertEqual(response_status, 400)

    def test_search_songs_no_message(self):
        response_status = self.app.get('/songs/search').status_code
        self.assertEqual(response_status, 400)

    def test_search_songs_yousician_message(self):
        response = loads(self.app.get('/songs/search?message=yousician').get_data())
        self.assertEqual(len(response), 10)

    def test_search_songs_yousician_power_message(self):
        message = urllib.parse.quote('yousician power')
        response = loads(self.app.get('/songs/search?message=' + message)
                         .get_data())
        self.assertEqual(len(response), 1)

    def test_give_song_rating(self):
        rating = '3'
        song_id = str(self.song_id)
        query = '/songs/rating?rating=' + rating + '&song_id=' + song_id
        response = loads(self.app.post(query).get_data())
        self.assertEqual(len(response['ratings']), 1)

    def test_give_song_wrong_rating(self):
        rating = '6'
        song_id = str(self.song_id)
        query = '/songs/rating?rating=' + rating + '&song_id=' + song_id
        response_status = self.app.post(query).status_code
        self.assertEqual(response_status, 400)

    def test_get_ratings_song(self):
        song_id = str(self.song_id)
        with self.songs_app.app_context():
            mongo.db.songs.update_one({'_id': ObjectId(self.song_id)},
                                      {'$set': {'ratings': [1, 2, 3, 4]}})
        query = '/songs/avg/rating?song_id=' + song_id
        response = loads(self.app.get(query).get_data())
        self.assertEqual(len(response), 3)
        self.assertEqual(response['avg'], 2.5)
        self.assertEqual(response['max'], 4)
        self.assertEqual(response['min'], 1)


if __name__ == '__main__':
    unittest.main()
