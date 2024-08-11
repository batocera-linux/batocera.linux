################################################################################
#
# alllinuxfirmwares
#
################################################################################

ALLLINUXFIRMWARES_VERSION = 20240811
ALLLINUXFIRMWARES_SOURCE = linux-firmware-$(ALLLINUXFIRMWARES_VERSION).tar.gz
ALLLINUXFIRMWARES_SITE = https://git.kernel.org/pub/scm/linux/kernel/git/firmware/linux-firmware.git/snapshot

# exclude some dirs not required on batocera
ALLLINUXFIRMWARES_REMOVE_DIRS = $(@D)/liquidio $(@D)/netronome $(@D)/mellanox $(@D)/dpaa2 $(@D)/bnx2x $(@D)/cxgb4 $(@D)/mrvl/prestera

ifeq ($(BR2_arm)$(BR2_aarch64),y)
    ALLLINUXFIRMWARES_REMOVE_DIRS += $(@D)/amd $(@D)/amdgpu $(@D)/intel $(@D)/i915 $(@D)/nvidia $(@D)/radeon $(@D)/s5p-* $(@D)/qat_* $(@D)/ql2*
endif

ifeq ($(BR2_PACKAGE_BRCMFMAC_SDIO_FIRMWARE_RPI)$(BR2_PACKAGE_EXTRALINUXFIRMWARES),y)
    ALLLINUXFIRMWARES_REMOVE_DIRS += $(@D)/brcm
endif

# Remove qualcomm firmware if not buidling Ayn ODIN
ifneq ($(BR2_PACKAGE_BATOCERA_TARGET_ODIN),y)
    ALLLINUXFIRMWARES_REMOVE_DIRS += $(@D)/qcom
endif

define ALLLINUXFIRMWARES_INSTALL_TARGET_CMDS
	mkdir -p $(TARGET_DIR)/lib/firmware

    # exclude some dirs not required on batocera
    rm -rf $(ALLLINUXFIRMWARES_REMOVE_DIRS)

    # -n is mandatory while some other packages provides firmwares too
    # this is not ideal, but i don't know how to tell to buildroot to install this package first (and not worry about all packages installing firmwares)
    cp --remove-destination -prn $(@D)/* $(TARGET_DIR)/lib/firmware/

    # Some firmware are distributed as a symlink, for drivers to load them using a
    # defined name other than the real one. Since 9cfefbd7fbda ("Remove duplicate
    # symlinks") those symlink aren't distributed in linux-firmware but are created
    # automatically by its copy-firmware.sh script during the installation, which
    # parses the WHENCE file where symlinks are described. We follow the same logic
    # here, adding symlink only for firmwares installed in the target directory.
    cd $(TARGET_DIR)/lib/firmware ; \
    sed -r -e '/^Link: (.+) -> (.+)$$/!d; s//\1 \2/' $(@D)/WHENCE | \
	while read f d; do \
		if test -f $$(readlink -m $$(dirname "$$f")/$$d); then \
            if test -f $(TARGET_DIR)/lib/firmware/$$(dirname "$$f")/$$d; then \
                ln -sf $$d "$$f" || exit 1; \
            fi \
		fi ; \
	done
endef

define ALLLINUXFIRMWARES_LINK_QCA_WIFI_BT
    # wifi
    mkdir -p $(TARGET_DIR)/lib/firmware/ath11k/WCN6855/hw2.1
    mkdir -p $(TARGET_DIR)/lib/firmware/ath11k/QCA2066
    cp -rf $(BR2_EXTERNAL_BATOCERA_PATH)/package/batocera/firmwares/alllinuxfirmwares/hw2.1/* \
	    $(TARGET_DIR)/lib/firmware/ath11k/WCN6855/hw2.1
    cp -rf $(BR2_EXTERNAL_BATOCERA_PATH)/package/batocera/firmwares/alllinuxfirmwares/QCA206X/* \
	    $(TARGET_DIR)/lib/firmware/ath11k/QCA2066
    # bluetooth
    cp -rf $(BR2_EXTERNAL_BATOCERA_PATH)/package/batocera/firmwares/alllinuxfirmwares/qca/* \
	    $(TARGET_DIR)/lib/firmware/qca
endef

# Copy Qualcomm firmware for Steam Deck OLED
ifeq ($(BR2_x86_64),y)
    ALLLINUXFIRMWARES_POST_INSTALL_TARGET_HOOKS = ALLLINUXFIRMWARES_LINK_QCA_WIFI_BT
endif

# symlink BT firmware for RK3588 kernel
define ALLLINUXFIRMWARES_LINK_RTL_BT
    ln -sf /lib/firmware/rtl_bt/rtl8852bu_fw.bin \
        $(TARGET_DIR)/lib/firmware/rtl8852bu_fw
    ln -sf /lib/firmware/rtl_bt/rtl8852bu_config.bin \
        $(TARGET_DIR)/lib/firmware/rtl8852bu_config
endef

ifeq ($(BR2_PACKAGE_BATOCERA_TARGET_RK3588),y)
    ALLLINUXFIRMWARES_POST_INSTALL_TARGET_HOOKS = ALLLINUXFIRMWARES_LINK_RTL_BT
endif

$(eval $(generic-package))
