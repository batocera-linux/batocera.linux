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
RPCS3_VERSION = 1a6e8e20dca9fd259e03c607d4c9d93ae5375298

RPCS3_SITE = https://github.com/RPCS3/rpcs3.git
RPCS3_SITE_METHOD=git
RPCS3_GIT_SUBMODULES=YES
RPCS3_LICENSE = GPLv2
RPCS3_DEPENDENCIES = qt5declarative libxml2 mesa3d libglu openal alsa-lib libevdev libglew libusb ffmpeg

RPCS3_CONF_OPTS += -DUSE_PULSE=OFF
RPCS3_CONF_OPTS += -DUSE_SYSTEM_FFMPEG=ON
RPCS3_CONF_OPTS += -DUSE_SYSTEM_LIBPNG=ON
RPCS3_CONF_OPTS += -DUSE_DISCORD_RPC=OFF

RPCS3_CONF_OPTS += -DCMAKE_CROSSCOMPILING=OFF
define RPCS3_BUILD_CMDS
        LD_LIBRARY_PATH=$(HOST_DIR)/lib $(TARGET_MAKE_ENV) $(MAKE) -C $(@D)
endef

define RPCS3_INSTALL_LIBS
        cp $(@D)/rpcs3/rpcs3qt/librpcs3_ui.so $(TARGET_DIR)/usr/lib/
        cp $(@D)/rpcs3/Emu/librpcs3_emu.so $(TARGET_DIR)/usr/lib/
        cp $(@D)/asmjitsrc/libasmjit.so $(TARGET_DIR)/usr/lib/
        cp $(@D)/3rdparty/yaml-cpp/libyaml-cpp.so.0.6 $(TARGET_DIR)/usr/lib/
        cp $(@D)/3rdparty/xxHash/cmake_unofficial/libxxhash.so.0.6.5 $(TARGET_DIR)/usr/lib/
        cp $(@D)/3rdparty/llvm_build/lib/libLLVM*.so.9svn $(TARGET_DIR)/usr/lib/
endef

RPCS3_POST_INSTALL_TARGET_HOOKS += RPCS3_INSTALL_LIBS

$(eval $(cmake-package))
