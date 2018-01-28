import os
from songs.songs import create_app

DB_URI = os.environ.get('SONGS_DB_URI',
                         default='mongodb://localhost/yousician-andres')
print(DB_URI)
app = create_app(DB_URI)
