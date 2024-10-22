################################################################################
#
# mangohud
#
################################################################################
# Version: Commits from Jun 15, 2024
MANGOHUD_VERSION = 12620c91eaca0917a7939a92ec33915cadf24475
MANGOHUD_SITE =  $(call github,flightlessmango,MangoHud,$(MANGOHUD_VERSION))

MANGOHUD_DEPENDENCIES = host-libcurl host-python-mako host-glslang dbus json-for-modern-cpp

ifeq ($(BR2_PACKAGE_LIBDRM),y)
    MANGOHUD_DEPENDENCIES += libdrm
endif

ifeq ($(BR2_PACKAGE_XSERVER_XORG_SERVER),y)
    MANGOHUD_DEPENDENCIES += xserver_xorg-server
endif

MANGOHUD_CONF_OPTS = -Dwith_xnvctrl=disabled

ifeq ($(BR2_PACKAGE_BATOCERA_VULKAN),y)
    MANGOHUD_DEPENDENCIES += vulkan-headers
    MANGOHUD_CONF_OPTS += -Duse_vulkan=true
else
    MANGOHUD_CONF_OPTS += -Duse_vulkan=false
endif

ifeq ($(BR2_PACKAGE_XORG7),y)
    MANGOHUD_CONF_OPTS += -Dwith_x11=enabled
else
    MANGOHUD_CONF_OPTS += -Dwith_x11=disabled
endif

ifeq ($(BR2_PACKAGE_BATOCERA_WAYLAND),y)
    MANGOHUD_DEPENDENCIES += wayland
    MANGOHUD_CONF_OPTS += -Dwith_wayland=enabled
else
    MANGOHUD_CONF_OPTS += -Dwith_wayland=disabled
endif

# this is a not nice workaround
# i don't know why meson uses bad ssl certificates and doesn't manage to download them
# use submodule vulkan headers - https://github.com/flightlessmango/MangoHud/issues/968
define MANGOHUD_DWD_DEPENDENCIES
	mkdir -p $(@D)/subprojects/packagecache
	$(HOST_DIR)/bin/curl -L https://github.com/ocornut/imgui/archive/refs/tags/v1.89.9.tar.gz \
        -o $(@D)/subprojects/packagecache/imgui-1.89.9.tar.gz
	$(HOST_DIR)/bin/curl -L https://wrapdb.mesonbuild.com/v2/imgui_1.89.9-1/get_patch \
        -o $(@D)/subprojects/packagecache/imgui_1.89.9-1_patch.zip
	$(HOST_DIR)/bin/curl -L https://github.com/gabime/spdlog/archive/refs/tags/v1.14.1.tar.gz \
        -o $(@D)/subprojects/packagecache/spdlog-1.14.1.tar.gz
	$(HOST_DIR)/bin/curl -L https://wrapdb.mesonbuild.com/v2/spdlog_1.14.1-1/get_patch \
        -o $(@D)/subprojects/packagecache/spdlog_1.14.1-1_patch.zip
	$(HOST_DIR)/bin/curl -L https://github.com/KhronosGroup/Vulkan-Headers/archive/v1.2.158.tar.gz \
        -o $(@D)/subprojects/packagecache/vulkan-headers-1.2.158.tar.gz
	$(HOST_DIR)/bin/curl -L https://wrapdb.mesonbuild.com/v2/vulkan-headers_1.2.158-2/get_patch \
        -o $(@D)/subprojects/packagecache/vulkan-headers-1.2.158-2-wrap.zip
	$(HOST_DIR)/bin/curl -L https://github.com/epezent/implot/archive/refs/tags/v0.16.zip \
        -o $(@D)/subprojects/packagecache/implot-0.16.zip
	$(HOST_DIR)/bin/curl -L https://wrapdb.mesonbuild.com/v2/implot_0.16-1/get_patch \
        -o $(@D)/subprojects/packagecache/implot_0.16-1_patch.zip
endef
MANGOHUD_PRE_CONFIGURE_HOOKS += MANGOHUD_DWD_DEPENDENCIES


define MANGOHUD_POST_INSTALL_CLEAN
	rm -f $(TARGET_DIR)/usr/share/man/man1/mangohud.1
endef

MANGOHUD_POST_INSTALL_TARGET_HOOKS = MANGOHUD_POST_INSTALL_CLEAN


$(eval $(meson-package))
