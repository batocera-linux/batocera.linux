################################################################################
#
# python-hidapi
#
################################################################################

PYTHON_HIDAPI_VERSION = 0.12.0.post2
PYTHON_HIDAPI_SOURCE = hidapi-$(PYTHON_HIDAPI_VERSION).tar.gz
PYTHON_HIDAPI_SETUP_TYPE = setuptools
PYTHON_HIDAPI_SITE = https://pypi.python.org/packages/source/h/hidapi
PYTHON_HIDAPI_LICENSE = GPLv3
PYTHON_HIDAPI_LICENSE_FILES = LICENSE-gpl3.txt
PYTHON_HIDAPI_DEPENDENCIES = libusb udev

define PYTHON_HIDAPI_UPDATE_INCLUDE_PATH
	sed -i "s+/usr/include/+$(STAGING_DIR)/usr/include/+g" $(@D)/setup.py
endef
PYTHON_HIDAPI_PRE_CONFIGURE_HOOKS += PYTHON_HIDAPI_UPDATE_INCLUDE_PATH

$(eval $(python-package))