# Functionality to retrieve the "infobox" image from a person's Wikipedia page.  

import db_wrapper
import sys
import wikipedia
import re
import os.path
import requests

from config import cfg 

img_suffix_pattern = re.compile('.+\.(\w+)$')
supported_img_suffixes = ('jpg', 'JPG', 'png', 'PNG', 'jpeg', 'JPEG')

def get_images():
    print(f"Getting images")

    q = "select title from people where image_fname is null"

    with db_wrapper.DBManager() as cur:
        cur_for_update = cur.connection.cursor()

        for row in cur.execute(q):
            title = row[0]
            print(f'Attempting to get image for {title}')
            sys.stdout.flush()
            get_image(title, cur_for_update)
            cur.connection.commit()
            sys.stdout.flush()

    print("Finished getting images")

def get_image(title, cur):
    image_fname = image_already_downloaded(title)
    if image_fname:
        print(f"Skipping fetch of img for title {title} because we already have it")
        update_img_in_db(title, image_fname, cur)
        return None

    html = get_html(title)

    infobox_start = html.find("infobox")
    if infobox_start == -1:
        print("Didn't find an infobox")
        update_img_in_db(title, "no infobox", cur)
        return None

    index_start = html.find(' src="//upload.wikimedia.org/wikipedia/',
                            infobox_start, infobox_start + 5000)
    if index_start == -1:
        print("Didn't find the start")
        update_img_in_db(title, "no image available", cur)        
        return None

    index_end = html.find('" ', index_start, index_start + 1000)

    if index_end == -1:
        print("Didn't find the end")
        update_img_in_db(title, "bad end: " + html[index_start:index_start+1000], cur)
        return None

    url = html[index_start:index_end]

    match = img_suffix_pattern.match(url)
    if not match:
        print(f'url does not match regex {url}')
        update_img_in_db(title, "bad url", cur)
        return None

    suffix = match.group(1)

    if suffix not in supported_img_suffixes:
        print(f'Unhandled suffix: {suffix}')
        update_img_in_db(title, f'bad suffix: {suffix}', cur)
        return None
    
    url = url.replace(' src="', 'https:', 1)
    print(f'url for {title} is {url}')

    get_image_from_url(title, cur, url)

def get_html(title):
    html=""

    try:
        page = wikipedia.page(title, pageid=None, auto_suggest=False,
                              redirect=False, preload=False)
        html = page.html()
    except wikipedia.exceptions.RedirectError:
        print(f'Skipping title ${title} because it will redirect')
    except wikipedia.exceptions.PageError:
        print(f'Skipping title ${title} because of PageError')
    except KeyError:
        print("Skipping due to KeyError")

    return html

def image_already_downloaded(title):
    cleaned_title = get_cleaned_title(title)
    for suffix in supported_img_suffixes:
        fname = f'{cfg.output_directory}/images/{cleaned_title}.{suffix}'
        if os.path.exists(fname):    
            return fname

    return None

def get_cleaned_title(title):
    cleaned_title = title.replace(' ', '_')
    cleaned_title = cleaned_title.replace('"', '')
    return cleaned_title

def update_img_in_db(title, img_str, cur):
    cur.execute("update people set image_fname = ? where title = ?", (img_str, title))

def get_image_from_url(title, cur, url):
    cleaned_title = get_cleaned_title(title)

    match = img_suffix_pattern.match(url)
    if not match:
        print(f'url does not match regex {url}')
        return None
    else:
        suffix = match.group(1)

    # Get a copy of the default headers that requests would use
    headers = requests.utils.default_headers()

    headers.update(
        {
            'User-Agent': f'WikiPeopleGetterTestBot/0.1 ({cfg.email})'
        }
    )

    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        print(response.request.headers)
        code = response.status_code
        if code != 403:
            text = response.text
        else:
            text = "Unauthorized"

        print(f'ERROR status = {code}, text = {text}')
        update_img_in_db(title, url, cur)
        return None

    print("SUCCESS")

    image_fname = f'{cfg.output_directory}/images/{cleaned_title}.{suffix}'
    os.makedirs(os.path.dirname(image_fname), exist_ok=True)

    with open(image_fname, 'wb') as f:
        f.write(response.content)

    update_img_in_db(title, image_fname, cur)
