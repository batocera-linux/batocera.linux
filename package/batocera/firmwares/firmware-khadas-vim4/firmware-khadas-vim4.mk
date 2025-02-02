################################################################################
#
# firmware-khadas-vim4
#
################################################################################

FIRMWARE_KHADAS_VIM4_VERSION = 1.7.3
FIRMWARE_KHADAS_VIM4_SITE = https://dl.khadas.com/repos/vim4/pool/main/l/linux-board-package-noble-vim4
FIRMWARE_KHADAS_VIM4_SOURCE = linux-board-package-noble-vim4_$(FIRMWARE_KHADAS_VIM4_VERSION)_arm64.deb
FIRMWARE_KHADAS_VIM4_FIRMWARE_DIR = $(TARGET_DIR)/lib/firmware

FIRMWARE_KHADAS_VIM4_OPTEE_USR_SRC = optee-userspace_0.6-202406_arm64.deb
FIRMWARE_KHADAS_VIM4_OPTEE_VFW_SRC = optee-video-firmware_0.5-202406_arm64.deb
FIRMWARE_KHADAS_VIM4_OPTEE_USR_PATH = optee-userspace
FIRMWARE_KHADAS_VIM4_OPTEE_VFW_PATH = optee-video-firmware

FIRMWARE_KHADAS_VIM4_EXTRA_DOWNLOADS = \
 https://dl.khadas.com/repos/vim4/pool/main/o/optee-userspace/$(FIRMWARE_KHADAS_VIM4_OPTEE_USR_SRC) \
 https://dl.khadas.com/repos/vim4/pool/main/o/optee-video-firmware/$(FIRMWARE_KHADAS_VIM4_OPTEE_VFW_SRC)

define FIRMWARE_KHADAS_VIM4_EXTRACT_CMDS
	# Extract Firmware
	$(AR) --output=$(@D) -x $(FIRMWARE_KHADAS_VIM4_DL_DIR)/$(FIRMWARE_KHADAS_VIM4_SOURCE)
	$(TAR) xf $(@D)/data.tar.xz -C $(@D)
	# Extract Optee Userspace
	mkdir -p $(@D)/$(FIRMWARE_KHADAS_VIM4_OPTEE_USR_PATH)
	$(AR) --output=$(@D)/$(FIRMWARE_KHADAS_VIM4_OPTEE_USR_PATH) -x $(FIRMWARE_KHADAS_VIM4_DL_DIR)/$(FIRMWARE_KHADAS_VIM4_OPTEE_USR_SRC)
	$(TAR) xf $(@D)/$(FIRMWARE_KHADAS_VIM4_OPTEE_USR_PATH)/data.tar.xz -C $(@D)/$(FIRMWARE_KHADAS_VIM4_OPTEE_USR_PATH)
	# Extract Optee Video Firmware
	mkdir -p $(@D)/$(FIRMWARE_KHADAS_VIM4_OPTEE_VFW_PATH)
	$(AR) --output=$(@D)/$(FIRMWARE_KHADAS_VIM4_OPTEE_VFW_PATH) -x $(FIRMWARE_KHADAS_VIM4_DL_DIR)/$(FIRMWARE_KHADAS_VIM4_OPTEE_VFW_SRC)
	$(TAR) xf $(@D)/$(FIRMWARE_KHADAS_VIM4_OPTEE_VFW_PATH)/data.tar.xz -C $(@D)/$(FIRMWARE_KHADAS_VIM4_OPTEE_VFW_PATH)
endef

define FIRMWARE_KHADAS_VIM4_BUILD_CMDS
	# Create links for hciattach
	cd $(@D)/lib/firmware/brcm ; ln -sf BCM43438A1.hcd BCM43430A1.hcd ; ln -sf BCM4356A2.hcd BCM4354A2.hcd
endef

define FIRMWARE_KHADAS_VIM4_INSTALL_TARGET_CMDS
	mkdir -p $(TARGET_DIR)/lib/firmware/
	cp -R $(BR2_EXTERNAL_BATOCERA_PATH)/package/batocera/firmwares/firmware-khadas-vim4/firmware/* $(FIRMWARE_KHADAS_VIM4_FIRMWARE_DIR)/
	cp -R $(@D)/lib/firmware/* $(FIRMWARE_KHADAS_VIM4_FIRMWARE_DIR)/
	mkdir -p $(TARGET_DIR)/usr/bin/
	mkdir -p $(TARGET_DIR)/usr/lib/
	# Install Optee Userspace
	cp -R $(@D)/$(FIRMWARE_KHADAS_VIM4_OPTEE_USR_PATH)/usr/bin/* $(TARGET_DIR)/usr/bin/
	cp -R $(@D)/$(FIRMWARE_KHADAS_VIM4_OPTEE_USR_PATH)/usr/lib/* $(TARGET_DIR)/usr/lib/
	# Install Optee Video Firmware
	cp -R $(@D)/$(FIRMWARE_KHADAS_VIM4_OPTEE_VFW_PATH)/usr/bin/* $(TARGET_DIR)/usr/bin/
	cp -R $(@D)/$(FIRMWARE_KHADAS_VIM4_OPTEE_VFW_PATH)/usr/lib/* $(TARGET_DIR)/usr/lib/
	cp -R $(@D)/$(FIRMWARE_KHADAS_VIM4_OPTEE_VFW_PATH)/lib/optee_armtz $(TARGET_DIR)/lib/
	cp -P $(@D)/$(FIRMWARE_KHADAS_VIM4_OPTEE_VFW_PATH)/lib/teetz $(TARGET_DIR)/lib/
endef

$(eval $(generic-package))
