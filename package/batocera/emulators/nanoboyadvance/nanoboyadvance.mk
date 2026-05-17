################################################################################
#
# nanoboyadvance
#
################################################################################

NANOBOYADVANCE_VERSION = v1.8.3
NANOBOYADVANCE_SITE = https://github.com/nba-emu/NanoBoyAdvance.git
NANOBOYADVANCE_SITE_METHOD = git
NANOBOYADVANCE_LICENSE = GPL-3.0
NANOBOYADVANCE_LICENSE_FILE = LICENSE
NANOBOYADVANCE_EMULATOR_INFO = nanoboyadvance.emulator.yml

NANOBOYADVANCE_DEPENDENCIES = sdl2 qt6base

NANOBOYADVANCE_CONF_OPTS += -DCMAKE_BUILD_TYPE=Release
NANOBOYADVANCE_CONF_OPTS += -DBUILD_SHARED_LIBS=OFF
NANOBOYADVANCE_CONF_OPTS += -DPLATFORM_QT=ON

ifeq ($(BR2_PACKAGE_XSERVER_XORG_SERVER),y)
    NANOBOYADVANCE_DEPENDENCIES += libglu
    NANOBOYADVANCE_CONF_OPTS += -DOpenGL_GL_PREFERENCE=GLVND
endif

ifeq ($(BR2_PACKAGE_WAYLAND),y)
    NANOBOYADVANCE_DEPENDENCIES += qt6wayland
endif

define NANOBOYADVANCE_EVMAPY
	mkdir -p $(TARGET_DIR)/usr/share/evmapy
	cp $(BR2_EXTERNAL_BATOCERA_PATH)/package/batocera/emulators/nanoboyadvance/*.keys \
	    $(TARGET_DIR)/usr/share/evmapy
endef

NANOBOYADVANCE_POST_INSTALL_TARGET_HOOKS += NANOBOYADVANCE_EVMAPY

$(eval $(cmake-package))
$(eval $(emulator-info-package))
