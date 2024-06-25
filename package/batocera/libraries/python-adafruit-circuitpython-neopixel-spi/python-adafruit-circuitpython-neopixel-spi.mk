################################################################################
#
# python-adafruit-circuitpython-neopixel-spi
#
################################################################################

PYTHON_ADAFRUIT_CIRCUITPYTHON_NEOPIXEL_SPI_VERSION = 1.0.9
PYTHON_ADAFRUIT_CIRCUITPYTHON_NEOPIXEL_SPI_SOURCE = adafruit-circuitpython-neopixel-spi-$(PYTHON_ADAFRUIT_CIRCUITPYTHON_NEOPIXEL_SPI_VERSION).tar.gz
PYTHON_ADAFRUIT_CIRCUITPYTHON_NEOPIXEL_SPI_SITE = https://files.pythonhosted.org/packages/4e/8a/8551808a687cd181737a52ea1629cd783e7a30c83ffa5129fd5d9ef96807
PYTHON_ADAFRUIT_CIRCUITPYTHON_NEOPIXEL_SPI_SETUP_TYPE = setuptools
PYTHON_ADAFRUIT_CIRCUITPYTHON_NEOPIXEL_SPI_LICENSE = MIT
PYTHON_ADAFRUIT_CIRCUITPYTHON_NEOPIXEL_SPI_LICENSE_FILES = LICENSE LICENSES/CC-BY-4.0.txt LICENSES/MIT.txt LICENSES/Unlicense.txt

PYTHON_ADAFRUIT_CIRCUITPYTHON_NEOPIXEL_SPI_DEPENDENCIES += python-adafruit-circuitpython-pixelbuf
PYTHON_ADAFRUIT_CIRCUITPYTHON_NEOPIXEL_SPI_DEPENDENCIES += python-adafruit-circuitpython-busdevice

$(eval $(python-package))
