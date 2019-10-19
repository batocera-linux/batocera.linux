#!/usr/bin/env python

import sys
import os

scriptDir = "/usr/bin"
sys.argv[0]="mimic_python"
str1 = '\n'.join(str(i) for i in sys.argv)
os.system('"%s"/batocera-settings "%s"' % (scriptDir, str1))
