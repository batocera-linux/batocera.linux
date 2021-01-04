################################################################################
#
# redream
#
################################################################################

REDREAM_VERSION = 1.5.0-580-gd567665
REDREAM_SOURCE = redream.x86_64-linux-v$(REDREAM_VERSION).tar.gz
REDREAM_SITE = https://redream.io/download

define REDREAM_EXTRACT_CMDS
	mkdir -p $(@D)/target && cd $(@D)/target && tar xf $(DL_DIR)/$(REDREAM_DL_SUBDIR)/$(REDREAM_SOURCE)
endef

define REDREAM_INSTALL_TARGET_CMDS
	# redream
	mkdir -p $(TARGET_DIR)/usr/share/redream
	cp -pr $(@D)/target/redream $(TARGET_DIR)/usr/share/redream
	ln -sf $(TARGET_DIR)/usr/share/redream/redream $(TARGET_DIR)/usr/bin/redream

	# key
	mkdir -p $(TARGET_DIR)/userdata/system/configs/redream
	touch $(TARGET_DIR)/userdata/system/configs/redream/redream.key
	ln -sf $(TARGET_DIR)/userdata/system/configs/redream/redream.key $(TARGET_DIR)/usr/share/redream/redream.key

	# config
	ln -sf $(TARGET_DIR)/userdata/system/configs/redream/redream.cfg $(TARGET_DIR)/usr/share/redream/redream.cfg

	# cache
	mkdir -p $(TARGET_DIR)/userdata/saves/dreamcast/redream/cache
	ln -sf $(TARGET_DIR)/userdata/saves/dreamcast/redream/cache $(TARGET_DIR)/usr/share/redream/cache

	# saves
	touch $(TARGET_DIR)/userdata/saves/dreamcast/redream/flash.bin
	touch $(TARGET_DIR)/userdata/saves/dreamcast/redream/vmu0.bin
	touch $(TARGET_DIR)/userdata/saves/dreamcast/redream/vmu1.bin
	touch $(TARGET_DIR)/userdata/saves/dreamcast/redream/vmu2.bin
	touch $(TARGET_DIR)/userdata/saves/dreamcast/redream/vmu3.bin
	ln -sf $(TARGET_DIR)/userdata/saves/dreamcast/redream/flash.bin $(TARGET_DIR)/usr/share/redream/flash.bin
	ln -sf $(TARGET_DIR)/userdata/saves/dreamcast/redream/vmu0.bin $(TARGET_DIR)/usr/share/redream/vmu0.bin
	ln -sf $(TARGET_DIR)/userdata/saves/dreamcast/redream/vmu1.bin $(TARGET_DIR)/usr/share/redream/vmu1.bin
	ln -sf $(TARGET_DIR)/userdata/saves/dreamcast/redream/vmu2.bin $(TARGET_DIR)/usr/share/redream/vmu2.bin
	ln -sf $(TARGET_DIR)/userdata/saves/dreamcast/redream/vmu3.bin $(TARGET_DIR)/usr/share/redream/vmu3.bin

	# logs
	touch $(TARGET_DIR)/userdata/system/logs/redream.log
	ln -sf $(TARGET_DIR)/userdata/system/logs/redream.log $(TARGET_DIR)/usr/share/redream/redream.log

	# evmap config
	mkdir -p $(TARGET_DIR)/usr/share/evmapy
	cp -prn $(BR2_EXTERNAL_BATOCERA_PATH)/package/batocera/emulators/redream/redream.keys $(TARGET_DIR)/usr/share/evmapy
endef

$(eval $(generic-package))
