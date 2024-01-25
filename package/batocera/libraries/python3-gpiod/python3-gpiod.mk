################################################################################
#
# python3-gpiod
#
################################################################################

PYTHON3_GPIOD_VERSION = v1.5.4
PYTHON3_GPIOD_SOURCE = $(PYTHON3_GPIOD_VERSION).tar.gz
PYTHON3_GPIOD_SITE = https://github.com/hhk7734/python3-gpiod/archive/refs/tags
PYTHON3_GPIOD_SETUP_TYPE = setuptools
PYTHON3_GPIOD_LICENSE_FILES = LICENSE

$(eval $(python-package))
