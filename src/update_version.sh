#!/bin/bash

svn update
major=1
minor=0
version=`svn info . | egrep "Revision: [0-9]+" | cut -d " " -f2`
sed -i "s/version='.*'/version=\'${major}.${minor}.${version}\'/g" setup.py
sed -i "s/BUILD =.*/BUILD = \"${version}\"/g" selfie/configs/env_prod.py
sed -i "s/BUILD =.*/BUILD = \"${version}\"/g" selfie/configs/env_dev.py
sed -i "s/BUILD =.*/BUILD = \"${version}\"/g" selfie/configs/env_beta.py
