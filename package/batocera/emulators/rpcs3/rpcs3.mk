################################################################################
#
# rpcs3
#
################################################################################

RPCS3_VERSION = v0.0.25
RPCS3_SITE = https://github.com/RPCS3/rpcs3.git
RPCS3_SITE_METHOD=git
RPCS3_GIT_SUBMODULES=YES
RPCS3_LICENSE = GPLv2
RPCS3_DEPENDENCIES += qt5declarative libxml2 mesa3d libglu openal alsa-lib 
RPCS3_DEPENDENCIES += libevdev libglew libusb ffmpeg faudio wolfssl

RPCS3_SUPPORTS_IN_SOURCE_BUILD = NO

RPCS3_CONF_OPTS = -DCMAKE_BUILD_TYPE=Release \
    -DCMAKE_CROSSCOMPILING=ON -DBUILD_SHARED_LIBS=OFF \
    -DUSE_SYSTEM_FFMPEG=ON -DUSE_NATIVE_INSTRUCTIONS=OFF \
	-DBUILD_LLVM_SUBMODULE=OFF -DLLVM_DIR=$(@D)/llvmlibs/lib/cmake/llvm/ \
	-DUSE_PRECOMPILED_HEADERS=OFF -DUSE_SYSTEM_CURL=ON

define RPCS3_LLVM_LIBS
	mkdir -p $(@D)/llvmlibs
    $(HOST_DIR)/bin/curl -L https://github.com/RPCS3/llvm-mirror/releases/download/custom-build/llvmlibs-linux.tar.gz -o $(@D)/llvmlibs-linux.tar.gz
	cd $(@D) && tar -xf llvmlibs-linux.tar.gz -C $(@D)/llvmlibs
endef

define RPCS3_BUILD_CMDS
	$(TARGET_CONFIGURE_OPTS) \
		$(MAKE) -C $(@D)/buildroot-build
endef

define RPCS3_INSTALL_EVMAPY
	mkdir -p $(TARGET_DIR)/usr/share/evmapy
	$(INSTALL) -D -m 0644 $(BR2_EXTERNAL_BATOCERA_PATH)/package/batocera/emulators/rpcs3/evmapy.keys \
	    $(TARGET_DIR)/usr/share/evmapy/ps3.keys
endef

RPCS3_PRE_CONFIGURE_HOOKS = RPCS3_LLVM_LIBS
RPCS3_POST_INSTALL_TARGET_HOOKS = RPCS3_INSTALL_EVMAPY

$(eval $(cmake-package))
