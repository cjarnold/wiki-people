import sys
import sqlite3
import db_wrapper
import csv
import yaml
import os.path

csv_name='keyword_to_professions.csv'

def apply_keyword_to_professions():
    print("Starting update of people_to_profession table...")
    sys.stdout.flush() 
    
    with db_wrapper.DBManager() as cur, open(csv_name, newline='') as csvfile:
        cur.execute('DELETE FROM people_to_profession')

        reader = csv.DictReader(csvfile)
        for row in reader:
            apply_keyword(cur, row['keyword'], row['profession'])

    print("people_to_profession table updated")

def apply_keyword(cur, keyword, profession):
    insert_cursor = cur.connection.cursor()

    # todo: binding the query parameter was not working for this first query.  Look into it.
    for row in cur.execute("select title from people where substr(summary, 0, 300) like '% " + keyword + "%'"):
        title = row[0]
        insert_cursor.execute("insert or ignore into people_to_profession values (?, ?)", (title, profession))

    insert_cursor.close()

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
