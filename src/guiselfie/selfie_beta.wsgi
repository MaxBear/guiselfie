#!/usr/bin/env python

import sys, os
import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path

SELFIE_HOME = str(Path(Path(__file__).parent.absolute()))
sys.path.insert(0, SELFIE_HOME)
os.environ['APPLICATION_SETTINGS']="%s/configs/env_beta.py" % SELFIE_HOME

from selfie import app as selfie
application=selfie
