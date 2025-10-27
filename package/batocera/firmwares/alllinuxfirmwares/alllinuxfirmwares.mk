################################################################################
#
# alllinuxfirmwares
#
################################################################################

ALLLINUXFIRMWARES_VERSION = 20251021
ALLLINUXFIRMWARES_SOURCE = linux-firmware-$(ALLLINUXFIRMWARES_VERSION).tar.gz
ALLLINUXFIRMWARES_SITE = https://www.kernel.org/pub/linux/kernel/firmware

ifeq ($(BR2_PACKAGE_FIRMWARE_ARMBIAN),y)
ALLLINUXFIRMWARES_DEPENDENCIES += firmware-armbian
endif

ifeq ($(BR2_PACKAGE_FIRMWARE_ORANGEPI),y)
ALLLINUXFIRMWARES_DEPENDENCIES += firmware-orangepi
endif

# exclude some dirs not required on batocera
ALLLINUXFIRMWARES_REMOVE_DIRS = $(@D)/liquidio $(@D)/netronome $(@D)/mellanox \
    $(@D)/dpaa2 $(@D)/bnx2x $(@D)/cxgb4 $(@D)/mrvl/prestera

ifeq ($(BR2_arm)$(BR2_aarch64),y)
    # rk3588 boards can allow for more varied pcie combo adapters
    ifeq ($(BR2_PACKAGE_BATOCERA_TARGET_RK3588)$(BR2_PACKAGE_BATOCERA_TARGET_RK3588_SDIO),y)
        ALLLINUXFIRMWARES_REMOVE_DIRS += $(@D)/amd $(@D)/amdgpu $(@D)/amdnpu $(@D)/intel/avs \
            $(@D)/intel/catpt $(@D)/intel/ice $(@D)/intel/ipu $(@D)/intel/ish $(@D)/intel/vsc \
            $(@D)/i915 $(@D)/nvidia $(@D)/radeon $(@D)/s5p-* $(@D)/qat_* $(@D)/ql2*
    else
        ALLLINUXFIRMWARES_REMOVE_DIRS += $(@D)/amd $(@D)/amdgpu $(@D)/amdnpu $(@D)/intel \
            $(@D)/i915 $(@D)/nvidia $(@D)/radeon $(@D)/s5p-* $(@D)/qat_* $(@D)/ql2*
    endif
endif

ifeq ($(BR2_PACKAGE_BRCMFMAC_SDIO_FIRMWARE_RPI)$(BR2_PACKAGE_EXTRALINUXFIRMWARES),y)
    ALLLINUXFIRMWARES_REMOVE_DIRS += $(@D)/brcm
endif

# Remove qualcomm firmware if not buidling Qualcomm Board
ifneq ($(BR2_PACKAGE_BATOCERA_TARGET_ODIN)$(BR2_PACKAGE_BATOCERA_TARGET_SM8250)$(BR2_PACKAGE_BATOCERA_TARGET_SM8550),y)
    ALLLINUXFIRMWARES_REMOVE_DIRS += $(@D)/qcom
endif

# Remove amlogic firmware if not building an Amlogic board
ifneq ($(BR2_PACKAGE_BATOCERA_TARGET_AMLOGIC_ANY),y)
    ALLLINUXFIRMWARES_REMOVE_DIRS += $(@D)/amlogic
endif

# Remove non-x86 specific firmware if building x86
ifeq ($(BR2_PACKAGE_BATOCERA_TARGET_X86_64_ANY),y)
    ALLLINUXFIRMWARES_REMOVE_DIRS += $(@D)/arm $(@D)/imx $(@D)/sun $(@D)/ti-keystone $(@D)/sxg $(@D)/meson
endif

