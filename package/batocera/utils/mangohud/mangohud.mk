################################################################################
#
# mangohud
#
################################################################################

MANGOHUD_VERSION = v0.8.4
MANGOHUD_SITE =  $(call github,flightlessmango,MangoHud,$(MANGOHUD_VERSION))

MANGOHUD_DEPENDENCIES += host-libcurl host-python-mako host-glslang dbus
MANGOHUD_DEPENDENCIES += json-for-modern-cpp

ifeq ($(BR2_PACKAGE_LIBXKBCOMMON),y)
    MANGOHUD_DEPENDENCIES += libxkbcommon
endif

ifeq ($(BR2_PACKAGE_LIBDRM),y)
    MANGOHUD_DEPENDENCIES += libdrm
endif

ifeq ($(BR2_PACKAGE_XSERVER_XORG_SERVER),y)
    MANGOHUD_DEPENDENCIES += xserver_xorg-server
endif

MANGOHUD_CONF_OPTS = -Dwith_xnvctrl=disabled

ifeq ($(BR2_PACKAGE_BATOCERA_VULKAN),y)
    MANGOHUD_DEPENDENCIES += vulkan-headers
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

define MANGOHUD_DWD_DEPENDENCIES
	mkdir -p $(@D)/subprojects/packagecache
	for wrap_file in $(@D)/subprojects/*.wrap; do \
		[ -f "$$wrap_file" ] || continue; \
		if grep -q '\[wrap-file\]' "$$wrap_file"; then \
			SRC_URL=$$(sed -n 's/^source_url *= *//p' "$$wrap_file" | tr -d '\r'); \
			SRC_FILE=$$(sed -n 's/^source_filename *= *//p' "$$wrap_file" | tr -d '\r'); \
			if [ -n "$$SRC_URL" ] && [ -n "$$SRC_FILE" ]; then \
				$(HOST_DIR)/bin/curl -L -o "$(@D)/subprojects/packagecache/$$SRC_FILE" "$$SRC_URL" || exit 1; \
			fi; \
			PATCH_URL=$$(sed -n 's/^patch_url *= *//p' "$$wrap_file" | tr -d '\r'); \
			PATCH_FILE=$$(sed -n 's/^patch_filename *= *//p' "$$wrap_file" | tr -d '\r'); \
			if [ -n "$$PATCH_URL" ] && [ -n "$$PATCH_FILE" ]; then \
				$(HOST_DIR)/bin/curl -L -o "$(@D)/subprojects/packagecache/$$PATCH_FILE" "$$PATCH_URL" || exit 1; \
			fi; \
		fi; \
	done
endef
MANGOHUD_PRE_CONFIGURE_HOOKS += MANGOHUD_DWD_DEPENDENCIES

define MANGOHUD_POST_INSTALL_CLEAN
	rm -f $(TARGET_DIR)/usr/share/man/man1/mangohud.1
endef

MANGOHUD_POST_INSTALL_TARGET_HOOKS = MANGOHUD_POST_INSTALL_CLEAN

$(eval $(meson-package))
