#!/usr/bin/env python3

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
import re
from config import cfg 

sys.stdin.reconfigure(encoding='utf-8')
sys.stdout.reconfigure(encoding='utf-8')

def do_year_range(year_start, year_end):
    for year in range(year_start, year_end + 1):
        print(f'\n====== Working on year {year} ======')
        wiki_by_birth_year.write_birth_year_file(year)
        wiki_summary.insert_summaries_for_year(year)

    print('')
    professions.apply_keyword_to_professions()

def do_backfill(fname):
    print("Backfill")
    wiki_summary.insert_summaries_for_file(fname)

def validate_summary_arg(value):
    value = value.lstrip()
    result = re.match('^(-?\d+):(-?\d+)$', value)

    if result:
        v1 = int(result[1])
        v2 = int(result[2])

        min = -1200
        max = 2050
        if v1 > v2 or v1 < -1200 or v2 > 2050:
            print(f'summary year range must be within {min} to {max}')
            raise ValueError
        else:
            return (v1, v2)
    else:
        print(f"summary argument must be of format 'YEAR-START:YEAR-END'")
        raise ValueError

# argparse cannot the "-" sign to signify negative numeric values,
# so we need this preprocessing:
for i, arg in enumerate(sys.argv):
    if (arg[0] == '-') and arg[1].isdigit():
        sys.argv[i] = ' ' + arg

parser = argparse.ArgumentParser()
group = parser.add_mutually_exclusive_group(required=True)

group.add_argument("-s", "--summary",
                    required=False,
                    type=validate_summary_arg,
                    metavar="YEAR-START:YEAR-END",
                    help="Fetch a summary from Wikipedia and store it in the DB for all people whose birth year is within the provided range and reference count meets the threshold defined in config.yaml")

group.add_argument("-b", "--backfill",
                    required=False,
                    metavar="FILENAME",
                    help="Insert each person into the database if they meet the reference count criteria")

group.add_argument("-i", "--images",
                    required=False,
                    action="store_true",
                    help="Fetch images for all people in the DB whose image is not already downloaded")

group.add_argument("-a", "--assign-professions",
                    required=False,
                    action="store_true",
                    help="Refresh the people_to_professions table based on keyword_to_professions.csv")

group.add_argument("-f", "--filter-professions",
                    required=False,
                    action="store_true",
                    help="Remove people from the DB whose reference count does not meet the threshold defined in the per-profession reference count thresholds in config.yaml")

group.add_argument("-p", "--profession-counts",
                    required=False,
                    action="store_true",
                    help="List how many people each profession applies to")

group.add_argument("-m", "--profession-members",
                    metavar="PROFESSION",
                    required=False,
                    help="List the members of PROFESSION, sorted by reference count")

group.add_argument("-d", "--details",
                    metavar="PERSON",
                    required=False,
                    help="Print the details available for PERSON")
              
args = parser.parse_args()

os.makedirs(cfg.output_directory, exist_ok=True)

if args.summary:
    do_year_range(*args.summary)
elif args.assign_professions:
    professions.apply_keyword_to_professions()
elif args.filter_professions:
    professions.do_filter()
elif args.images:
    image_retriever.get_images()
elif args.profession_counts:
    professions.print_profession_summary()
elif args.details:
    wiki_summary.print_details(args.details)
elif args.profession_members:
    professions.print_profession_members(args.profession_members)
elif args.backfill:
    do_backfill(args.backfill)

