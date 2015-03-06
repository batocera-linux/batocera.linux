################################################################################
#
# SCUMMVM
#
################################################################################
LIBRETRO_SCUMMVM_VERSION = 6a8f4b0d84b8cf72f76c54d745fcaaba3a7ac63a
LIBRETRO_SCUMMVM_SITE = $(call github,libretro,scummvm,$(LIBRETRO_SCUMMVM_VERSION))
#CXX="$(TARGET_CXX)" CC="$(TARGET_CC)" \
#	LD="$(TARGET_LD)" RANLIB="$(TARGET_RANLIB)" AR="$(TARGET_AR) cru"  \

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
