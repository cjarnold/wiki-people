# This module's primary functionality is the 'write_birth_year_file'
# method.  Given a year, it writes to a file the name and reference count
# of all humans born in that year who have a page on wikipedia.
#
# Once a birth year file is obtained it can later be iterated through using
# 'iterate_birth_year_file'

import sys
import os
import re

# Two 3rd party wikipedia modules are used, based on unique functionality.

# This module is capable of retrieving all members in a wikipedia
# category.  This is useful because for each year in history,
# wikipedia defines a category for humans born in that year.
import wikipediaapi

# This module is capable of retrieving the list of references
# for a wiki page.  Reference count on a page is a simple first
# metric to filter out likely unimportant historical figures.
import wikipedia

from config import cfg 

wikipediaapi.log.setLevel(level=wikipediaapi.logging.DEBUG)
out_hdlr = wikipediaapi.logging.StreamHandler(sys.stderr)
out_hdlr.setFormatter(wikipediaapi.logging.Formatter('%(asctime)s %(message)s'))
out_hdlr.setLevel(wikipediaapi.logging.DEBUG)
wikipediaapi.log.addHandler(out_hdlr)

wiki_wiki = wikipediaapi.Wikipedia('en')

def write_birth_year_file(year):
    page_name = year_to_category_name(year)
    fname = year_to_filename(year)

    if os.path.exists(fname):
        print(f'Birth year file {fname} already exists; not regenerating it')
        return

    os.makedirs(os.path.dirname(fname), exist_ok=True)

    with open(fname, 'w', encoding='utf-8') as myfile:
        print(f"Getting category '{page_name}' and writing results to {fname}")

        cat = wiki_wiki.page(page_name)

        counter = 0
        for c in cat.categorymembers.values():
            write_member(c.title, year, counter, myfile)
            counter = counter + 1

    print("Done")

def write_member(title, birth_year, counter, myfile):
    try:
        utf8_title = title.encode("utf-8")
        print(f'About to work on member {counter} {title}')
        sys.stdout.flush()
        ref_count = get_reference_count(title)

        myfile.write(f'{ref_count} {birth_year} |{title}\n')
        myfile.flush()
    except UnicodeEncodeError:
        print("UnicodeEncodeError")
    except KeyError:
        print("Skipping due to KeyError")

def get_reference_count(title):
    ref_count = 0
    try:
        page = wikipedia.page(title, pageid=None, auto_suggest=False,
                              redirect=False, preload=False)
        ref_count = len(page.references)
    except wikipedia.exceptions.RedirectError:
        print(f'Skipping title ${title} because it will redirect')
    except wikipedia.exceptions.PageError:
        print(f'Skipping title ${title} because of PageError')

    return ref_count

def year_to_category_name(year):
    # Wikipedia has categories for all the people born in each year of history.
    #
    # Example: https://en.wikipedia.org/wiki/Category:1982_births
    #
    # For BC it is like:
    # https://en.wikipedia.org/wiki/Category:9_BC_births
    # The earliest Wikipedia has is 1152 BC.
    # 0 is special: https://en.wikipedia.org/wiki/Category:0s_BC_births
    #
    # From AD 1-11, the format is unique: https://en.wikipedia.org/wiki/Category:AD_<year>_births
    #
    # There are many people that have an unknown birth year.  Wikipedia puts these
    # into 3 special categories.  I've mapped these to special placeholder years
    # 3000, 3001, and 3002:
    #   3000: Category:Year_of_birth_missing_(living_people)
    #   3001: Category:Year_of_birth_missing
    #   3002: Category:Year_of_birth_unknown

    if year == 3000:
        return 'Category:Year_of_birth_missing_(living_people)'
    elif year == 3001:
        return 'Category:Year_of_birth_missing'
    elif year == 3002:
        return 'Category:Year_of_birth_unknown'
    elif year < 11 and year > 0:
        return f'Category:AD_{year}_births'
    elif year >= 11:
        return f'Category:{year}_births'
    elif year < 0:
        year = -1*year
        return f'Category:{year}_BC_births'
    else:
        # year == 0
        return 'Category:0s_births'

def year_to_filename(year):
    prefix = ""

    if year < 0:
        year = -1*year
        prefix = "bc_"

    return f'{cfg.output_directory}/birth_year_files/{prefix}{year}_births'

# Generator which yields tuples of (page title, ref_count)
# for all items previously downloaded in the 'year' file.
def iterate_birth_year_file(year):
    fname = year_to_filename(year)
    pattern = re.compile('(\d+) -?(\d+) \|(.+)')

    with open(fname, 'r', encoding='utf-8') as myfile:
        for line in myfile:
            line.rstrip()
            match = pattern.match(line)
            if match:
                ref_count = int(match.group(1))
                title = match.group(3)
                yield (title, ref_count)
            else:
                print(f'ERROR: Line {line} is not in the correct format')

def have_birth_year_file(year):
    fname = year_to_filename(year)
    return os.path.exists(fname)
