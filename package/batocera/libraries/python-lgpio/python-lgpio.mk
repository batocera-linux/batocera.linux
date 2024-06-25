################################################################################
#
# python-lgpio
#
################################################################################

PYTHON_LGPIO_VERSION = 0.2.2.0
PYTHON_LGPIO_SOURCE = lgpio-$(PYTHON_LGPIO_VERSION).tar.gz
PYTHON_LGPIO_SITE = https://files.pythonhosted.org/packages/56/33/26ec2e8049eaa2f077bf23a12dc61ca559fbfa7bea0516bf263d657ae275
PYTHON_LGPIO_SETUP_TYPE = setuptools
PYTHON_LGPIO_LICENSE = Unencumbered
PYTHON_LGPIO_LICENSE_FILES = LICENSE

PYTHON_LGPIO_DEPENDENCIES = liblgpio

$(eval $(python-package))
