################################################################################
#
# drastic
#
################################################################################

DRASTIC_VERSION = 1.0
DRASTIC_SOURCE = drastic.tar.gz
DRASTIC_SITE = https://github.com/liberodark/drastic/releases/download/$(DRASTIC_VERSION)

define DRASTIC_EXTRACT_CMDS
	mkdir -p $(@D)/target && cd $(@D)/target && tar xf $(DL_DIR)/$(DRASTIC_DL_SUBDIR)/$(DRASTIC_SOURCE)
endef

ifeq ($(BR2_PACKAGE_BATOCERA_TARGET_RPI4)$(BR2_PACKAGE_BATOCERA_TARGET_S922X),y)
DRASTIC_BINARYFILE=drastic_n2
else ifeq ($(BR2_PACKAGE_BATOCERA_TARGET_ODROIDGOA),y)
DRASTIC_BINARYFILE=drastic_oga
endif

define DRASTIC_INSTALL_TARGET_CMDS
	mkdir -p $(TARGET_DIR)/usr/share/
	mkdir -p $(TARGET_DIR)/usr/share/evmapy

	install -m 0755 $(@D)/target/$(DRASTIC_BINARYFILE) $(TARGET_DIR)/usr/bin/drastic
	cp -pr $(@D)/target/drastic $(TARGET_DIR)/usr/share/drastic

	# evmap config
	mkdir -p $(TARGET_DIR)/usr/share/evmapy
	cp $(BR2_EXTERNAL_BATOCERA_PATH)/package/batocera/emulators/drastic/nds.drastic.keys $(TARGET_DIR)/usr/share/evmapy
endef

$(eval $(generic-package))
