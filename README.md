# OR CRIME
A simple project that watches crimes reported to the University of Oregon campus police.

This code is open source under the MIT license. See ```LICENSE``` for complete details.

## Getting this running

### Setup your computer
Follow [these instructions](http://blog.apps.npr.org/2013/06/06/how-to-setup-a-developers-environment.html) for getting your computer set up to work with a Python project.

### Get the code
Check out this project from GitHub and cd to its directory.
```
git clone git@github.com:jeremyjbowers/orcrime.git
cd orcrime
```
### Prepare an environment
Make a virtual environment for this project and install the requirements.
```
mkvirtualenv orcrime
pip install -r requirements.txt
```

### Install pdf2html
[Download the files here.](http://sourceforge.net/projects/pdftohtml/files/latest/download?source=files). Unzip this folder to your desktop and open your terminal.

Current version is 0.40a; change the path in the commands below if this has changed.
```
cd ~/Desktop/pdftohtml-0.40a/
make
cp src/pdf2html /usr/local/bin/pdf2html
```

### Get the data
*Warning*: This will take some time.
```
fab bootstrap_data
```

## What's coming
* A web application with charts and such.
* An ORM, probably [peewee](http://peewee.readthedocs.org/en/latest/index.html).

## What's this all about?
[Email Jeremy](mailto:jeremyjbowers@gmail.com) if you're confused.
