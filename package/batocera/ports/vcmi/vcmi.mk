################################################################################
#
# VCMI
#
################################################################################

VCMI_VERSION = 1.3.1
VCMI_SITE = https://github.com/vcmi/vcmi.git
VCMI_SITE_METHOD=git
VCMI_GIT_SUBMODULES=YES
VCMI_DEPENDENCIES = sdl2 sdl2_image sdl2_mixer sdl2_ttf ffmpeg tbb boost

VCMI_CONF_OPTS += -DENABLE_TEST=OFF -DENABLE_MONOLITHIC_INSTALL=ON -DCMAKE_INSTALL_PREFIX="/usr/vcmi/" -DQT_VERSION_MAJOR=6

# Launcher requires Qt
ifeq ($(BR2_PACKAGE_QT6),)
VCMI_CONF_OPTS += -DENABLE_LAUNCHER=OFF -DENABLE_EDITOR=OFF
else
VCMI_DEPENDENCIES += qt6base qt6tools
ifeq ($(BR2_PACKAGE_QT6WAYLAND),y)
VCMI_DEPENDENCIES += qt6wayland
endif
endif

# Install into proper prefix
VCMI_INSTALL_TARGET_OPTS = DESTDIR="$(TARGET_DIR)" install


$(eval $(cmake-package))
