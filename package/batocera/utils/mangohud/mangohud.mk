################################################################################
#
# MangoHud
#
################################################################################
# Version: Commits from Oct, 2021
MANGOHUD_VERSION = a8a0a245e69fbbca5263d2436fd1c04289375498
MANGOHUD_SITE =  $(call github,flightlessmango,MangoHud,$(MANGOHUD_VERSION))

MANGOHUD_DEPENDENCIES = host-libcurl host-python-mako host-glslang

ifeq ($(BR2_PACKAGE_LIBDRM),y)
	MANGOHUD_DEPENDENCIES += libdrm
endif

ifeq ($(BR2_PACKAGE_XSERVER_XORG_SERVER),y)
	MANGOHUD_DEPENDENCIES += xserver_xorg-server
endif

MANGOHUD_CONF_OPTS = -Dwith_xnvctrl=disabled

ifeq ($(BR2_PACKAGE_VULKAN_HEADERS),y)
    MANGOHUD_DEPENDENCIES += vulkan-headers
    MANGOHUD_CONF_OPTS += -Duse_vulkan=true
else
    MANGOHUD_CONF_OPTS += -Duse_vulkan=false
endif

ifeq ($(BR2_PACKAGE_XSERVER_XORG_SERVER),y)
	MANGOHUD_CONF_OPTS += -Dwith_x11=enabled
else
	MANGOHUD_CONF_OPTS += -Dwith_x11=disabled
endif

ifeq ($(BR2_PACKAGE_WAYLAND),y)
	MANGOHUD_CONF_OPTS += -Dwith_wayland=enabled
else
	MANGOHUD_CONF_OPTS += -Dwith_wayland=disabled
endif

# this is a not nice workaround
# i don't know why meson uses bad ssl certificates and doesn't manage to download them
# use submodule vulkan headers - https://github.com/flightlessmango/MangoHud/issues/968
define MANGOHUD_DWD_DEPENDENCIES
	mkdir -p $(@D)/subprojects/packagecache
	$(HOST_DIR)/bin/curl -L https://github.com/ocornut/imgui/archive/v1.81.tar.gz                  -o $(@D)/subprojects/packagecache/imgui-1.81.tar.gz
	$(HOST_DIR)/bin/curl -L https://wrapdb.mesonbuild.com/v2/imgui_1.81-1/get_patch                -o $(@D)/subprojects/packagecache/imgui-1.81-1-wrap.zip
	$(HOST_DIR)/bin/curl -L https://github.com/gabime/spdlog/archive/v1.8.5.tar.gz                 -o $(@D)/subprojects/packagecache/v1.8.5.tar.gz
	$(HOST_DIR)/bin/curl -L https://wrapdb.mesonbuild.com/v2/spdlog_1.8.5-1/get_patch              -o $(@D)/subprojects/packagecache/spdlog-1.8.5-1-wrap.zip
	$(HOST_DIR)/bin/curl -L https://github.com/KhronosGroup/Vulkan-Headers/archive/v1.2.158.tar.gz -o $(@D)/subprojects/packagecache/vulkan-headers-1.2.158.tar.gz
	$(HOST_DIR)/bin/curl -L https://wrapdb.mesonbuild.com/v2/vulkan-headers_1.2.158-2/get_patch    -o $(@D)/subprojects/packagecache/vulkan-headers-1.2.158-2-wrap.zip
endef
MANGOHUD_PRE_CONFIGURE_HOOKS += MANGOHUD_DWD_DEPENDENCIES

$(eval $(meson-package))
