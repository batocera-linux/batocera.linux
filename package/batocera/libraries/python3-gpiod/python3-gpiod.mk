################################################################################
#
# python3-gpiod
#
################################################################################

PYTHON3_GPIOD_VERSION = 2.2.0
PYTHON3_GPIOD_SOURCE = gpiod-$(PYTHON3_GPIOD_VERSION).tar.gz
PYTHON3_GPIOD_SITE = https://files.pythonhosted.org/packages/aa/b7/12bda3ba884c7299ac461f84732583048d962145ad230447115758c32e6e
PYTHON3_GPIOD_SETUP_TYPE = setuptools
PYTHON3_GPIOD_LICENSE_FILES = LICENSE

$(eval $(python-package))
