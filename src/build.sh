#!/bin/bash

bash update_version.sh
rm -r deb_dist/*
python setup.py --command-packages=stdeb.command sdist_dsc --with-python2=False --with-python3=True --no-python2-scripts=True bdist_deb
