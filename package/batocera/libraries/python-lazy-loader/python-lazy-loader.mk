################################################################################
#
# python-lazy-loader
#
################################################################################

PYTHON_LAZY_LOADER_VERSION = 0.5
PYTHON_LAZY_LOADER_SOURCE = lazy_loader-$(PYTHON_LAZY_LOADER_VERSION).tar.gz
PYTHON_LAZY_LOADER_SITE = https://files.pythonhosted.org/packages/49/ac/21a1f8aa3777f5658576777ea76bfb124b702c520bbe90edf4ae9915eafa
PYTHON_LAZY_LOADER_SETUP_TYPE = setuptools
PYTHON_LAZY_LOADER_LICENSE = BSD-3-Clause
PYTHON_LAZY_LOADER_LICENSE_FILES = LICENSE.md
PYTHON_LAZY_LOADER_DEPENDENCIES = python-packaging

$(eval $(python-package))
