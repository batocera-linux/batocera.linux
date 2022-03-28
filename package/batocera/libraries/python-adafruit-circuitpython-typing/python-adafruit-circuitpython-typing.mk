################################################################################
#
# python-adafruit-circuitpython-typing
#
################################################################################

PYTHON_ADAFRUIT_CIRCUITPYTHON_TYPING_VERSION = 1.0.0
PYTHON_ADAFRUIT_CIRCUITPYTHON_TYPING_SOURCE = adafruit-circuitpython-typing-$(PYTHON_ADAFRUIT_CIRCUITPYTHON_TYPING_VERSION).tar.gz
PYTHON_ADAFRUIT_CIRCUITPYTHON_TYPING_SITE = https://files.pythonhosted.org/packages/88/15/fd21032233fae87de43e538e131d884200a3e15fa41ea0d5e1f03ef9a867
PYTHON_ADAFRUIT_CIRCUITPYTHON_TYPING_SETUP_TYPE = setuptools
PYTHON_ADAFRUIT_CIRCUITPYTHON_TYPING_LICENSE = MIT
PYTHON_ADAFRUIT_CIRCUITPYTHON_TYPING_LICENSE_FILES = LICENSE LICENSES/CC-BY-4.0.txt LICENSES/MIT.txt LICENSES/Unlicense.txt

$(eval $(python-package))
