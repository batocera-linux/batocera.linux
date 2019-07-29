################################################################################
#
# RPCS3
#
################################################################################

RPCS3_VERSION = 997e3046e303662e73cc595997d4776e09100165
RPCS3_SITE = https://github.com/RPCS3/rpcs3.git
RPCS3_SITE_METHOD=git
RPCS3_GIT_SUBMODULES=YES
RPCS3_LICENSE = GPLv2
RPCS3_DEPENDENCIES = qt5declarative libxml2 mesa3d libglu openal alsa-lib libevdev libglew libusb ffmpeg

RPCS3_CONF_OPTS += -DUSE_PULSE=OFF
RPCS3_CONF_OPTS += -DUSE_SYSTEM_FFMPEG=ON
RPCS3_CONF_OPTS += -DUSE_SYSTEM_LIBPNG=ON

#RPCS3_CONF_OPTS += -DBUILD_LLVM_SUBMODULE=OFF
RPCS3_CONF_OPTS += -DWITH_LLVM=OFF

$(eval $(cmake-package))