define ALLLINUXFIRMWARES_INSTALL_TARGET_CMDS
	mkdir -p $(TARGET_DIR)/lib/firmware

    # exclude some dirs not required on batocera
    rm -rf $(ALLLINUXFIRMWARES_REMOVE_DIRS)

    if [ "$BR2_PACKAGE_BATOCERA_TARGET_RK3588" = "y" ] || [ "$BR2_PACKAGE_BATOCERA_TARGET_RK3588_SDIO" = "y" ]; then \
        find $(@D)/intel -type f ! -name 'ibt-*' -delete; \
    fi

    # -n is mandatory while some other packages provides firmwares too
    # this is not ideal, but i don't know how to tell to buildroot to install this package first
    # (and not worry about all packages installing firmwares)
    rsync -au --checksum $(@D)/ $(TARGET_DIR)/lib/firmware/

    # Some firmware are distributed as a symlink, for drivers to load them using a
    # defined name other than the real one. Since 9cfefbd7fbda ("Remove duplicate
    # symlinks") those symlink aren't distributed in linux-firmware but are created
    # automatically by its copy-firmware.sh script during the installation, which
    # parses the WHENCE file where symlinks are described. We follow the same logic
    # here, adding symlink only for firmwares installed in the target directory.
    cd $(TARGET_DIR)/lib/firmware ; \
        sed -r -e '/^Link: (.+) -> (.+)$$/!d; s//\1 \2/' $(@D)/WHENCE | \
        while read -r f d; do \
            if test -f "$$(readlink -m "$$(dirname "$$f")/$${d}")"; then \
                mkdir -p "$$(dirname "$$f")" && \
                ln -sf "$$d" "$$f" || exit 1; \
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
endef

# symlink AMD GPU firmware for 890M devices
define ALLLINUXFIRMWARES_FIX_AMD_890M
    ln -sf /lib/firmware/amdgpu/isp_4_1_1.bin \
        $(TARGET_DIR)/lib/firmware/amdgpu/isp_4_1_0.bin
endef

# symlink Bee-Link SER9 for a BIOS / firmware bug
define ALLLINUXFIRMWARES_FIX_SER9
    mkdir -p $(TARGET_DIR)/usr/share/batocera/firmware
    mkdir -p $(TARGET_DIR)/etc/init.d
    cp -f $(BR2_EXTERNAL_BATOCERA_PATH)/package/batocera/firmwares/alllinuxfirmwares/dcn_3_5_dmcub.bin \
        $(TARGET_DIR)/usr/share/batocera/firmware/dcn_3_5_dmcub.bin
    $(INSTALL) -m 0755 -D $(BR2_EXTERNAL_BATOCERA_PATH)/package/batocera/firmwares/alllinuxfirmwares/S03firmware \
        $(TARGET_DIR)/etc/init.d/
endef

# Copy Qualcomm firmware for Steam Deck OLED etc
ifeq ($(BR2_x86_64),y)
    ALLLINUXFIRMWARES_POST_INSTALL_TARGET_HOOKS = ALLLINUXFIRMWARES_LINK_QCA_WIFI_BT
    ALLLINUXFIRMWARES_POST_INSTALL_TARGET_HOOKS += ALLLINUXFIRMWARES_FIX_AMD_890M
    ALLLINUXFIRMWARES_POST_INSTALL_TARGET_HOOKS += ALLLINUXFIRMWARES_FIX_SER9
endif

# symlink BT firmware for RK3588 kernel
define ALLLINUXFIRMWARES_LINK_RTL_BT
    ln -sf /lib/firmware/rtl_bt/rtl8852bu_fw.bin \
        $(TARGET_DIR)/lib/firmware/rtl8852bu_fw
    ln -sf /lib/firmware/rtl_bt/rtl8852bu_config.bin \
        $(TARGET_DIR)/lib/firmware/rtl8852bu_config
endef

ifeq ($(BR2_PACKAGE_BATOCERA_TARGET_RK3588)$(BR2_PACKAGE_BATOCERA_TARGET_RK3588_SDIO),y)
    ALLLINUXFIRMWARES_POST_INSTALL_TARGET_HOOKS = ALLLINUXFIRMWARES_LINK_RTL_BT
endif

$(eval $(generic-package))
