
import wikipediaapi
import wikipedia
import sys
import argparse
import db_wrapper
import wiki_by_birth_year
import wiki_summary
import professions
import image_retriever
import os
from config import cfg 

sys.stdin.reconfigure(encoding='utf-8')
sys.stdout.reconfigure(encoding='utf-8')

def do_year_range(year_start, year_end):
    for year in range(year_start, year_end + 1):
        print(f'\n====== Working on year {year} ======')
        wiki_by_birth_year.write_birth_year_file(year)
        wiki_summary.insert_summaries(year)

    print('\n')

    professions.apply_keyword_to_professions()
    professions.filter_professions(cfg.min_ref_counts_per_profession)
    professions.filter_professions(cfg.min_ref_counts_per_sole_profession, must_be_sole_profession=True)

    # This table needs to be rebuilt to remove the now deleted people
    professions.apply_keyword_to_professions()

    print('\n')

    image_retriever.get_images()

possible_actions = ['db_summary', 'update_professions']

parser = argparse.ArgumentParser()

parser.add_argument("-a", "--action",
                    required=False,
                    choices = possible_actions,
                    help="An action")

parser.add_argument("-r", "--retrieve",
                    required=False,
                    type=int,
                    help="Retrieve the name and reference counts"
                    "of all humans born in this year")

parser.add_argument("-i", "--insert",
                    required=False,
                    type=int,
                    help="Do summary lookups of the humans born in this year")

parser.add_argument("-s", "--year-start",
                    required=True,
                    type=int,
                    help="Starting year")

parser.add_argument("-e", "--year-end",
                    required=True,
                    type=int,
                    help="Ending year")
                   
args = parser.parse_args()

os.makedirs(cfg.output_directory, exist_ok=True)

if args.action == "db_summary":
    db_wrapper.print_summary()
elif args.action == "update_professions":
    professions.apply_keyword_to_professions()
elif args.action == "iterate_summaries":
    pass
    #iterate_summaries()
elif args.retrieve:
    wiki_by_birth_year.write_birth_year_file(args.retrieve)
elif args.insert:
    wiki_summary.insert_summaries(args.insert)
else:
    do_year_range(args.year_start, args.year_end)
