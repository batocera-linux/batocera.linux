################################################################################
#
# EDUKE32
#
################################################################################
# Version.: Commits on Oct 16, 2021
EDUKE32_VERSION = b90417ed8e48a3bc6c115ffc92a813ace35b5cfc
EDUKE32_SITE = https://github.com/nukeykt/NBlood.git

EDUKE32_DEPENDENCIES = sdl2 sdl2_image
EDUKE32_SITE_METHOD=git
EDUKE32_LICENSE = GPLv3

ifeq ($(BR2_PACKAGE_BATOCERA_TARGET_X86_ANY),y)
EDUKE32_CONF_OPTS=USE_OPENGL=1 POLYMER=1
else
EDUKE32_CONF_OPTS=USE_OPENGL=0 POLYMER=1 RPI4=1
endif

define EDUKE32_BUILD_CMDS
		$(TARGET_CONFIGURE_OPTS) $(MAKE) \
		CPP="$(TARGET_CPP)" CXX="$(TARGET_CXX)" CC="$(TARGET_CC)" \
		AS="$(TARGET_CC)" LD="$(TARGET_LD)" STRIP="$(TARGET_STRIP)" \
		-C $(@D) -f GNUmakefile HAVE_GTK2=0 $(EDUKE32_CONF_OPTS)
endef

define EDUKE32_INSTALL_TARGET_CMDS
	$(INSTALL) -m 0755 $(@D)/eduke32 -D $(TARGET_DIR)/usr/bin/eduke32
	$(INSTALL) -m 0755 $(@D)/nblood -D $(TARGET_DIR)/usr/bin/nblood
	$(INSTALL) -m 0755 $(@D)/pcexhumed -D $(TARGET_DIR)/usr/bin/pcexhumed
	$(INSTALL) -m 0755 $(@D)/etekwar -D $(TARGET_DIR)/usr/bin/etekwar
	$(INSTALL) -m 0755 $(@D)/rednukem -D $(TARGET_DIR)/usr/bin/rednukem
	$(INSTALL) -m 0755 $(@D)/voidsw -D $(TARGET_DIR)/usr/bin/voidsw

	#copy settings
	mkdir -p $(TARGET_DIR)/usr/share/batocera/datainit/system/.config/eduke32
    cp $(BR2_EXTERNAL_BATOCERA_PATH)/package/batocera/ports/eduke32/eduke32.cfg $(TARGET_DIR)/usr/share/batocera/datainit/system/.config/eduke32
    cp $(BR2_EXTERNAL_BATOCERA_PATH)/package/batocera/ports/eduke32/settings.cfg $(TARGET_DIR)/usr/share/batocera/datainit/system/.config/eduke32

	#copy sdl game contoller info
	cp $(@D)/package/common/gamecontrollerdb.txt $(TARGET_DIR)/usr/share/gamecontrollerdb.txt

	# evmap config
	mkdir -p $(TARGET_DIR)/usr/share/evmapy
	cp $(BR2_EXTERNAL_BATOCERA_PATH)/package/batocera/ports/eduke32/eduke32.keys $(TARGET_DIR)/usr/share/evmapy/eduke32.keys
	cp $(BR2_EXTERNAL_BATOCERA_PATH)/package/batocera/ports/eduke32/nblood.keys $(TARGET_DIR)/usr/share/evmapy/nblood.keys
	cp $(BR2_EXTERNAL_BATOCERA_PATH)/package/batocera/ports/eduke32/pcexhumed.keys $(TARGET_DIR)/usr/share/evmapy/pcexhumed.keys
	cp $(BR2_EXTERNAL_BATOCERA_PATH)/package/batocera/ports/eduke32/eduke32.keys $(TARGET_DIR)/usr/share/evmapy/etekwar.keys
	cp $(BR2_EXTERNAL_BATOCERA_PATH)/package/batocera/ports/eduke32/eduke32.keys $(TARGET_DIR)/usr/share/evmapy/rednukem.keys
	cp $(BR2_EXTERNAL_BATOCERA_PATH)/package/batocera/ports/eduke32/voidsw.keys $(TARGET_DIR)/usr/share/evmapy/voidsw.keys
endef

$(eval $(generic-package))
