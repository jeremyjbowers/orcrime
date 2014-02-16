import csv
from glob import glob
import json
import os

from bs4 import BeautifulSoup
from fabric.api import *
import requests

def scrape_pdf():
    """
    Scrape the crime PDFs from the campus police.
    TODO: Ignore the file if we have a copy.
    """
    url = "http://police.uoregon.edu/content/campus-daily-crime-log"
    r = requests.get(url)

    if r.status_code == 200:

        soup = BeautifulSoup(r.content)
        links = soup.select('#attachments a')[1:]

        for link in links:
            link_url = link['href']
            file_name = link_url.split('http://police.uoregon.edu/sites/police.uoregon.edu/files/Clery Crime Log')[1].strip()

            r = requests.get(link_url)

            if r.status_code == 200:

                with open('data/%s' % file_name, 'wb') as writefile:
                    writefile.write(r.content)

def pdf_to_csv():
    """
    Convert the crime PDFs to CSV for parsing.
    This is really slow and will take a long time for each PDF, on the order of a minute or two.

    Requires pdftohtml to be installed in a directory that this user can access.
    http://sourceforge.net/projects/pdftohtml/files/latest/download?source=files

    This project installs pdftable in the requirements.
    """
    for path in glob('data/pdf/*.pdf'):

        name, extension = os.path.splitext(path.replace('data/pdf/', ''))
        os.system('pdftohtml -xml -stdout data/pdf/%s.pdf | pdftable -f data/csv/%s.csv' % (name, name))

        print '+ %s' % name

def clean_csv():
    """
    Many rows of the resulting CSV have junk data.
    Clean these by ignoring any row missing a value in the first column.
    Writes the result to a clean/ directory.
    """
    for path in glob('data/csv/*.csv'):

        rows = []

        with open(path, 'rb') as readfile:

            for row in csv.reader(readfile):
                if row[0] != '':
                    rows.append(row)

        name, extension = os.path.splitext(path.replace('data/csv/', ''))

        with open('data/csv/clean/%s%s' % (name, extension), 'wb') as writefile:
            csvfile = csv.writer(writefile)

            for row in rows:
                row_list = []

                for item in row:
                    # These CSVs were saved in Windows, and they're encoded Latin-1.
                    # Decode them and then re-encode them as UTF-8 for sanity.
                    row_list.append(item.decode('latin-1').encode('utf-8'))

                csvfile.writerow(row_list)

def parse_csv():
    """
    Finally, parse all of these CSVs into a big JSON file.
    """
    incidents = []

    for path in glob('data/csv/clean/*.csv'):
        name, extension = os.path.splitext(path.replace('data/csv/clean/', ''))

        with open(path, 'rb') as readfile:

            for incident in csv.DictReader(readfile):
                incident['originating_file'] = name
                incidents.append(incident)

    with open('data/incidents.json', 'wb') as writefile:
        writefile.write(json.dumps(incidents))

    print "%s incidents written to JSON" % len(incidents)

def parse_json():
    """
    Parses the JSON file of incidents.
    """
    with open('data/incidents.json', 'rb') as readfile:
        incident_list = list(json.loads(readfile.read()))

    for incident in incident_list[2000:2050]:
        print incident