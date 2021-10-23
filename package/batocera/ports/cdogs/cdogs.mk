################################################################################
#
# C-Dogs
#
################################################################################
# Version.: Commits on Oct 12, 2021
CDOGS_VERSION = 33872a66b18e3cb51826419f3593dfea5cffc6f4
CDOGS_SITE = $(call github,cxong,cdogs-sdl,$(CDOGS_VERSION))

CDOGS_DEPENDENCIES = sdl2 python-protobuf
CDOGS_LICENSE = GPL-2.0

CDOGS_SUPPORTS_IN_SOURCE_BUILD = NO

CDOGS_CONF_OPTS += -DCMAKE_BUILD_TYPE=Release
CDOGS_CONF_OPTS += -DCDOGS_DATA_DIR=/userdata/roms/cdogs/
CDOGS_CONF_OPTS += -DBUILD_EDITOR=OFF

define CDOGS_INSTALL_TARGET_CMDS
    $(INSTALL) -D $(@D)/buildroot-build/src/cdogs-sdl $(TARGET_DIR)/usr/bin/cdogs
    mkdir -p $(TARGET_DIR)/usr/share/batocera/datainit/roms/cdogs
    cp -pav $(@D)/data $(TARGET_DIR)/usr/share/batocera/datainit/roms/cdogs
    cp -pav $(@D)/doc $(TARGET_DIR)/usr/share/batocera/datainit/roms/cdogs
    cp -pav $(@D)/dogfights $(TARGET_DIR)/usr/share/batocera/datainit/roms/cdogs
    cp -pav $(@D)/graphics $(TARGET_DIR)/usr/share/batocera/datainit/roms/cdogs
    cp -pav $(@D)/missions $(TARGET_DIR)/usr/share/batocera/datainit/roms/cdogs
    cp -pav $(@D)/music $(TARGET_DIR)/usr/share/batocera/datainit/roms/cdogs
    cp -pav $(@D)/sounds $(TARGET_DIR)/usr/share/batocera/datainit/roms/cdogs
    cp -f $(BR2_EXTERNAL_BATOCERA_PATH)/package/batocera/ports/cdogs/gamecontrollerdb.txt $(TARGET_DIR)/usr/share/batocera/datainit/roms/cdogs/data

    # evmap config
	mkdir -p $(TARGET_DIR)/usr/share/evmapy
	cp $(BR2_EXTERNAL_BATOCERA_PATH)/package/batocera/ports/cdogs/cdogs.keys $(TARGET_DIR)/usr/share/evmapy
endef

$(eval $(cmake-package))
