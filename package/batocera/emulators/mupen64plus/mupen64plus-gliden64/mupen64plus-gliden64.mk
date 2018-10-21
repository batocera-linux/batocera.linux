################################################################################
#
# mupen64plus video GLIDEN64
#
################################################################################

MUPEN64PLUS_GLIDEN64_VERSION = 34fa719a61fa2338025facc9810ad2ef1a00e7ee # ok
#MUPEN64PLUS_GLIDEN64_VERSION = 21f46db8693ae07dce93f03db129dbf4f7136823 ok bug buggy after 1 or 2 1080 course
#MUPEN64PLUS_GLIDEN64_VERSION = 926e6c9225dd55efb317139029d84999cc9e11d3 ok bug buggy after 1 or 2 1080 course
MUPEN64PLUS_GLIDEN64_SITE = $(call github,gonetz,GLideN64,$(MUPEN64PLUS_GLIDEN64_VERSION))
MUPEN64PLUS_GLIDEN64_LICENSE = MIT
MUPEN64PLUS_GLIDEN64_DEPENDENCIES = sdl2 alsa-lib mupen64plus-core
MUPEN64PLUS_GLIDEN64_CONF_OPTS = -DMUPENPLUSAPI=On
MUPEN64PLUS_GLIDEN64_SUBDIR = /src/

ifeq ($(BR2_PACKAGE_RPI_USERLAND),y)
	MUPEN64PLUS_GLIDEN64_DEPENDENCIES += rpi-userland
endif

ifeq ($(BR2_PACKAGE_BATOCERA_TARGET_S905)$(BR2_PACKAGE_BATOCERA_TARGET_S912)$(BR2_PACKAGE_BATOCERA_TARGET_C2)$(BR2_PACKAGE_BATOCERA_TARGET_XU4)$(BR2_PACKAGE_BATOCERA_TARGET_LEGACYXU4),y)
       MUPEN64PLUS_GLIDEN64_CONF_OPTS += -DGLES2=1
endif

define MUPEN64PLUS_GLIDEN64_INSTALL_TARGET_CMDS
	mkdir -p $(TARGET_DIR)/recalbox/configs/mupen64/
	mkdir -p $(TARGET_DIR)/usr/share/mupen64plus/
	$(INSTALL) -D $(@D)/src/plugin/release/mupen64plus-video-GLideN64.so \
		$(TARGET_DIR)/usr/lib/mupen64plus/mupen64plus-video-gliden64.so
	$(INSTALL) -D $(@D)/ini/* \
		$(TARGET_DIR)/usr/share/mupen64plus/
	$(INSTALL) -D $(@D)/ini/* \
		$(TARGET_DIR)/recalbox/configs/mupen64/
endef

define MUPEN64PLUS_GLIDEN64_PRE_CONFIGURE_FIXUP
	chmod +x $(@D)/src/getRevision.sh
	sh $(@D)/src/getRevision.sh
	$(SED) 's|/opt/vc/include|$(STAGING_DIR)/usr/include|g' $(@D)/src/CMakeLists.txt
	$(SED) 's|/opt/vc/lib|$(STAGING_DIR)/usr/lib|g' $(@D)/src/CMakeLists.txt

endef

MUPEN64PLUS_GLIDEN64_PRE_CONFIGURE_HOOKS += MUPEN64PLUS_GLIDEN64_PRE_CONFIGURE_FIXUP


$(eval $(cmake-package))


