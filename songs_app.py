import os
from songs import create_app

DB_URI = os.environ.get('SONGS_DB_URI',
                        default='mongodb://localhost/yousician-andres')

app = create_app(DB_URI)
