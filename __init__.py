import os
from songs.songs import create_app

DB_NAME = os.environ.get('SONGS_DB', default='yousician-andres')
app = create_app(DB_NAME)
