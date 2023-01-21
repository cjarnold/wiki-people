import sys
import sqlite3
import db_wrapper
import csv
import yaml
import os.path
from config import cfg

csv_name='keyword_to_professions.csv'

def apply_keyword_to_professions():
    print("Starting update of people_to_profession table...")
    sys.stdout.flush() 
    
    with db_wrapper.DBManager() as cur, open(csv_name, newline='') as csvfile:
        # start fresh
        cur.execute('DELETE FROM people_to_profession')

        reader = csv.DictReader(csvfile)
        for row in reader:
            apply_keyword(cur, row['keyword'], row['profession'])

    print("people_to_profession table updated")

def apply_keyword(cur, keyword, profession):
    insert_cursor = cur.connection.cursor()

    # todo: binding the query parameter was not working for this first query.  Look into it.
    # todo: the substr length should be configurable
    for row in cur.execute("select title from people where substr(summary, 0, 300) like '% " + keyword + "%'"):
        title = row[0]
        insert_cursor.execute("insert or ignore into people_to_profession values (?, ?)", (title, profession))

    insert_cursor.close()

def do_filter():
    start_count = db_wrapper.get_people_count()
    filter_professions(cfg.min_ref_counts_per_profession)
    filter_professions(cfg.min_ref_counts_per_sole_profession, must_be_sole_profession=True)
    # This table needs to be rebuilt to remove the now deleted people
    apply_keyword_to_professions()
    end_count = db_wrapper.get_people_count()
    print(f'Removed {start_count - end_count} people')

def filter_professions(profession_to_threshold, must_be_sole_profession=False):
    print(f'Filtering professions: must_be_sole_profession: {must_be_sole_profession}')
    for profession, ref_count_threshold in profession_to_threshold.items():
        if must_be_sole_profession:
            filter_by_sole_profession(profession, ref_count_threshold)
        else:
            filter_by_profession(profession, ref_count_threshold)

def filter_by_sole_profession(profession, ref_count_threshold):
    with db_wrapper.DBManager() as cur:
        cur.execute('''
            delete from people where title in
            (
                select DISTINCT(a.title) 
                from people as a,
                people_to_profession as b
                
                where a.title = b.title and b.profession = ? 
                and a.title in (select title from (select title, count(1) as num_professions from people_to_profession group by 1) where num_professions = 1)
                and a.reference_count < ?
            )
            ''',
            (profession, ref_count_threshold)
        )

def filter_by_profession(profession, ref_count_threshold):
    with db_wrapper.DBManager() as cur:
        cur.execute('''
            delete from people where title in
            (
                select DISTINCT(a.title) from people as a, people_to_profession as b
                where a.title = b.title and b.profession = ?
                and a.reference_count < ?
            )
            ''',
            (profession, ref_count_threshold)
        )

def print_profession_summary():
    with db_wrapper.DBManager() as cur:
        query = '''
            select profession, count(1) from people_to_profession
            group by 1
            order by 2 DESC
            '''
        for row in cur.execute(query):
            print(f'{row[0]}: {row[1]}')

def print_profession_members(profession):
    with db_wrapper.DBManager() as cur:
        query = '''
            select a.title, a.reference_count, a.birth_year
            from people as a, people_to_profession as b
            where a.title = b.title and b.profession = ?
            order by a.reference_count desc
            '''
        for row in cur.execute(query, (profession,)):
            print(f'{row[0]:<40} Refs:{row[1]:<10} Year:{row[2]}')

def get_professions(title):
    with db_wrapper.DBManager() as cur:
        query = '''
            select profession from people_to_profession
            where title = ?
            order by profession
            '''
        for row in cur.execute(query, (title,)):
            yield row[0]