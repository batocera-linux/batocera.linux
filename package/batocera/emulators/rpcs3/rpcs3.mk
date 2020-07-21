################################################################################
#
# RPCS3
#
################################################################################

# last version without gcc-9 and qt bump
#RPCS3_VERSION = 491526b42185c864883176f5000e144b9ac3c83e

# original
#RPCS3_VERSION = cb66d05693504f4e453999af489786d05d2a8e51

# 1er january
#RPCS3_VERSION = 4c20881f8f40f4dfd45ffb3eca94ac206a56e7f9

# 1er december
#RPCS3_VERSION = 1a6e8e20dca9fd259e03c607d4c9d93ae5375298

# Jun, 30 2020 release
RPCS3_VERSION = v0.0.11

RPCS3_SITE = https://github.com/RPCS3/rpcs3.git
RPCS3_SITE_METHOD=git
RPCS3_GIT_SUBMODULES=YES
RPCS3_LICENSE = GPLv2
RPCS3_DEPENDENCIES = qt5declarative libxml2 mesa3d libglu openal alsa-lib libevdev libglew libusb ffmpeg

RPCS3_CONF_OPTS += -DUSE_PULSE=OFF
RPCS3_CONF_OPTS += -DUSE_SYSTEM_FFMPEG=ON
RPCS3_CONF_OPTS += -DUSE_SYSTEM_LIBPNG=ON
RPCS3_CONF_OPTS += -DUSE_DISCORD_RPC=OFF
RPCS3_CONF_OPTS += -DUSE_VULKAN=OFF
#RPCS3_CONF_OPTS += -DCMAKE_CROSSCOMPILING=ON
RPCS3_CONF_OPTS += -DWITH_LLVM=ON
RPCS3_CONF_OPTS += -DBUILD_LLVM_SUBMODULE=ON
RPCS3_CONF_OPTS += -DUSE_NATIVE_INSTRUCTIONS=OFF
RPCS3_CONF_OPTS += -DBUILD_SHARED_LIBS=OFF
RPCS3_CONF_OPTS += -DCMAKE_BUILD_TYPE=Release
#RPCS3_CONF_OPTS += -DLLVM_USE_HOST_TOOLS=ON

RPCS3_CONF_ENV += PATH="/x86_64/host/x86_64-buildroot-linux-gnu/sysroot/usr/bin:$$PATH"

define RPCS3_BUILD_CMDS
	$(TARGET_CONFIGURE_OPTS) CXX="$(TARGET_CXX)" CC="$(TARGET_CC)" \
		CC_FOR_BUILD="$(TARGET_CC)" GCC_FOR_BUILD="$(TARGET_CC)" \
		CXX_FOR_BUILD="$(TARGET_CXX)" LD_FOR_BUILD="$(TARGET_LD)" \
                CROSS_COMPILE="$(STAGING_DIR)/usr/bin/" \
                PREFIX="/x86_64/host/x86_64-buildroot-linux-gnu/sysroot/" \
                PKG_CONFIG="/x86_64/host/x86_64-buildroot-linux-gnu/sysroot/usr/bin/pkg-config" \
		$(MAKE) -C $(@D)
endef

#		LD_LIBRARY_PATH="/x86_64/host/x86_64-buildroot-linux-gnu/sysroot/usr/lib:/x86_64/host/x86_64-buildroot-linux-gnu/sysroot/lib:$LD_LIBRARY_PATH" \

$(eval $(cmake-package))
