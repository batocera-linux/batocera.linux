################################################################################
#
# CITRA
#
################################################################################
# Version.: Commits on Jan 16, 2019
CITRA_VERSION = e1d1dcdcd93004b656e9c10eed7d9ff35604ee45
CITRA_SITE = https://github.com/citra-emu/citra.git
CITRA_SITE_METHOD=git
CITRA_GIT_SUBMODULES=YES
CITRA_DEPENDENCIES = sdl2 fmt boost

# Should be set when the package cannot be built inside the source tree but needs a separate build directory.
CITRA_SUPPORTS_IN_SOURCE_BUILD = NO

CITRA_CONF_OPTS  = -DENABLE_QT=OFF
CITRA_CONF_OPTS += -DENABLE_SDL2=ON
CITRA_CONF_OPTS += -DCMAKE_BUILD_TYPE=Release
CITRA_CONF_OPTS += -DENABLE_WEB_SERVICE=OFF
CITRA_CONF_OPTS += -DTHREADS_PREFER_PTHREAD_FLAG0=ON

define CITRA_INSTALL_TARGET_CMDS
	$(INSTALL) -D $(@D)/buildroot-build/bin/citra \
		$(TARGET_DIR)/usr/bin/citra
	
	cp -pr $(@D)/buildroot-build/externals/inih/*.so \
		$(TARGET_DIR)/usr/lib/

	cp -pr $(@D)/buildroot-build/externals/cubeb/*.so \
		$(TARGET_DIR)/usr/lib/

	cp -pr $(@D)/buildroot-build/externals/teakra/src/*.so \
		$(TARGET_DIR)/usr/lib/
endef

$(eval $(cmake-package))