################################################################################
#
# SCUMMVM
#
################################################################################
# VERSION.: Commits on Oct 9, 2018
LIBRETRO_SCUMMVM_VERSION = 20d71cd7189ae7fdd453a3041f3103bffabea13e
LIBRETRO_SCUMMVM_SITE = $(call github,libretro,scummvm,$(LIBRETRO_SCUMMVM_VERSION))

define LIBRETRO_SCUMMVM_BUILD_CMDS
	CFLAGS="$(TARGET_CFLAGS)" CXXFLAGS="$(TARGET_CXXFLAGS)" LDFLAGS="-shared -Wl,--no-undefined" $(MAKE) \
	TOOLSET="$(TARGET_CROSS)" \
	-C $(@D)/backends/platform/libretro/build platform="$(LIBRETRO_PLATFORM)"
endef

define LIBRETRO_SCUMMVM_INSTALL_TARGET_CMDS
	$(INSTALL) -D $(@D)/backends/platform/libretro/build/scummvm_libretro.so \
		$(TARGET_DIR)/usr/lib/libretro/scummvm_libretro.so
endef

$(eval $(generic-package))
