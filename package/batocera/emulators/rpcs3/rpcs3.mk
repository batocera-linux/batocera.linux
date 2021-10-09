################################################################################
#
# RPCS3
#
################################################################################

# 2021 Sep, 1 release
RPCS3_VERSION = v0.0.18

RPCS3_SITE = https://github.com/RPCS3/rpcs3.git
RPCS3_SITE_METHOD=git
RPCS3_GIT_SUBMODULES=YES
RPCS3_LICENSE = GPLv2
RPCS3_DEPENDENCIES = qt5declarative libxml2 mesa3d libglu openal alsa-lib libevdev libglew libusb ffmpeg faudio wolfssl

RPCS3_CONF_OPTS += -DUSE_PULSE=OFF
RPCS3_CONF_OPTS += -DUSE_SYSTEM_FFMPEG=ON
RPCS3_CONF_OPTS += -DUSE_SYSTEM_LIBPNG=ON
RPCS3_CONF_OPTS += -DUSE_DISCORD_RPC=OFF
RPCS3_CONF_OPTS += -DUSE_VULKAN=ON
RPCS3_CONF_OPTS += -DCMAKE_CROSSCOMPILING=ON
RPCS3_CONF_OPTS += -DWITH_LLVM=ON
RPCS3_CONF_OPTS += -DBUILD_LLVM_SUBMODULE=ON
RPCS3_CONF_OPTS += -DUSE_NATIVE_INSTRUCTIONS=OFF
RPCS3_CONF_OPTS += -DBUILD_SHARED_LIBS=OFF
RPCS3_CONF_OPTS += -DUSE_SYSTEM_FAUDIO=ON
RPCS3_CONF_OPTS += -DUSE_SYSTEM_WOLFSSL=ON
RPCS3_CONF_OPTS += -DCMAKE_BUILD_TYPE=Release

RPCS3_CONF_ENV += PATH="$(STAGING_DIR)/usr/bin:$$PATH"
RPCS3_CONF_ENV += LD_LIBRARY_PATH="$(HOST_DIR)/lib:$(HOST_DIR)/usr/lib:$$LD_LIBRARY_PATH"

define RPCS3_BUILD_CMDS
	$(TARGET_CONFIGURE_OPTS) CXX="$(TARGET_CXX)" CC="$(TARGET_CC)" \
		CC_FOR_BUILD="$(TARGET_CC)" GCC_FOR_BUILD="$(TARGET_CC)" \
		CXX_FOR_BUILD="$(TARGET_CXX)" LD_FOR_BUILD="$(TARGET_LD)" \
                CROSS_COMPILE="$(STAGING_DIR)/usr/bin/" LD_LIBRARY_PATH="$(HOST_DIR)/usr/lib:$(HOST_DIR)/lib:$(LD_LIBRARY_PATH)" \
                PREFIX="$(STAGING_DIR)" \
                PKG_CONFIG="$(STAGING_DIR)/usr/bin/pkg-config" \
		$(MAKE) -C $(@D)
endef

define RPCS3_INSTALL_EVMAPY
	mkdir -p $(TARGET_DIR)/usr/share/evmapy
	$(INSTALL) -D -m 0644 $(BR2_EXTERNAL_BATOCERA_PATH)/package/batocera/emulators/rpcs3/evmapy.keys $(TARGET_DIR)/usr/share/evmapy/ps3.keys
endef

RPCS3_POST_INSTALL_TARGET_HOOKS = RPCS3_INSTALL_EVMAPY

$(eval $(cmake-package))
