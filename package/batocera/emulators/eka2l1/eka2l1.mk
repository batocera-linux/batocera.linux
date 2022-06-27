################################################################################
#
# eka2l1
#
################################################################################
#Version: 0.0.8.1 - 30 May 2022
#EKA2L1_VERSION = d90fd0c3e056c88498abb8f674b25604a2c80771
EKA2L1_SOURCE = 
EKA2L1_VERSION = 1.0.0-001
#EKA2L1_SITE = https://github.com/EKA2L1/EKA2L1.git
#EKA2L1_SITE_METHOD=git
#EKA2L1_GIT_SUBMODULES=YES
EKA2L1_LICENSE = GPL-3.0
#EKA2L1_DEPENDENCIES = qt5base qt5tools qt5multimedia
## Seem to be included as external packages, maybe not needed to be included here?
##fmt boost ffmpeg sdl2
#
## May be needed for translations.
##EKA2L1_CONF_OPTS = -DENABLE_QT_TRANSLATION=ON
#
## EKA2L1 compiles most of its stuff from its submodules, and errors out if attempting to use "non-static" libraries. The build test also fails so it must be forced to off for now (binary seems unaffected by this).
#EKA2L1_CONF_OPTS = -DBUILD_SHARED_LIBS=OFF -DEKA2L1_BUILD_TESTS=OFF
#
## Does this matter? The readme says to do it if not using Qt5Creator but I'm not seeing where this would actually be in Batocera.
##EKA2L1_CONF_OPTS += -DCMAKE_PREFIX_PATH="$(STAGING_DIR)"
#
## Should be set when the package cannot be built inside the source tree but needs a separate build directory.
#EKA2L1_SUPPORTS_IN_SOURCE_BUILD = NO
#
## Grab the .git folder to ensure git variables apply during the build. Should be fixed upstream in the future.
##define EKA2L1_FIXGIT
##    cp -r $(BR2_DL_DIR)/eka2l1/git/.git $(@D)
##endef
#
##EKA2L1_PRE_CONFIGURE_HOOKS += EKA2L1_FIXGIT
#
#define EKA2L1_INSTALL_TARGET_CMDS
#    mkdir -p $(TARGET_DIR)/usr/bin
#    $(INSTALL) -D $(@D)/buildroot-build/bin/eka2l1_qt \
#        $(TARGET_DIR)/usr/bin/
#endef
#
#$(eval $(cmake-package))

define EKA2L1_INSTALL_TARGET_CMDS
	mkdir -p $(TARGET_DIR)/usr/bin
	$(INSTALL) -D -m 0555 "$(BR2_EXTERNAL_BATOCERA_PATH)/package/batocera/emulators/eka2l1/eka2l1-qt-x64.AppImage" "${TARGET_DIR}/usr/bin/eka2l1-qt"
endef

# Hotkeys
#define EKA2L1_EVMAP
#	mkdir -p $(TARGET_DIR)/usr/share/evmapy
#
#	cp -prn $(BR2_EXTERNAL_BATOCERA_PATH)/package/batocera/emulators/eka2l1/ngage.eka2l1.keys \
#		$(TARGET_DIR)/usr/share/evmapy
#endef

#EKA2L1_POST_INSTALL_TARGET_HOOKS = EKA2L1_EVMAP

$(eval $(generic-package))
