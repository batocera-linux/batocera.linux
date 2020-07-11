################################################################################
#
# CITRA
#
################################################################################
# Version.: Commits on Jul 08, 2020
CITRA_VERSION = 96fa75fb93a3dea4a8fbe72bde23b16979057a43
CITRA_SITE = https://github.com/citra-emu/citra.git
CITRA_SITE_METHOD=git
CITRA_GIT_SUBMODULES=YES
CITRA_LICENSE = GPLv2
CITRA_DEPENDENCIES = qt5base qt5tools qt5multimedia fmt boost ffmpeg

# Should be set when the package cannot be built inside the source tree but needs a separate build directory.
CITRA_SUPPORTS_IN_SOURCE_BUILD = NO

CITRA_CONF_OPTS += -DCMAKE_BUILD_TYPE=Release
CITRA_CONF_OPTS += -DENABLE_WEB_SERVICE=OFF
CITRA_CONF_OPTS += -DENABLE_QT_TRANSLATION=ON
CITRA_CONF_OPTS += -DENABLE_FFMPEG=ON
CITRA_CONF_OPTS += -DARCHITECTURE=x86_64

CITRA_CONF_ENV += LDFLAGS=-lpthread

define CITRA_INSTALL_TARGET_CMDS
        mkdir -p $(TARGET_DIR)/usr/bin
        mkdir -p $(TARGET_DIR)/usr/lib

	$(INSTALL) -D $(@D)/buildroot-build/bin/citra-qt \
		$(TARGET_DIR)/usr/bin/

	cp -pr $(@D)/buildroot-build/externals/inih/*.so \
		$(TARGET_DIR)/usr/lib/

	cp -pr $(@D)/buildroot-build/externals/cubeb/*.so \
		$(TARGET_DIR)/usr/lib/

	cp -pr $(@D)/buildroot-build/externals/teakra/src/*.so \
		$(TARGET_DIR)/usr/lib/

	cp -pr $(@D)/buildroot-build/externals/lodepng/*.so \
		$(TARGET_DIR)/usr/lib/
endef

$(eval $(cmake-package))
