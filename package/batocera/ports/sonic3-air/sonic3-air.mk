################################################################################
#
# sonic3-air
#
################################################################################

SONIC3_AIR_VERSION = v25.02.15.0-test
SONIC3_AIR_SITE = https://github.com/Eukaryot/sonic3air.git
SONIC3_AIR_SITE_METHOD = git
SONIC3_AIR_GIT_SUBMODULES = YES
SONIC3_AIR_LICENSE = GPL-3.0
SONIC3_AIR_LICENSE_FILE = COPYING.txt
# CMakeLists.txt in subfolder
SONIC3_AIR_SUBDIR = Oxygen/sonic3air/build/_cmake

SONIC3_AIR_DEPENDENCIES += alsa-lib pulseaudio libcurl libglu
SONIC3_AIR_DEPENDENCIES += xlib_libXxf86vm xlib_libXcomposite zlib

ifeq ($(BR2_PACKAGE_BATOCERA_TARGET_BCM2711),y)
SONIC3_AIR_DEPENDENCIES += mesa3d-rpi4
else
SONIC3_AIR_DEPENDENCIES += mesa3d
endif

SONIC3_AIR_SUPPORTS_IN_SOURCE_BUILD = NO

SONIC3_AIR_CONF_OPTS += -DCMAKE_BUILD_TYPE=Release
SONIC3_AIR_CONF_OPTS += -DBUILD_SHARED_LIBS=OFF
SONIC3_AIR_CONF_OPTS += -DUSE_DISCORD=OFF

define SONIC3_AIR_INSTALL_TARGET_CMDS
    mkdir -p $(TARGET_DIR)/usr/bin/sonic3-air
	# copy binary
	cp $(@D)/Oxygen/sonic3air/sonic3air_linux $(TARGET_DIR)/usr/bin/sonic3-air
	# copy config files
	cp $(@D)/Oxygen/sonic3air/config.json $(TARGET_DIR)/usr/bin/sonic3-air
	cp $(@D)/Oxygen/sonic3air/oxygenproject.json $(TARGET_DIR)/usr/bin/sonic3-air
	# copy game resource files
	cp -r $(@D)/Oxygen/sonic3air/data $(TARGET_DIR)/usr/bin/sonic3-air
	cp -r $(@D)/Oxygen/sonic3air/scripts $(TARGET_DIR)/usr/bin/sonic3-air
	cp -r $(@D)/Oxygen/sonic3air/saves $(TARGET_DIR)/usr/bin/sonic3-air
endef

$(eval $(cmake-package))
