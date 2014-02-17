import collections
import csv
import glob
import json
import os

import bs4
from fabric.api import *
import requests

def scrape_pdf():
    """
    Scrape crime PDFs from the UO police Web site.
    """
    print "Scrape: Crime index page"
    url = "http://police.uoregon.edu/content/campus-daily-crime-log"
    r = requests.get(url)

    if r.status_code == 200:
        soup = bs4.BeautifulSoup(r.content)
        links = soup.select('#attachments a')[1:]

        print "Scrape: Evaluating %s links" % len(links)
        for link in links:
            link_url = link['href']
            file_name = link_url.split('http://police.uoregon.edu/sites/police.uoregon.edu/files/Clery Crime Log')[1].strip()

            if not os.path.exists('data/pdf/%s' % file_name):
                r = requests.get(link_url)
                print 'Downloading %s' % file_name

                if r.status_code == 200:
                    with open('data/pdf/%s' % file_name, 'wb') as writefile:
                        writefile.write(r.content)

                else:
                    print "Failed downloading %s" % file_name

    else:
        print "Scrape: Crime index page error"

def pdf_to_csv():
    """
    Convert crime PDFs to CSV for parsing.
    This is really slow and will take a long time for each PDF, on the order of a minute or two.

    Requires pdftohtml to be installed in a directory that this user can access.
    http://sourceforge.net/projects/pdftohtml/files/latest/download?source=files

    This project installs pdftable in the requirements.
    """
    print "Convert: Evaluating %s files" % len(glob.glob('data/pdf/*.pdf'))
    for path in glob.glob('data/pdf/*.pdf'):
        name, extension = os.path.splitext(path.replace('data/pdf/', ''))

        if not os.path.exists('data/csv/%s.csv' % name):
            print 'Converting %s' % name
            os.system('pdftohtml -xml -stdout data/pdf/%s.pdf | pdftable -f data/csv/%s.csv' % (name, name))

def clean_csv():
    """
    Remove junk rows from generated CSVs.
    Many rows of the resulting CSV have junk data.
    Ignore any row missing a value in the first column.
    Write the result to a clean/ directory.
    """
    print "Clean: Evaluating %s files" % len(glob.glob('data/csv/*.csv'))
    for path in glob.glob('data/csv/*.csv'):
        name, extension = os.path.splitext(path.replace('data/csv/', ''))

        if not os.path.exists('data/csv/clean/%s%s' % (name, extension)):
            print "Cleaning %s" % name

            rows = []

            with open(path, 'rb') as readfile:
                for row in csv.reader(readfile):
                    if row[0] != '':
                        rows.append(row)

            with open('data/csv/clean/%s%s' % (name, extension), 'wb') as writefile:
                csvfile = csv.writer(writefile)

                for row in rows:
                    row_list = []

                    # These CSVs were saved in Windows, and they're encoded Latin-1.
                    # Decode them and then re-encode them as UTF-8 for sanity.
                    [row_list.append(item.decode('latin-1').encode('utf-8')) for item in row]

                    csvfile.writerow(row_list)

def parse_clean_csv():
    """
    Parse CSV rows to dictionaries and add to a JSON file.
    TODO: Each PDF is 60 days worth of crime reports, which repeat. Many do not have an ID.
    Find out what makes them unique? Perhaps date + description but only within a filename?
    """
    incidents = []

    print "Parse: Parsing %s cleaned CSV files" % len(glob.glob('data/csv/clean/*.csv'))

    for path in glob.glob('data/csv/clean/*.csv'):
        name, extension = os.path.splitext(path.replace('data/csv/clean/', ''))

        with open(path, 'rb') as readfile:

            for incident in csv.DictReader(readfile):

                # List which file we found this incident in, for troubleshooting and recordkeeping.
                incident['originating_file'] = name
                incidents.append(incident)

    with open('data/incidents.json', 'wb') as writefile:
        writefile.write(json.dumps(incidents))

    print "Parse: Writing %s incidents to JSON" % len(incidents)

def parse_json():
    """
    Opens the JSON file and sends it out to subfunctions for parsing.
    """
    with open('data/incidents.json', 'rb') as readfile:
        incident_list = list(json.loads(readfile.read()))

    generate_counts_by_date(incident_list)
    generate_counts_by_type(incident_list)

def generate_counts_by_date(incident_list):
    """
    Generates counts of reported incident by date.
    """
    incident_types = collections.defaultdict(int)

    for incident in incident_list:
        incident_types[incident['Date Reported'].strip().lower()] += 1

    incident_list = []

    for k,v in incident_types.items():
        incident_type_dict = {}
        incident_type_dict['date'] = k
        incident_type_dict['count'] = v
        incident_list.append(incident_type_dict)

    incident_list = sorted(incident_list, key=lambda x: x['count'], reverse=True)

    with open('data/count-incidents-by-date.json', 'wb') as writefile:
        writefile.write(json.dumps(incident_list))

    for incident in incident_list:
        if incident['date'] not in ["", "date reported"]:
            print "%s: %s" % (incident['date'], incident['count'])

def generate_counts_by_type(incident_list):
    """
    Generates counts of reported incidents by type.
    """
    incident_types = collections.defaultdict(int)

    for incident in incident_list:
        if u"," in incident['Nature (Classification)']:
            for i in incident['Nature (Classification)'].split(','):
                incident_types[i.strip().lower()] += 1
        else:
            incident_types[incident['Nature (Classification)'].strip().lower()] += 1

    incident_list = []

    for k,v in incident_types.items():
        incident_type_dict = {}
        incident_type_dict['type'] = k
        incident_type_dict['count'] = v
        incident_list.append(incident_type_dict)

    incident_list = sorted(incident_list, key=lambda x: x['count'], reverse=True)

    with open('data/count-incidents-by-type.json', 'wb') as writefile:
        writefile.write(json.dumps(incident_list))

    for incident in incident_list:
        if incident['type'] not in [""]:
            print "%s: %s" % (incident['type'], incident['count'])

def bootstrap_data():
    """
    Bootstrap this project by downloading PDFs, convert them to CSV, and parse the CSVs to JSON.
    """
    scrape_pdf()
    pdf_to_csv()
    clean_csv()
    parse_clean_csv()