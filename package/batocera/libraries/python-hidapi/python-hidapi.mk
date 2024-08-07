################################################################################
#
# python-hidapi
#
################################################################################

PYTHON_HIDAPI_VERSION = 0.14.0
PYTHON_HIDAPI_SOURCE = hidapi-$(PYTHON_HIDAPI_VERSION).tar.gz
PYTHON_HIDAPI_SETUP_TYPE = pep517
PYTHON_HIDAPI_SITE = https://files.pythonhosted.org/packages/95/0e/c106800c94219ec3e6b483210e91623117bfafcf1decaff3c422e18af349
PYTHON_HIDAPI_LICENSE = GPLv3
PYTHON_HIDAPI_LICENSE_FILES = LICENSE-gpl3.txt
PYTHON_HIDAPI_DEPENDENCIES = libusb udev hidapi host-python-cython

define PYTHON_HIDAPI_UPDATE_INCLUDE_PATH
	sed -i "s+/usr/include/+$(STAGING_DIR)/usr/include/+g" $(@D)/setup.py
endef
PYTHON_HIDAPI_PRE_CONFIGURE_HOOKS += PYTHON_HIDAPI_UPDATE_INCLUDE_PATH

$(eval $(python-package))