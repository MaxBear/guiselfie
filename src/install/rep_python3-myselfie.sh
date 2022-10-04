#!/bin/bash

reprepro -Vb /home/nocadmin/debian remove buster python3-selfie-portal
reprepro -Vb /home/nocadmin/debian remove stretch python3-selfie-portal
reprepro -Vb /home/nocadmin/debian includedeb buster /home/nancy/selfie/branches/1.0_build/1.0/deb_dist/python3-selfie-portal_1.0.*_all.deb
reprepro -Vb /home/nocadmin/debian includedeb stretch /home/nancy/selfie/branches/1.0_build/1.0/deb_dist/python3-selfie-portal_1.0.*_all.deb
