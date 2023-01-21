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
pipenv run ./main.py --year-start 10 --year-end 12 
```

Configuration
===========



# Notes
Please see https://en.wikipedia.org/wiki/Wikipedia:Copyrights for licensing information.

