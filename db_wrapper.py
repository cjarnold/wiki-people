import sqlite3
from config import cfg 

class DBManager():
    def __init__(self):
        self.file=f'{cfg.output_directory}/people.db'

    def __enter__(self):
        self.conn = sqlite3.connect(self.file)
        return self.conn.cursor()

    def __exit__(self, type, value, traceback):
        self.conn.commit()
        self.conn.close()

# Creates the necessary sqlite tables if they don't already exist
def initialize_tables():
    with DBManager() as cur:
        cur.execute('''
            CREATE TABLE IF NOT EXISTS people (
                title TEXT PRIMARY KEY,
                name TEXT,
                birth_year INTEGER NOT NULL,
                reference_count INTEGER NOT NULL,
                summary TEXT,
                image_fname TEXT
            )
        ''')

        cur.execute('''
            CREATE TABLE IF NOT EXISTS people_to_profession (
                title TEXT,
                profession TEXT,
                UNIQUE(title, profession)
            )
        ''')

def get_people_count():
    with DBManager() as cur:
        res = cur.execute("select count(1) from people")
        count = res.fetchone()[0]
        return int(count)