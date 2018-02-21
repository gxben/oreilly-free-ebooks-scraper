#!/usr/bin/env python3

import os
import shutil
import requests
from bs4 import BeautifulSoup
from bs4 import SoupStrainer

SITE_BASE = "http://www.oreilly.com/"
SITE_REPORTS = SITE_BASE + "free/reports.html"
EXTENSIONS = ["pdf", "mobi", "epub"]
OUTPUT_DIR = "output"

only_a_tags = SoupStrainer("a")
r = requests.get(SITE_REPORTS)
soup = BeautifulSoup(r.text, "html.parser", parse_only=only_a_tags)
sections = soup.find_all("a", class_="btn see-more")
for s in sections:
    href = s.get('href')
    x = href[len(SITE_BASE):].split('/')[0]
    #print(x, href)
    sr = requests.get(href)
    ssoup = BeautifulSoup(sr.text, "html.parser", parse_only=only_a_tags)
    ssections = ssoup.find_all("a", attrs={"data-toggle": "popover"})
    for ss in ssections:
        title = ss.get('title')
        uri = ss.get('href')
        #print("  ", title, uri)
        if not "http:" in uri and not "https:" in uri:
            uri = "http:" + uri
        if '?' in uri:
                tokens = uri.split('?')
                # remove trailing ?intcmp= from URI
                if "intcmp=" in tokens[1]:
                    uri = tokens[0]
                if "topic=" in tokens[1]:
                    uri = tokens[0]
                    topic = tokens[1][len("topic="):]
                    if topic not in uri:
                        uri = uri[:len(SITE_BASE)] + topic + "/" + uri[len(SITE_BASE):]
        #print("  -> ", uri)
        uri_array = uri.rsplit('/', 1)
        baseuri = uri_array[0] + "/files/"
        for e in EXTENSIONS:
            book_uri = baseuri + uri_array[1].rsplit('.', 1)[0] + "." + e
            r2 = requests.options(book_uri)
            if r2.status_code != 200:
                continue

            book_path = "{}/{}/{}".format(OUTPUT_DIR, x, title)
            if not os.path.exists(book_path):
                os.makedirs(book_path)
            book_file = "{}/{}.{}".format(book_path, title, e)

            #print("    * ", r2.status_code, book_uri)

            if not os.path.exists(book_file):
                print("Downloading {}.{} from {}".format(title, e, book_uri))
                file = requests.get(book_uri, stream=True)
                with open(book_file, 'wb') as out_file:
                    shutil.copyfileobj(file.raw, out_file)
                del file

print("Up To Date !")
