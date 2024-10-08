import logging
import subprocess

eslog = logging.getLogger(__name__)

class batoceraServices:

    @staticmethod
    def isServiceEnabled(name: str):
        proc = subprocess.Popen(["batocera-services list"], stdout=subprocess.PIPE, shell=True)
        (out, err) = proc.communicate()
        for valmod in out.decode().splitlines():
            vals = valmod.split(";")
            if(name == vals[0] and vals[1] == "*"):
                eslog.debug(f"service {name} is enabled")
                return True
        eslog.debug(f"service {name} is disabled")
        return False

    @staticmethod
    def getServiceStatus(name: str):
        proc = subprocess.Popen(["batocera-services status \"" + name + "\""], stdout=subprocess.PIPE, shell=True)
        (out, err) = proc.communicate()
        val = out.decode().strip()
        eslog.debug(f"service {name} status : \"" + val + "\"") # strip any end of lines
        return val
