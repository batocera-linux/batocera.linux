################################################################################
#
# EKA2L1
#
################################################################################
# Version: Commits on Oct 24, 2026
EKA2L1_VERSION = e756b507b0d7b63ae8db88f78461afd7237e9308
EKA2L1_SITE = https://github.com/EKA2L1/EKA2L1.git
EKA2L1_SITE_METHOD=git
EKA2L1_GIT_SUBMODULES=YES
EKA2L1_LICENSE = GPLv3
EKA2L1_LICENSE_FILES = LICENSE
EKA2L1_DEPENDENCIES = qt6base qt6multimedia qt6svg qt6tools sdl2
EKA2L1_EMULATOR_INFO = eka2l1.emulator.yml

EKA2L1_SUPPORTS_IN_SOURCE_BUILD = NO

EKA2L1_CONF_OPTS += -DCMAKE_BUILD_TYPE=Release
EKA2L1_CONF_OPTS += -DBUILD_SHARED_LIBS=OFF
EKA2L1_CONF_OPTS += -DEKA2L1_ENABLE_SCRIPTING_ABILITY=OFF
EKA2L1_CONF_OPTS += -DEKA2L1_BUILD_TOOLS=OFF
EKA2L1_CONF_OPTS += -DEKA2L1_BUILD_TESTS=OFF
EKA2L1_CONF_OPTS += -DEKA2L1_ENABLE_DISCORD_RICH_PRESENCE=OFF
EKA2L1_CONF_OPTS += -DEKA2L1_ENABLE_QT_CAMERA=OFF
EKA2L1_CONF_OPTS += -DENABLE_PROGRAMS=OFF # for mbedtls

ifeq ($(BR2_PACKAGE_BATOCERA_WAYLAND),y)
    EKA2L1_DEPENDENCIES += wayland qt6wayland
endif

ifeq ($(BR2_PACKAGE_XORG7),y)
    EKA2L1_DEPENDENCIES += xlib_libX11
endif

# batocera-pad.keys: the default pad layout, turned into an EKA2L1 key profile by batocera-launch
# (not an evmapy file: EKA2L1 reads the pad itself)
define EKA2L1_INSTALL_TARGET_CMDS
    mkdir -p $(TARGET_DIR)/usr/eka2l1
    $(TARGET_STRIP) $(@D)/buildroot-build/bin/eka2l1_qt
    cp -R $(@D)/buildroot-build/bin/* \
                $(TARGET_DIR)/usr/eka2l1/
    $(INSTALL) -D -m 0644 $(BR2_EXTERNAL_BATOCERA_PATH)/package/batocera/emulators/eka2l1/batocera-pad.keys \
        $(TARGET_DIR)/usr/eka2l1/batocera-pad.keys
endef

$(eval $(cmake-package))
$(eval $(emulator-info-package))
