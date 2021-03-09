################################################################################
#
# python3-pyparsing
#
################################################################################

PYTHON3_PYPARSING_VERSION = 2.4.2
PYTHON3_PYPARSING_SOURCE = pyparsing-$(PYTHON3_PYPARSING_VERSION).tar.gz
PYTHON3_PYPARSING_SITE = https://files.pythonhosted.org/packages/7e/24/eaa8d7003aee23eda270099eeec754d7bf4399f75c6a011ef948304f66a2
PYTHON3_PYPARSING_LICENSE = MIT
PYTHON3_PYPARSING_LICENSE_FILES = LICENSE
PYTHON3_PYPARSING_SETUP_TYPE = setuptools

HOST_PYTHON3_PYPARSING_NEEDS_HOST_PYTHON = python3

#batocera
PYTHON_PYPARSING_INSTALL_STAGING = YES

$(eval $(python-package))
#batocera
$(eval $(host-python-package))
