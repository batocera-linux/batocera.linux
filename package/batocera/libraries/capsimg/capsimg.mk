################################################################################
#
# CAPSIMG
#
################################################################################
# Version.: Commits on May 3, 2019
CAPSIMG_VERSION = 5d306bb19bc4382367a1e489fb36768fd224b5e6
CAPSIMG_SITE = $(call github,FrodeSolheim,capsimg,$(CAPSIMG_VERSION))
CAPSIMG_LICENSE = Non-commercial

define CAPSIMG_HOOK_BOOTSTRAP
	cd $(@D) && ./bootstrap.fs
endef

CAPSIMG_PRE_CONFIGURE_HOOKS += CAPSIMG_HOOK_BOOTSTRAP

define CAPSIMG_CONFIGURE_CMDS
	cd $(@D) && ./configure.fs
endef

define CAPSIMG_BUILD_CMDS
	CFLAGS="$(TARGET_CFLAGS)" CXXFLAGS="$(TARGET_CXXFLAGS)" \
		$(MAKE) CXX="$(TARGET_CXX)" CC="$(TARGET_CC)" -C $(@D)/ -f Makefile.fs
endef

define CAPSIMG_INSTALL_TARGET_CMDS
	$(INSTALL) -D $(@D)/capsimg.so \
		$(TARGET_DIR)/usr/share/FS-UAE/Plugins/capsimg.so
        echo "$(CAPSIMG_VERSION)" > $(TARGET_DIR)/usr/share/FS-UAE/Plugins/Version.txt
endef

$(eval $(autotools-package))
