################################################################################
#
# NanoBoyAdvance
#
################################################################################

NBA_VERSION = v1.4
NBA_SITE = https://github.com/nba-emu/NanoBoyAdvance.git
NBA_SITE_METHOD = git
NBA_GIT_SUBMODULES = YES
NBA_LICENSE = GPL v3
NBA_DEPENDENCIES = sdl2 libglew

NBA_CONF_OPTS += -DCMAKE_BUILD_TYPE=Release
NBA_CONF_OPTS += -DBUILD_SHARED_LIBS=ON
NBA_CONF_OPTS += -DBUILD_TESTS=OFF

define NBA_INSTALL_TARGET_CMDS
	mkdir -p $(TARGET_DIR)/usr/nba
	mkdir -p $(TARGET_DIR)/usr/lib

	$(INSTALL) -D $(@D)/bin/sdl/NanoBoyAdvance \
		$(TARGET_DIR)/usr/nba/NanoBoyAdvance
	$(INSTALL) -D $(@D)/external/fmtlib/libfmt.so.6.1.3 \
		$(TARGET_DIR)/usr/lib/libfmt.so.6.1.3

	cp -pr $(@D)/external/fmtlib/libfmt.so.6 $(TARGET_DIR)/usr/lib/
	cp -pr $(@D)/bin/sdl/shader $(TARGET_DIR)/usr/nba/
	cp -pr $(@D)/bin/sdl/*.toml $(TARGET_DIR)/usr/nba/

	# evmap config
	mkdir -p $(TARGET_DIR)/usr/share/evmapy
	cp $(BR2_EXTERNAL_BATOCERA_PATH)/package/batocera/emulators/nba/gba.nba.keys $(TARGET_DIR)/usr/share/evmapy
endef

$(eval $(cmake-package))
