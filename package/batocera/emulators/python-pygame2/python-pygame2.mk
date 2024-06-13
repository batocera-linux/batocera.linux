################################################################################
#
# python-pygame2
#
################################################################################

PYTHON_PYGAME2_VERSION = 2.5.2
PYTHON_PYGAME2_SITE =  $(call github,pygame,pygame,$(PYTHON_PYGAME2_VERSION))
PYTHON_PYGAME2_SETUP_TYPE = setuptools
PYTHON_PYGAME2_LICENSE = LGPL-2.1+
PYTHON_PYGAME2_LICENSE_FILES = LGPL

PYTHON_PYGAME2_DEPENDENCIES = sdl2 sdl2_image sdl2_ttf sdl2_mixer libpng jpeg host-python-cython

define PYTHON_PYGAME2_FIXSDL2_PATH
	sed -i "s+sdl2-config+$(STAGING_DIR)/usr/bin/sdl2-config+g" $(@D)/buildconfig/config_unix.py
	sed -i 's+"/usr+"$(STAGING_DIR)/usr+g' $(@D)/buildconfig/config_unix.py
endef

PYTHON_PYGAME2_PRE_CONFIGURE_HOOKS += PYTHON_PYGAME2_FIXSDL2_PATH

define PYTHON_PYGAME2_REMOVE_DOC
	rm -rf $(TARGET_DIR)/usr/lib/python*/site-packages/pygame/docs
endef

PYTHON_PYGAME2_POST_INSTALL_TARGET_HOOKS += PYTHON_PYGAME2_REMOVE_DOC

define PYTHON_PYGAME2_REMOVE_TESTS
	rm -rf $(TARGET_DIR)/usr/lib/python*/site-packages/pygame/tests
endef

PYTHON_PYGAME2_POST_INSTALL_TARGET_HOOKS += PYTHON_PYGAME2_REMOVE_TESTS

ifneq ($(BR2_PACKAGE_PYTHON_PYGAME2_EXAMPLES),y)
define PYTHON_PYGAME2_REMOVE_EXAMPLES
	rm -rf $(TARGET_DIR)/usr/lib/python$(PYTHON_VERSION_MAJOR)/site-packages/pygame/examples
endef
PYTHON_PYGAME2_POST_INSTALL_TARGET_HOOKS += PYTHON_PYGAME2_REMOVE_EXAMPLES
endif

$(eval $(python-package))
