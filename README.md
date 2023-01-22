wiki-people
============

wiki-people is a Python tool which creates a local sqlite database of humans who are referenced on Wikipedia.

The database is populated with the name, birth year, summary text, and small image of each person whose Wikipedia page exceeds a reference threshold.  

Keywords from the summary text are used to assign one or more professions to each person in a separate database table.  Custom reference thresholds can be configured per profession.

Installation and Setup
============

First, install python 3 and [pipenv](https://pipenv.pypa.io/en/latest/).

Then in the wiki-people directory:
```
pipenv install
```

This will install two third party wikipedia modules: https://pypi.org/project/Wikipedia-API/ and https://pypi.org/project/wikipedia/.


Apart from the wikipedia modules referenced above, wiki-people makes direct requests to wikipedia image resources.  These requests must have a User-Agent header which abides by [wikimedia's user-agent policy](https://meta.wikimedia.org/wiki/User-Agent_policy), including an email address. wiki-people forms this header but it needs an email address.  This address needs to be configured in config.yaml.  This config defaults to
```
email: you@example.com
```
Please modify it before running the tool.

Basic Usage
===========

```
pipenv run ./main.py --summary 1960:1965
```

The summary argument takes a year range (inclusive on both ends).
This will fetch from Wikipedia a summary for each person born within the provided year range and store the data in a sqlite database with filename `results/people.db`.  The number of references in the Wikipedia page must equal or exceed the `min_ref_count_for_summary` threshold defined in config.yaml in order to be inserted into the database.

Wikipedia has over 1.7 million pages of humans throughout history going back to 1152 BC.  The vast majority of these pages are for obscure people with very few references.  Therefore the `min_ref_count_for_summary` configuration is very important to sift out these likely uninteresting people.  The default `min_ref_count_for_summary = 60` will bring the people count to below 50,000.  Further profession based filtering will likely be necessary to get your dataset to be more interesting and manageable.  See below for more details.


Assigning and filtering by professions
===========
wiki-people applies a basic keyword search of each person's summary to match against a list of professions.  See keyword_to_professions.csv to customize this keyword search.  If any changes are made, refresh the people_to_professions table by doing 
```
pipenv run ./main.py --assign-professions
```

Once professions are assigned, you can see the number of people assigned to each profession by using:
```
pipenv run ./main.py --profession-counts
```

View the list of people in a profession (sorted by reference count) using:
```
pipenv run ./main.py --profession-members <profession>
```

You can put in place more stringent reference count requirements on a per-profession basis using the `min_ref_counts_per_profession` dictionary in config.yaml.  For example, the default config has:
```
min_ref_counts_per_profession:
  'basketball player': 100
  'economist': 150
```
This means basketball players need at least 100 references in order to stay in the database.  economists need at least 150 references.  This default configuration is for example purposes only.  Modify this dictionary as necessary based on your preferences.

There is another similar dictionary in config.yaml called `min_ref_counts_per_sole_profession`.  The default config looks like:
```
min_ref_counts_per_sole_profession:
  'architect': 80
```
These values also represent per-profession reference thresholds, but will only apply if the listed profession is the sole profession assigned to a person.  So for example, if a person is tagged as both an engineer and an architect and has a reference count below 80, they will not be filtered out by the above rule.

Retrieving images
===========
Once your dataset is trimmed down using the above filtering techniques, you can have wiki-people attempt to retrieve a small image of each person in the database by doing:
```
pipenv run ./main.py --images
```
Images will be stored in `results/images/` and then the `image_fname` column in the people table will be updated with this location.  If no image is availabe or there is an error, the `image_fname` column will be updated with the appropriate error text.

Viewing details
===========
View the birth year, summary, reference count, and image location of a person by using:
```
pipenv run ./main.py --details <title of the person's wikipedia page>
```
In most cases, the title of the person's Wikipedia page is their name.  But in some cases the title is made unique with extra text to disambiguate.

FAQ
===========
### If I run --summary again for a year that I've already run it for, what happens?

It is safe to re-run --summary.

For each year, wiki-people first generates a raw list of people and reference counts to `results/birth_year_files/<year>_births`.  If that file is already present, wiki-people will not re-generate it.

If a person is already present in the database, wiki-people will not request the summary again and will continue on to the next person in the list.

### Why is the tool so slow?  Can it be sped up?
The tool currently does not parallelize requests.  Adding the parallelization is very do-able but as I developed this I did not want Wikipedia to block my IP address due to abuse of their HTTP services.  So, the requests are serial.  More investigation will be necessary to see if Wikipedia allows higher request rates and concurrency.

### Am I allowed to use all of this data for my app?

See https://en.wikipedia.org/wiki/Wikipedia:Copyrights for details.

