################################################################################
#
# OPENJAZZ
#
################################################################################
# Version.: Commits on Feb 18, 2024
OPENJAZZ_VERSION = 71eb6e50adf0b4e6c7fcb426791bd3e72eae5a2b
OPENJAZZ_SITE =  $(call github,AlisterT,openjazz,$(OPENJAZZ_VERSION))
OPENJAZZ_DEPENDENCIES = sdl2
OPENJAZZ_LICENSE = GPLv2

#define OPENJAZZ_BUILD_CMDS
#		$(TARGET_CONFIGURE_OPTS) $(MAKE) \
#		CPP="$(TARGET_CPP)" CXX="$(TARGET_CXX)" CC="$(TARGET_CC)" \
#		AS="$(TARGET_CC)" LD="$(TARGET_LD)" STRIP="$(TARGET_STRIP)" \
#		-C $(@D) -f Makefile
#endef

define OPENJAZZ_INSTALL_TARGET_CMDS
	$(INSTALL) -D -m 0755 $(@D)/OpenJazz $(TARGET_DIR)/usr/bin/OpenJazz
endef

define OPENJAZZ_POST_PROCESS
	mkdir -p $(TARGET_DIR)/usr/share/evmapy
	cp $(BR2_EXTERNAL_BATOCERA_PATH)/package/batocera/ports/openjazz/openjazz.keys $(TARGET_DIR)/usr/share/evmapy
	cp $(BR2_EXTERNAL_BATOCERA_PATH)/package/batocera/ports/openjazz/openjazz.cfg $(TARGET_DIR)/usr/share/batocera/datainit/system/configs/openjazz.cfg
endef

$(eval $(cmake-package))

