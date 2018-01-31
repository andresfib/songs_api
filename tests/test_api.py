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
songs_list = []
with codecs.open('tests/fixtures/songs.json', 'rU', 'utf-8') as f:
    for line in f:
        songs_list.append(loads(line))


class SongTestAPI(unittest.TestCase):

    def setUp(self):
        self.songs_app = create_app(DB_URI)

        with self.songs_app.app_context():
            # We add songs to the test database
            self.total_songs = len(songs_list)
            # We keep one _id to be used in tests
            self.song = songs_list.pop()
            # We insert the rest of the data
            mongo.db.songs.insert_many(songs_list)
            # We insert the single song last
            result = mongo.db.songs.insert_one(self.song)
            self.song_id = result.inserted_id

        self.app = self.songs_app.test_client()

    def tearDown(self):
        with self.songs_app.app_context():
            mongo.db.songs.drop()
            songs_list.append(self.song)

    def test_get_songs(self):
        response = self.app.get('/songs')
        data = get_data(response)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(data), 11)

    def test_get_third_page_of_songs(self):
        response = self.app.get('/songs?page=3')
        data = get_data(response)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(data), 1)

    def test_get_next_page_of_songs(self):
        query = '/songs?last_id=' + str(self.song_id)
        response = self.app.get(query)
        data = get_data(response)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(data), SONGS_PER_PAGE)

    def test_get_avg_difficulty(self):
        response = self.app.get('/songs/avg/difficulty')
        data = get_data(response)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(data['avg'], round(10.3236363636, 2))

    def test_get_avg_difficulty_with_level(self):
        response = self.app.get('/songs/avg/difficulty?level=13')
        data = get_data(response)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(data['avg'], round(14.096, 2))

    def test_get_avg_difficulty_with_non_existent_level(self):
        response = self.app.get('/songs/avg/difficulty?level=12343')
        self.assertEqual(response.status_code, 400)

    def test_get_avg_difficulty_with_wrong_level(self):
        response = self.app.get('/songs/avg/difficulty?level=asdf')
        self.assertEqual(response.status_code, 400)

    def test_search_songs_no_message(self):
        response = self.app.get('/songs/search')
        self.assertEqual(response.status_code, 400)

    def test_search_songs_yousician_message(self):
        response = self.app.get('/songs/search?message=yousician')
        data = get_data(response)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(data), 10)

    def test_search_songs_yousician_power_message(self):
        message = urllib.parse.quote('yousician power')
        response = self.app.get('/songs/search?message=' + message)
        data = get_data(response)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(data), 1)

    def test_give_song_rating(self):
        rating = '3'
        song_id = str(self.song_id)
        query = '/songs/rating?rating=' + rating + '&song_id=' + song_id
        response = self.app.post(query)
        data = get_data(response)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(data['ratings']), 1)

    def test_give_non_existent_song_rating(self):
        rating = '3'
        song_id = 'F' * 24
        query = '/songs/rating?rating=' + rating + '&song_id=' + song_id
        response = self.app.post(query)
        self.assertEqual(response.status_code, 400)

    def test_give_song_wrong_rating(self):
        rating = '6'
        song_id = str(self.song_id)
        query = '/songs/rating?rating=' + rating + '&song_id=' + song_id
        response = self.app.post(query)
        self.assertEqual(response.status_code, 400)

    def test_get_ratings_song(self):
        song_id = str(self.song_id)
        with self.songs_app.app_context():
            mongo.db.songs.update_one({'_id': ObjectId(self.song_id)},
                                      {'$set': {'ratings': [1, 2, 3, 4]}})
        query = '/songs/avg/rating?song_id=' + song_id
        response = self.app.get(query)
        data = get_data(response)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(data), 3)
        self.assertEqual(data['avg'], 2.5)
        self.assertEqual(data['max'], 4)
        self.assertEqual(data['min'], 1)

    def test_get_ratings_song_with_no_rating(self):
        song_id = str(self.song_id)
        query = '/songs/avg/rating?song_id=' + song_id
        response = self.app.get(query)
        self.assertEqual(response.status_code, 400)

    def test_get_ratings_non_existent_song(self):
        song_id = 'F' * 24
        query = '/songs/avg/rating?song_id=' + song_id
        response = self.app.get(query)
        self.assertEqual(response.status_code, 400)


def get_data(response):
    return loads(response.get_data(as_text=True))


if __name__ == '__main__':
    unittest.main()
