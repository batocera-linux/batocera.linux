################################################################################
#
# IONFURY
#
################################################################################
# Version.: Commits on Sep 04, 2021
IONFURY_VERSION = 25afea98fc9faac2a2f2adb032a4ec2407b5498b
IONFURY_SITE = https://voidpoint.io/terminx/eduke32.git
IONFURY_SITE_METHOD = git
IONFURY_LICENSE = GPLv2
IONFURY_DEPENDENCIES = sdl2 boost

ifeq ($(BR2_PACKAGE_BATOCERA_TARGET_X86_ANY),y)
IONFURY_CONF_OPTS=USE_OPENGL=1
else
IONFURY_CONF_OPTS=USE_OPENGL=0 RPI4=1
endif

define IONFURY_BUILD_CMDS
		$(TARGET_CONFIGURE_OPTS) $(MAKE) \
		CPP="$(TARGET_CPP)" CXX="$(TARGET_CXX)" CC="$(TARGET_CC)" \
		AS="$(TARGET_CC)" LD="$(TARGET_LD)" STRIP="$(TARGET_STRIP)" \
		-C $(@D) -f GNUmakefile HAVE_GTK2=0 FURY=1 $(IONFURY_CONF_OPTS)
endef

define IONFURY_INSTALL_TARGET_CMDS
	$(INSTALL) -m 0755 $(@D)/fury -D $(TARGET_DIR)/usr/bin/ionfury

	#copy settings
    mkdir -p $(TARGET_DIR)/usr/share/batocera/datainit/system/.config/fury
    cp $(BR2_EXTERNAL_BATOCERA_PATH)/package/batocera/ports/ionfury/ionfury.cfg $(TARGET_DIR)/usr/share/batocera/datainit/system/.config/fury
    cp $(BR2_EXTERNAL_BATOCERA_PATH)/package/batocera/ports/ionfury/settings.cfg $(TARGET_DIR)/usr/share/batocera/datainit/system/.config/fury

	#copy sdl game contoller info
	cp $(@D)/package/common/gamecontrollerdb.txt $(TARGET_DIR)/usr/share/gamecontrollerdb.txt

	# evmap config
	mkdir -p $(TARGET_DIR)/usr/share/evmapy
	cp $(BR2_EXTERNAL_BATOCERA_PATH)/package/batocera/ports/ionfury/ionfury.keys $(TARGET_DIR)/usr/share/evmapy
endef

$(eval $(generic-package))
