#!/usr/bin/env python

from .logger import get_logger
import subprocess

eslog = get_logger(__name__)

class batoceraServices:

    def isServiceEnabled(name):
        proc = subprocess.Popen(["batocera-services list"], stdout=subprocess.PIPE, shell=True)
        (out, err) = proc.communicate()
        for valmod in out.decode().splitlines():
            vals = valmod.split(";")
            if(name == vals[0] and vals[1] == "*"):
                eslog.debug(f"service {name} is enabled")
                return True
        eslog.debug(f"service {name} is disabled")
        return False
