import logging
import subprocess

_logger = logging.getLogger(__name__)

class batoceraServices:

    @staticmethod
    def isServiceEnabled(name: str):
        proc = subprocess.Popen(["batocera-services list"], stdout=subprocess.PIPE, shell=True)
        (out, err) = proc.communicate()
        for valmod in out.decode().splitlines():
            vals = valmod.split(";")
            if(name == vals[0] and vals[1] == "*"):
                _logger.debug("service %s is enabled", name)
                return True
        _logger.debug("service %s is disabled", name)
        return False

    @staticmethod
    def getServiceStatus(name: str):
        proc = subprocess.Popen([f'batocera-services status "{name}"'], stdout=subprocess.PIPE, shell=True)
        (out, err) = proc.communicate()
        val = out.decode().strip()
        _logger.debug('service %s status : "%s"', name, val) # strip any end of lines
        return val
