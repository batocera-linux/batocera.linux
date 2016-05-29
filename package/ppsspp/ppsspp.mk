################################################################################
#
# PPSSPP
#
################################################################################
# This is the commit for v1.2.2. The source tar.gz doesn't contain full dependencies
PPSSPP_VERSION = 8c9f3b9509e8a6850e086ec36a59ca7fa4082d60
PPSSPP_SITE = $(call github,hrydgard,ppsspp,$(PPSSPP_VERSION))
PPSSPP_GIT = https://github.com/hrydgard/ppsspp.git
PPSSPP_DEPENDENCIES = sdl2 zlib libzip linux zip

# Dirty hack to download submodules
define PPSSPP_EXTRACT_CMDS
	rm -rf $(@D)
	git clone --recursive --depth 1 $(PPSSPP_GIT) $(@D)
	touch $(@D)/.stamp_downloaded
endef

define PPSSPP_CONFIGURE_PI
	sed -i "s+/opt/vc+$(STAGING_DIR)/usr+g" $(@D)/CMakeLists.txt
endef

PPSSPP_PRE_CONFIGURE_HOOKS += PPSSPP_CONFIGURE_PI

define PPSSPP_INSTALL_TO_TARGET
	$(INSTALL) -D -m 0755 $(@D)/PPSSPPSDL $(TARGET_DIR)/usr/bin
	cp -R $(@D)/assets $(TARGET_DIR)/usr/bin
endef

PPSSPP_INSTALL_TARGET_CMDS = $(PPSSPP_INSTALL_TO_TARGET)

$(eval $(cmake-package))
