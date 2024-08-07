################################################################################
#
# python-adafruit-circuitpython-typing
#
################################################################################

PYTHON_ADAFRUIT_CIRCUITPYTHON_TYPING_VERSION = 1.10.3
PYTHON_ADAFRUIT_CIRCUITPYTHON_TYPING_SOURCE = adafruit-circuitpython-typing-$(PYTHON_ADAFRUIT_CIRCUITPYTHON_TYPING_VERSION).tar.gz
PYTHON_ADAFRUIT_CIRCUITPYTHON_TYPING_SITE = https://files.pythonhosted.org/packages/35/0b/3bdb065264f061e5ab8bbf8b0746b349ff3adbf219dc69c39f7d8e2427c3
PYTHON_ADAFRUIT_CIRCUITPYTHON_TYPING_SETUP_TYPE = setuptools
PYTHON_ADAFRUIT_CIRCUITPYTHON_TYPING_LICENSE = MIT
PYTHON_ADAFRUIT_CIRCUITPYTHON_TYPING_LICENSE_FILES = LICENSE LICENSES/CC-BY-4.0.txt LICENSES/MIT.txt LICENSES/Unlicense.txt

$(eval $(python-package))
