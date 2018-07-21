#!/usr/bin/env python

from sys import stderr
import traceback

def log(str):
    stderr.write(str + "\n")

def logtrace():
    traceback.print_exc(file=stderr)
