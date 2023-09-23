import wikipedia
import wiki_by_birth_year
import db_wrapper
import professions
import sys
import os

from config import cfg 

def get_summary(title):
    summary=""

    print(f'Getting summary for {title}')

    try:
        page = wikipedia.page(title, pageid=None, auto_suggest=False,
                              redirect=False, preload=False)
        summary = page.summary
    except wikipedia.exceptions.RedirectError:
        print(f'Skipping title ${title} because it will redirect')
    except wikipedia.exceptions.PageError:
        print(f'Skipping title ${title} because of PageError')
    except KeyError:
        print("Skipping due to KeyError")

    return summary

def insert_summaries_for_file(fname):
    if not os.path.exists(fname):
        print(f'ERROR: file {fname} was not found')
        return False

    db_wrapper.initialize_tables()

    good = 0
    skip_low_ref = 0
    skip_already_have = 0

    for title, ref_count, year in wiki_by_birth_year.iterate_people_file(fname):
        if ref_count >= cfg.min_ref_count_for_summary:
            with db_wrapper.DBManager() as cur:
                res = cur.execute("select title from people where title = ?", (title,) )

                if res.fetchone():
                    print(f'Summary for {title} already exists in the DB; skipping')
                    sys.stdout.flush()
                    skip_already_have += 1
                else:
                    summary = get_summary(title)
                    cur.execute("insert or ignore into people values (?, ?, ?, ?, ?)",
                                (title, year, ref_count, summary, None))
                    good += 1
        else:
            skip_low_ref += 1

    print(f'Inserted {good} good entries, skipped {skip_low_ref} low reference entries, '
          f'{skip_already_have} entries we already have')
    print(f'Database now contains {db_wrapper.get_people_count()} people')

    return True

# For all people born in 'year', with reference count above a threshold, does a wiki
# lookup on the page to get the summary and inserts the information
# into the 'people' table
def insert_summaries_for_year(year):
    fname = wiki_by_birth_year.year_to_filename(year)
    return insert_summaries_for_file(fname)

def print_details(title):
    with db_wrapper.DBManager() as cur:
        query = '''
            select birth_year, reference_count, summary, image_fname from people
            where title = ?
            '''
        res = cur.execute(query, (title,))
        row = res.fetchone()
        if row is None:
            print(f'{title} is not in the database')
        else:
            print(f'{title}:')
            print(f'  Born: {row[0]}')
            print(f'  Reference count: {row[1]}')
            print(f'  Image: {row[3]}')

            print(f'  Professions: ', end = '')
            prof_gen = (p for p in professions.get_professions(title))
            print(', '.join(prof_gen))

            print(f'\n{row[2]}')

