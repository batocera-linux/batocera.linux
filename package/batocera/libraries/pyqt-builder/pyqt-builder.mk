################################################################################
#
# pyqt-builder
#
################################################################################

PYQT_BUILDER_VERSION = 1.18.1
PYQT_BUILDER_SITE = https://files.pythonhosted.org/packages/0b/0a/e7684c054c3b85999354bb3be7ccbd6e6d9b751940cec8ecff5e7a8ea9f7
PYQT_BUILDER_SOURCE = pyqt_builder-$(PYQT_BUILDER_VERSION).tar.gz
PYQT_BUILDER_LICENSE = BSD-2-Clause
PYQT_BUILDER_LICENSE_FILES = LICENSE
PYQT_BUILDER_SETUP_TYPE = setuptools

PYQT_BUILDER_DEPENDENCIES += host-python-setuptools-scm
HOST_PYQT_BUILDER_DEPENDENCIES += host-python-setuptools-scm

$(eval $(python-package))
$(eval $(host-python-package))
