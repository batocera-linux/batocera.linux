################################################################################
#
# solarus-engine
#
################################################################################

SOLARUS_ENGINE_VERSION = v2.0.4
SOLARUS_ENGINE_SITE = https://gitlab.com/solarus-games/solarus
SOLARUS_ENGINE_SITE_METHOD=git
SOLARUS_ENGINE_EMULATOR_INFO = solarus.emulator.yml
SOLARUS_ENGINE_LICENSE = GPL-3.0 (code), CC-BY-SA-4.0 (Solarus logos and icons), \
	CC-BY-SA-3.0 (GUI icons)
SOLARUS_ENGINE_LICENSE_FILES = license.txt
# Install libsolarus.so
SOLARUS_ENGINE_INSTALL_STAGING = YES

SOLARUS_ENGINE_DEPENDENCIES += batocera-luajit glm libmodplug libogg libvorbis
SOLARUS_ENGINE_DEPENDENCIES += openal physfs sdl2 sdl2_image sdl2_ttf

ifeq ($(BR2_PACKAGE_HAS_LIBGLES),y)
SOLARUS_ENGINE_DEPENDENCIES += libgles
SOLARUS_ENGINE_CONF_OPTS += -DSOLARUS_GL_ES=ON
endif

SOLARUS_ENGINE_CONF_OPTS += -DSOLARUS_BASE_WRITE_DIR=/userdata/saves
SOLARUS_ENGINE_CONF_OPTS += -DSOLARUS_WRITE_DIR=solarus
SOLARUS_ENGINE_CONF_OPTS += -DSOLARUS_USE_LUAJIT=ON
SOLARUS_ENGINE_CONF_OPTS += -DSOLARUS_TESTS=OFF

define SOLARUS_ENGINE_INSTALL_TARGET_CMDS
    $(INSTALL) -D $(@D)/cli/solarus-run $(TARGET_DIR)/usr/bin/
    cp -af $(@D)/libsolarus.so* $(TARGET_DIR)/usr/lib/
	mkdir -p $(TARGET_DIR)/usr/share/evmapy
	cp -f $(SOLARUS_ENGINE_PKGDIR)/solarus.keys $(TARGET_DIR)/usr/share/evmapy/
endef

$(eval $(cmake-package))
$(eval $(emulator-info-package))
