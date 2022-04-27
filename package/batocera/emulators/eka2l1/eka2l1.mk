################################################################################
#
# eka2l1
#
################################################################################
#Version: 0.0.8.1 - 01 Mar 2022
EKA2L1_VERSION = 0.0.8.1
EKA2L1_SITE = https://github.com/EKA2L1/EKA2L1.git
EKA2L1_SITE_METHOD=git
EKA2L1_GIT_SUBMODULES=YES
EKA2L1_LICENSE = GPL-3.0
EKA2L1_DEPENDENCIES = qt5base qt5tools qt5multimedia
# Seem to be included as external packages, maybe not needed to be included here?
# fmt boost ffmpeg sdl2

# May be needed for translations.
#EKA2L1_CONF_OPTS = -DENABLE_QT_TRANSLATION=ON
#EKA2L1_CONF_OPTS = -DCMAKE_INSTALL_PREFIX= $(@D)/buildroot-build/eka2l1 $(TARGET_DIR)/usr/eka2l1
EKA2L1_CONF_OPTS = -DBUILD_SHARED_LIBS=OFF

# Should be set when the package cannot be built inside the source tree but needs a separate build directory.
EKA2L1_SUPPORTS_IN_SOURCE_BUILD = NO

# Sort this out once we have the binary.
#define EKA2L1_INSTALL_TARGET_CMDS
#    mkdir -p $(TARGET_DIR)/usr/bin
#    mkdir -p $(TARGET_DIR)/usr/lib
#	$(INSTALL) -D $(@D)/buildroot-build/bin/Release/citra-qt \
#		$(TARGET_DIR)/usr/bin/
#endef

$(eval $(cmake-package))
