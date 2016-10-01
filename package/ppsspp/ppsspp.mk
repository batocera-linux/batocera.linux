################################################################################
#
# PPSSPP
#
################################################################################
PPSSPP_VERSION = v1.2.2
PPSSPP_SITE = $(call github,hrydgard,ppsspp,$(PPSSPP_VERSION))
PPSSPP_GIT = https://github.com/hrydgard/ppsspp.git
PPSSPP_DEPENDENCIES = sdl2 zlib libzip linux zip

# required at least on x86
ifeq ($(BR2_PACKAGE_LIBGLU),y)
PPSSPP_DEPENDENCIES += libglu
endif

# Dirty hack to download submodules
define PPSSPP_EXTRACT_CMDS
	rm -rf $(@D)
	git clone --recursive $(PPSSPP_GIT) $(@D)
	touch $(@D)/.stamp_downloaded
	cd $(@D) && \
	git reset --hard $(PPSSPP_VERSION)
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

ifeq ($(BR2_PACKAGE_MALI_OPENGLES_SDK),y)
	PPSSPP_CONF_OPTS += -DMALISDK=1
endif

ifeq ($(BR2_PACKAGE_RECALBOX_TARGET_RPI3)$(BR2_PACKAGE_RECALBOX_TARGET_XU4),y)
	PPSSPP_CONF_OPTS += -DARMV7=1
endif
$(eval $(cmake-package))

