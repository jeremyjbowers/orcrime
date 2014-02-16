# ORCRIME
A simple project that watches crimes reported to the University of Oregon campus police.

This project is released under an MIT licence. See ```LICENSE``` for details.

## Getting started
Prerequisites: [Make sure your computer is set up properly.](http://blog.apps.npr.org/2013/06/06/how-to-setup-a-developers-environment.html)

First, clone this project locally.
```
git clone git@github.com:jeremyjbowers/orcrime.git
cd orcrime
```

Next, make a virtual environment and install the requirements.
```
mkvirtualenv orcrime
pip install -r requirements.txt
```

Next, install pdftohtml. [Download the files here.](http://sourceforge.net/projects/pdftohtml/files/latest/download?source=files). Unzip this folder to your desktop and open your terminal. Current version is 0.40a; change the path in the commands below if this has changed.
```
cd ~/Desktop/pdftohtml-0.40a/
make
cp src/pdf2html /usr/local/bin/pdf2html
```

Finally, run the fabric ```bootstrap``` command. *Warning*: This will take some time.
```
fab bootstrap_data
```