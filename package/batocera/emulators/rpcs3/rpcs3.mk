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
RPCS3_DEPENDENCIES = qt5declarative libxml2 mesa3d libglu openal alsa-lib libevdev libglew libusb ffmpeg llvm

RPCS3_CONF_OPTS += -DUSE_PULSE=OFF
RPCS3_CONF_OPTS += -DUSE_SYSTEM_FFMPEG=ON
RPCS3_CONF_OPTS += -DUSE_SYSTEM_LIBPNG=ON
RPCS3_CONF_OPTS += -DUSE_DISCORD_RPC=OFF
RPCS3_CONF_OPTS += -DUSE_VULKAN=OFF
RPCS3_CONF_OPTS += -DCMAKE_CROSSCOMPILING=ON
RPCS3_CONF_OPTS += -DWITH_LLVM=ON
RPCS3_CONF_OPTS += -DBUILD_LLVM_SUBMODULE=ON
RPCS3_CONF_OPTS += -DUSE_NATIVE_INSTRUCTIONS=OFF
RPCS3_CONF_OPTS += -DBUILD_SHARED_LIBS=FALSE
RPCS3_CONF_OPTS += -DCMAKE_BUILD_TYPE=Release

RPCS3_CONF_ENV += LD_LIBRARY_PATH="$(TARGET_DIR)/usr/lib:$LD_LIBRARY_PATH"

#RPCS3_CONF_OPTS += -DLLVM_USE_HOST_TOOLS=ON

# It seems to support in-source tree build, but easier to track down issues
#RPCS3_SUPPORTS_IN_SOURCE_BUILD = NO

#RPCS3_CONF_OPTS += -DCMAKE_EXE_LINKER_FLAGS="-L$(STAGING_DIR)/usr/lib"

# Use native llvm-tblgen from host-llvm (needed for cross-compilation)
#RPCS3_CONF_OPTS += -DLLVM_TABLEGEN=/usr/bin/llvm-tblgen

# Use native llvm-config from host-llvm (needed for cross-compilation)
#RPCS3_CONF_OPTS += -DLLVM_CONFIG_PATH=/usr/bin/llvm-config

define RPCS3_BUILD_CMDS
	#LD_LIBRARY_PATH=$(HOST_DIR)/lib
	$(TARGET_CONFIGURE_OPTS) $(MAKE) -C $(@D)
endef

$(eval $(cmake-package))
