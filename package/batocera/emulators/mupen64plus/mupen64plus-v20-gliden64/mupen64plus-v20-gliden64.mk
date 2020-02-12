################################################################################
#
# mupen64plus video GLIDEN64
#
################################################################################
# Version.: Commits on Oct 19, 2015 (version.: 2.0)
MUPEN64PLUS_V20_GLIDEN64_VERSION = 34fa719a61fa2338025facc9810ad2ef1a00e7ee
MUPEN64PLUS_V20_GLIDEN64_SITE = $(call github,gonetz,GLideN64,$(MUPEN64PLUS_V20_GLIDEN64_VERSION))
MUPEN64PLUS_V20_GLIDEN64_LICENSE = GPLv2
MUPEN64PLUS_V20_GLIDEN64_DEPENDENCIES = sdl2 alsa-lib mupen64plus-core
MUPEN64PLUS_V20_GLIDEN64_CONF_OPTS = -DMUPENPLUSAPI=On
MUPEN64PLUS_V20_GLIDEN64_SUBDIR = /src/

ifeq ($(BR2_PACKAGE_RPI_USERLAND),y)
	MUPEN64PLUS_V20_GLIDEN64_DEPENDENCIES += rpi-userland
endif

ifeq ($(BR2_arm)$(BR2_aarch64),y)
	MUPEN64PLUS_V20_GLIDEN64_CONF_OPTS += -DGLES2=1
endif

ifeq ($(BR2_ENABLE_DEBUG),y)
	MUPEN64PLUS_V20_GLIDEN64_RELEASE = "debug"
else
	MUPEN64PLUS_V20_GLIDEN64_RELEASE = "release"
endif

define MUPEN64PLUS_V20_GLIDEN64_INSTALL_TARGET_CMDS
	mkdir -p $(TARGET_DIR)/usr/share/mupen64plus/
	$(INSTALL) -D $(@D)/src/plugin/$(MUPEN64PLUS_V20_GLIDEN64_RELEASE)/mupen64plus-video-GLideN64.so \
		$(TARGET_DIR)/usr/lib/mupen64plus/mupen64plus-video-gliden64.so
	$(INSTALL) -D $(@D)/ini/* \
		$(TARGET_DIR)/usr/share/mupen64plus/
endef

define MUPEN64PLUS_V20_GLIDEN64_PRE_CONFIGURE_FIXUP
	chmod +x $(@D)/src/getRevision.sh
	sh $(@D)/src/getRevision.sh
	$(SED) 's|/opt/vc/include|$(STAGING_DIR)/usr/include|g' $(@D)/src/CMakeLists.txt
	$(SED) 's|/opt/vc/lib|$(STAGING_DIR)/usr/lib|g' $(@D)/src/CMakeLists.txt
endef

MUPEN64PLUS_V20_GLIDEN64_PRE_CONFIGURE_HOOKS += MUPEN64PLUS_V20_GLIDEN64_PRE_CONFIGURE_FIXUP

$(eval $(cmake-package))
