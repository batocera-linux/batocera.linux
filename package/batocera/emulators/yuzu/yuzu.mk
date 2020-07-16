################################################################################
#
# YUZU
#
################################################################################
# Version.: Commits on Jul 14, 2020
YUZU_VERSION = 263200f982f1c8509450721cf5fa9d8639c198ef
YUZU_SITE = https://github.com/yuzu-emu/yuzu.git
YUZU_SITE_METHOD=git
YUZU_GIT_SUBMODULES=YES
YUZU_LICENSE = GPLv2
YUZU_DEPENDENCIES = qt5base qt5tools qt5multimedia fmt boost ffmpeg zstd

# Should be set when the package cannot be built inside the source tree but needs a separate build directory.
YUZU_SUPPORTS_IN_SOURCE_BUILD = NO

YUZU_CONF_OPTS += -DCMAKE_BUILD_TYPE=Release
YUZU_CONF_OPTS += -DENABLE_WEB_SERVICE=OFF
YUZU_CONF_OPTS += -DENABLE_QT_TRANSLATION=ON
YUZU_CONF_OPTS += -DENABLE_FFMPEG=ON
YUZU_CONF_OPTS += -DARCHITECTURE=x86_64

YUZU_CONF_ENV += LDFLAGS=-lpthread

define YUZU_INSTALL_TARGET_CMDS
        mkdir -p $(TARGET_DIR)/usr/bin
        mkdir -p $(TARGET_DIR)/usr/lib

	$(INSTALL) -D $(@D)/buildroot-build/bin/yuzu-qt \
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
