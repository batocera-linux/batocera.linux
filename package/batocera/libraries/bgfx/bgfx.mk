################################################################################
#
# bgfx
#
################################################################################

BGFX_VERSION = v1.143.9262-545
BGFX_SITE = https://github.com/bkaradzic/bgfx.cmake
BGFX_SITE_METHOD = git
BGFX_GIT_SUBMODULES = YES
BGFX_LICENSE = CC0 1.0 Universal
BGFX_LICENSE_FILES = LICENSE
BGFX_DEPENDENCIES = xlib_libX11
BGFX_SUPPORTS_IN_SOURCE_BUILD = NO
BGFX_INSTALL_STAGING = YES

ifeq ($(BR2_PACKAGE_HAS_LIBGL),y)
BGFX_DEPENDENCIES += libgl
else ifeq ($(BR2_PACKAGE_HAS_LIBGLES),y)
BGFX_DEPENDENCIES += libgles
endif

BGFX_CONF_OPTS += -DCMAKE_BUILD_TYPE=Release \
                  -DBGFX_LIBRARY_TYPE=SHARED \
                  -DBGFX_BUILD_TOOLS=OFF \
                  -DBGFX_BUILD_EXAMPLES=OFF \
                  -DBGFX_CONFIG_MULTITHREADED=ON \
                  -DBGFX_CONFIG_MAX_FRAME_BUFFERS=256

ifeq ($(BR2_PACKAGE_WAYLAND),y)
BGFX_CONF_OPTS += -DBGFX_WITH_WAYLAND=ON
BGFX_DEPENDENCIES += wayland
else
BGFX_CONF_OPTS += -DBGFX_WITH_WAYLAND=OFF
endif

# patch version details from vpinball - platforms/config.sh
BGFX_PATCH_VERSION = 66fbca4dfe93da62b0f145bec872ee96df326afa
BGFX_PATCH_SOURCE = $(BGFX_PATCH_VERSION).tar.gz
BGFX_EXTRA_DOWNLOADS = \
    $(addprefix \
    https://github.com/vbousquet/bgfx/archive/,\
    $(BGFX_PATCH_SOURCE))

# Post-extract hook to swap out the default bgfx submodule with the patch archive.
define BGFX_EXTRACT_PATCH
	rm -rf $(@D)/bgfx
	$(TAR) -xf $(BGFX_DL_DIR)/$(BGFX_PATCH_SOURCE) -C $(@D)
	mv $(@D)/bgfx-$(BGFX_PATCH_VERSION) $(@D)/bgfx
endef
BGFX_POST_EXTRACT_HOOKS += BGFX_EXTRACT_PATCH

$(eval $(cmake-package))
