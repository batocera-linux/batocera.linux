################################################################################
#
# mupen64plus video GLIDEN64
#
################################################################################
# Version.: Commits on Jan 12, 2020
MUPEN64PLUS_GLIDEN64_VERSION = 495d9f959ef9c6443f45277c85049322faca5028
MUPEN64PLUS_GLIDEN64_SITE = $(call github,gonetz,GLideN64,$(MUPEN64PLUS_GLIDEN64_VERSION))
MUPEN64PLUS_GLIDEN64_LICENSE = GPLv2
MUPEN64PLUS_GLIDEN64_DEPENDENCIES = sdl2 alsa-lib mupen64plus-core
MUPEN64PLUS_GLIDEN64_CONF_OPTS = -DMUPENPLUSAPI=ON -DUSE_SYSTEM_LIBS=ON
MUPEN64PLUS_GLIDEN64_SUBDIR = /src/

ifeq ($(BR2_arm)$(BR2_aarch64),y)
	MUPEN64PLUS_GLIDEN64_CONF_OPTS += -DEGL=ON
endif

ifeq ($(BR2_ARM_CPU_HAS_NEON),y)
	MUPEN64PLUS_GLIDEN64_CONF_OPTS += -DNEON_OPT=ON
endif

ifeq ($(BR2_ENABLE_DEBUG),y)
	MUPEN64PLUS_GLIDEN64_RELTYPE= Debug
else
	MUPEN64PLUS_GLIDEN64_RELTYPE = Release
endif

define MUPEN64PLUS_GLIDEN64_INSTALL_TARGET_CMDS
	mkdir -p $(TARGET_DIR)/usr/share/mupen64plus/
	$(INSTALL) -D $(@D)/src/plugin/$(MUPEN64PLUS_GLIDEN64_RELTYPE)/mupen64plus-video-GLideN64.so \
		$(TARGET_DIR)/usr/lib/mupen64plus/mupen64plus-video-gliden64.so
	$(INSTALL) -D $(@D)/ini/* \
		$(TARGET_DIR)/usr/share/mupen64plus/
endef

define MUPEN64PLUS_GLIDEN64_PRE_CONFIGURE_FIXUP
	chmod +x $(@D)/src/getRevision.sh
	sh $(@D)/src/getRevision.sh
	$(SED) 's|/opt/vc/include|$(STAGING_DIR)/usr/include|g' $(@D)/src/CMakeLists.txt
	$(SED) 's|/opt/vc/lib|$(STAGING_DIR)/usr/lib|g' $(@D)/src/CMakeLists.txt
endef

MUPEN64PLUS_GLIDEN64_PRE_CONFIGURE_HOOKS += MUPEN64PLUS_GLIDEN64_PRE_CONFIGURE_FIXUP

$(eval $(cmake-package))
