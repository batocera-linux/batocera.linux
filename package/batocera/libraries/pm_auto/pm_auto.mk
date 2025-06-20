################################################################################
#
# pm_auto
#
################################################################################

PM_AUTO_VERSION = 1.2.11
PM_AUTO_SITE = $(call github,sunfounder,pm_auto,$(PM_AUTO_VERSION))
PM_AUTO_SETUP_TYPE = setuptools
PM_AUTO_LICENSE = GPL-2.0
PM_AUTO_LICENSE_FILES = LICENSE

PM_AUTO_DEPENDENCIES += python-adafruit-circuitpython-neopixel-spi
PM_AUTO_DEPENDENCIES += python-smbus2 python-psutil python-lgpio
PM_AUTO_DEPENDENCIES += python-pillow python3-gpiod python-gpiozero
PM_AUTO_DEPENDENCIES += python-adafruit-circuitpython-requests

$(eval $(python-package))
