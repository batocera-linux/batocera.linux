################################################################################
#
# CITRA
#
################################################################################
# Version.: Commits on Aug 10, 2019
CITRA_VERSION = d18d2a0a18a0d96b325812b874126387f8be0727
CITRA_SITE = https://github.com/citra-emu/citra.git
CITRA_SITE_METHOD=git
CITRA_GIT_SUBMODULES=YES
CITRA_LICENSE = GPLv2
CITRA_DEPENDENCIES = sdl2 fmt ffmpeg boost

# Should be set when the package cannot be built inside the source tree but needs a separate build directory.
CITRA_SUPPORTS_IN_SOURCE_BUILD = NO

CITRA_CONF_OPTS  = -DENABLE_QT=OFF
CITRA_CONF_OPTS += -DENABLE_SDL2=ON
CITRA_CONF_OPTS += -DCMAKE_BUILD_TYPE=Release
CITRA_CONF_OPTS += -DENABLE_WEB_SERVICE=OFF
CITRA_CONF_OPTS += -DENABLE_FFMPEG=ON

CITRA_CONF_ENV += LDFLAGS=-lpthread

define CITRA_INSTALL_TARGET_CMDS
        mkdir -p $(TARGET_DIR)/usr/bin
        mkdir -p $(TARGET_DIR)/usr/lib

	$(INSTALL) -D $(@D)/buildroot-build/bin/citra \
		$(TARGET_DIR)/usr/bin/citra

	cp -pr $(@D)/buildroot-build/externals/inih/*.so \
		$(TARGET_DIR)/usr/lib/

	cp -pr $(@D)/buildroot-build/externals/cubeb/*.so \
		$(TARGET_DIR)/usr/lib/

	cp -pr $(@D)/buildroot-build/externals/dynarmic/src/*.so \
		$(TARGET_DIR)/usr/lib/
	
	cp -pr $(@D)/buildroot-build/externals/teakra/src/*.so \
		$(TARGET_DIR)/usr/lib/
endef

$(eval $(cmake-package))
