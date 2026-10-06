################################################################################
#
# python-mkbootimg
#
################################################################################

PYTHON_MKBOOTIMG_VERSION = d2bb0af5ba6d3198a3e99529c97eda1be0b5a093
PYTHON_MKBOOTIMG_SITE = https://android.googlesource.com/platform/system/tools/mkbootimg
PYTHON_MKBOOTIMG_SITE_METHOD = git
PYTHON_MKBOOTIMG_LICENSE = Apache-2.0

PYTHON_MKBOOTIMG_DEPENDENCIES += python

define HOST_PYTHON_MKBOOTIMG_INSTALL_CMDS
	$(INSTALL) -D -m 0755 $(@D)/mkbootimg.py $(HOST_DIR)/usr/bin/mkbootimg.py
endef

$(eval $(host-generic-package))
