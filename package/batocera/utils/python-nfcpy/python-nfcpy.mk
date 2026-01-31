################################################################################
#
# python-nfcpy
#
################################################################################

PYTHON_NFCPY_VERSION = 1.0.4
PYTHON_NFCPY_SITE = $(call github,nfcpy,nfcpy,v$(PYTHON_NFCPY_VERSION))
PYTHON_NFCPY_DEPENDENCIES = libusb libusb-compat
PYTHON_NFCPY_SETUP_TYPE = setuptools
PYTHON_NFCPY_LICENSE = EUPL-1.1+
PYTHON_NFCPY_LICENSE_FILES = LICENSE

$(eval $(python-package))
