################################################################################
#
# CAPSIMG
#
################################################################################
# Version.: Commits on Dec 02, 2019
CAPSIMG_VERSION = 264973530f131f1de586dcf4346871ac633824a3
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
		$(TARGET_DIR)/usr/share/fs-uae/Plugins/capsimg.so
        echo "$(CAPSIMG_VERSION)" > $(TARGET_DIR)/usr/share/fs-uae/Plugins/Version.txt
endef

$(eval $(autotools-package))
