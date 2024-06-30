################################################################################
#
# python-adafruit-circuitpython-pixelbuf
#
################################################################################

PYTHON_ADAFRUIT_CIRCUITPYTHON_PIXELBUF_VERSION = 2.0.4
PYTHON_ADAFRUIT_CIRCUITPYTHON_PIXELBUF_SOURCE = adafruit-circuitpython-pixelbuf-$(PYTHON_ADAFRUIT_CIRCUITPYTHON_PIXELBUF_VERSION).tar.gz
PYTHON_ADAFRUIT_CIRCUITPYTHON_PIXELBUF_SITE = https://files.pythonhosted.org/packages/f4/70/4145f3b6ea67e0735acbcee58f1f49979249b3e44136e563896ad83d1254
PYTHON_ADAFRUIT_CIRCUITPYTHON_PIXELBUF_SETUP_TYPE = setuptools
PYTHON_ADAFRUIT_CIRCUITPYTHON_PIXELBUF_LICENSE = MIT
PYTHON_ADAFRUIT_CIRCUITPYTHON_PIXELBUF_LICENSE_FILES = LICENSE LICENSES/CC-BY-4.0.txt LICENSES/MIT.txt LICENSES/Unlicense.txt

$(eval $(python-package))
