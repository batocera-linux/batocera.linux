################################################################################
#
# python-adafruit-circuitpython-connectionmanager
#
################################################################################

PYTHON_ADAFRUIT_CIRCUITPYTHON_CONNECTIONMANAGER_VERSION = 3.1.1
PYTHON_ADAFRUIT_CIRCUITPYTHON_CONNECTIONMANAGER_SOURCE = adafruit_circuitpython_connectionmanager-$(PYTHON_ADAFRUIT_CIRCUITPYTHON_CONNECTIONMANAGER_VERSION).tar.gz
PYTHON_ADAFRUIT_CIRCUITPYTHON_CONNECTIONMANAGER_SITE = https://files.pythonhosted.org/packages/21/8c/a7d5e38ae4b41c6a7c3aa9b3c9c8f742faed570acdcb48b634e2e1dde573
PYTHON_ADAFRUIT_CIRCUITPYTHON_CONNECTIONMANAGER_SETUP_TYPE = setuptools
PYTHON_ADAFRUIT_CIRCUITPYTHON_CONNECTIONMANAGER_LICENSE = MIT
PYTHON_ADAFRUIT_CIRCUITPYTHON_CONNECTIONMANAGER_LICENSE_FILES = LICENSE LICENSES/CC-BY-4.0.txt LICENSES/MIT.txt LICENSES/Unlicense.txt

$(eval $(python-package))

