################################################################################
#
# alllinuxfirmwares
#
################################################################################

ALLLINUXFIRMWARES_VERSION = 20261019
ALLLINUXFIRMWARES_SOURCE = linux-firmware-$(ALLLINUXFIRMWARES_VERSION).tar.xz
ALLLINUXFIRMWARES_SITE = https://www.kernel.org/pub/linux/kernel/firmware

# the prunes below read the kernel config and the iwlwifi versions it loads
ifeq ($(BR2_LINUX_KERNEL),y)
ALLLINUXFIRMWARES_DEPENDENCIES += linux
endif

ifeq ($(BR2_PACKAGE_FIRMWARE_ARMBIAN),y)
ALLLINUXFIRMWARES_DEPENDENCIES += firmware-armbian
endif

ifeq ($(BR2_PACKAGE_FIRMWARE_ORANGEPI),y)
ALLLINUXFIRMWARES_DEPENDENCIES += firmware-orangepi
endif

# These folders contain massive blobs for 40Gb/100Gb SmartNICs and Mainframes.
# Removed to save significant space on all targets.
ALLLINUXFIRMWARES_REMOVE_DIRS = $(@D)/liquidio $(@D)/netronome $(@D)/mellanox \
    $(@D)/dpaa2 $(@D)/bnx2x $(@D)/cxgb4 $(@D)/mrvl/prestera $(@D)/qed \
    $(@D)/qlogic $(@D)/nfp $(@D)/pensando $(@D)/cavium \
    $(@D)/ath10k/WCN3990/hw1.0/shikra

# firmware for drivers the kernel doesn't build, as CONFIG_<option>:<path>
ALLLINUXFIRMWARES_KCONFIG_PRUNE = \
    IWLWIFI:intel/iwlwifi \
    DRM_AMDGPU:amdgpu \
    DRM_RADEON:radeon \
    ATH10K_SNOC:ath10k/WCN3990 \
    ATH10K_AHB:ath10k/QCA4019 \
    ATH11K_AHB:ath11k/IPQ* \
    ATH11K_AHB:ath11k/WCN6750 \
    ATH12K_AHB:ath12k/IPQ* \
    RTW89_8922D[A-Z]*:rtw89/rtw8922d*

# Remove strictly ARM/Mobile SoC components
ifeq ($(BR2_PACKAGE_BATOCERA_TARGET_X86_64_ANY),y)
    ALLLINUXFIRMWARES_REMOVE_DIRS += \
        $(@D)/airoha $(@D)/amlogic $(@D)/amphion $(@D)/apple \
        $(@D)/arm $(@D)/cadence $(@D)/cis $(@D)/cnm $(@D)/dsp56k $(@D)/imx \
        $(@D)/inside-secure $(@D)/ixp4xx $(@D)/meson $(@D)/microchip \
        $(@D)/nxp $(@D)/powervr $(@D)/qcom $(@D)/rockchip $(@D)/s5p-* \
        $(@D)/starfive $(@D)/sun $(@D)/sunxi $(@D)/sxg $(@D)/ti-keystone \
        $(@D)/v3d $(@D)/vc4 $(@D)/vicam
    # SoC wifi, cameras, NPU, server NICs and Instinct GPUs
    ALLLINUXFIRMWARES_REMOVE_DIRS += \
        $(@D)/ath10k/QCA4019 $(@D)/ath10k/WCN3990 $(@D)/ath11k/IPQ* \
        $(@D)/ath11k/WCN6750 $(@D)/ath12k/IPQ* $(@D)/mediatek/mt798* \
        $(@D)/ti-connectivity $(@D)/intel/ice $(@D)/intel/ipu \
        $(@D)/intel/qat $(@D)/intel/vpu $(@D)/intel/vsc \
        $(@D)/amdgpu/aldebaran_* $(@D)/amdgpu/arcturus_* \
        $(@D)/amdgpu/gc_9_4_[34]_* $(@D)/amdgpu/gc_9_5_0_* \
        $(@D)/amdgpu/psp_13_0_6_* $(@D)/amdgpu/psp_13_0_1[24]_* \
        $(@D)/amdgpu/sdma_4_4_[245].bin $(@D)/amdgpu/vcn_4_0_3.bin \
        $(@D)/amdgpu/vcn_5_0_1.bin $(@D)/nvidia/tegra*
    # nouveau only falls back to 535 when 570 is missing
    ALLLINUXFIRMWARES_REMOVE_DIRS += $(@D)/nvidia/*/gsp/*-535.113.01.bin
endif

# This removes strictly ARM/RISC-V SoC components while preserving all Wi-Fi/BT.
ifeq ($(BR2_arm)$(BR2_aarch64),y)
    ALLLINUXFIRMWARES_REMOVE_DIRS += \
        $(@D)/amd $(@D)/amdgpu $(@D)/amdnpu $(@D)/amdtee $(@D)/amd-ucode \
        $(@D)/i915 $(@D)/xe $(@D)/intel/avs $(@D)/intel/catpt $(@D)/intel/ice \
        $(@D)/intel/ipu $(@D)/intel/ish $(@D)/intel/vsc $(@D)/intel/sof* \
        $(@D)/HP $(@D)/LENOVO $(@D)/nvidia $(@D)/radeon \
        $(@D)/3com $(@D)/acenic $(@D)/adaptec $(@D)/advansys $(@D)/cis \
        $(@D)/dsp56k $(@D)/matrox $(@D)/yamaha
    
    # Prune other ARM SoC vendors if building a specific ARM target
    ifneq ($(BR2_PACKAGE_BATOCERA_TARGET_RK3562)$(BR2_PACKAGE_BATOCERA_TARGET_RK3588)$(BR2_PACKAGE_BATOCERA_TARGET_RK3588_SDIO)$(BR2_PACKAGE_BATOCERA_TARGET_RK3588_MAINLINE)$(BR2_PACKAGE_BATOCERA_TARGET_AMLOGIC_ANY),y)
         ALLLINUXFIRMWARES_REMOVE_DIRS += \
            $(@D)/rockchip $(@D)/amlogic $(@D)/meson $(@D)/sunxi \
            $(@D)/nxp $(@D)/imx $(@D)/starfive $(@D)/powervr \
            $(@D)/airoha $(@D)/amphion $(@D)/cadence $(@D)/ar3k
    endif
endif

# Remove Broadcom if RPi/External firmware is already handling it
ifeq ($(BR2_PACKAGE_BRCMFMAC_SDIO_FIRMWARE_RPI)$(BR2_PACKAGE_EXTRALINUXFIRMWARES),y)
    ALLLINUXFIRMWARES_REMOVE_DIRS += $(@D)/brcm
endif

# the rpi package ships these too, keep its newer firmware and matching clm_blob
ifeq ($(BR2_PACKAGE_BRCMFMAC_SDIO_FIRMWARE_RPI),y)
    ALLLINUXFIRMWARES_REMOVE_DIRS += $(@D)/cypress/cyfmac43430-sdio.* $(@D)/cypress/cyfmac43455-sdio.*
endif

# Remove snadragon SoC folder if not a Qualcomm board
# Preserves ath10k/11k/12k wifi separately
ifneq ($(BR2_PACKAGE_BATOCERA_TARGET_QUALCOMM_ANY),y)
    ALLLINUXFIRMWARES_REMOVE_DIRS += $(@D)/qcom
endif

# qcom folders the board device trees load from, video firmware is shared
ALLLINUXFIRMWARES_QCOM_KEEP = vpu vpu-* venus-*
ifeq ($(BR2_PACKAGE_BATOCERA_TARGET_QCS6490),y)
    ALLLINUXFIRMWARES_QCOM_KEEP += qcm6490 qcs6490
endif
ifeq ($(BR2_PACKAGE_BATOCERA_TARGET_SDM845),y)
    ALLLINUXFIRMWARES_QCOM_KEEP += sdm845
endif
ifeq ($(BR2_PACKAGE_BATOCERA_TARGET_SM4450),y)
    ALLLINUXFIRMWARES_QCOM_KEEP += sm4450
endif
ifeq ($(BR2_PACKAGE_BATOCERA_TARGET_SM6115),y)
    ALLLINUXFIRMWARES_QCOM_KEEP += sm6115 qrb4210
endif
ifeq ($(BR2_PACKAGE_BATOCERA_TARGET_SM8250),y)
    ALLLINUXFIRMWARES_QCOM_KEEP += sm8250
endif
ifeq ($(BR2_PACKAGE_BATOCERA_TARGET_SM8550),y)
    ALLLINUXFIRMWARES_QCOM_KEEP += sm8550
endif
ifeq ($(BR2_PACKAGE_BATOCERA_TARGET_SM8650),y)
    ALLLINUXFIRMWARES_QCOM_KEEP += sm8650
endif
ifeq ($(BR2_PACKAGE_BATOCERA_TARGET_SM8750),y)
    ALLLINUXFIRMWARES_QCOM_KEEP += sm8750
endif

# Irrelevant blobs for SM6115 & SM8250.
ifeq ($(BR2_PACKAGE_BATOCERA_TARGET_SM6115)$(BR2_PACKAGE_BATOCERA_TARGET_SM8250),y)
    ALLLINUXFIRMWARES_REMOVE_DIRS += $(@D)/intel $(@D)/mediatek
endif

# Remove amlogic firmware if not building an Amlogic board
ifneq ($(BR2_PACKAGE_BATOCERA_TARGET_AMLOGIC_ANY),y)
    ALLLINUXFIRMWARES_REMOVE_DIRS += $(@D)/amlogic
endif

define ALLLINUXFIRMWARES_INSTALL_TARGET_CMDS
	mkdir -p $(TARGET_DIR)/lib/firmware

    # Exclude defined directories
    rm -rf $(ALLLINUXFIRMWARES_REMOVE_DIRS)

    if [ -f $(LINUX_DIR)/.config ]; then \
        for p in $(ALLLINUXFIRMWARES_KCONFIG_PRUNE); do \
            grep -q "^CONFIG_$${p%%:*}=[ym]" $(LINUX_DIR)/.config || \
                rm -rf $(@D)/$${p#*:}; \
        done; \
    fi

    if [ -d $(@D)/qcom ]; then \
        find $(@D)/qcom -mindepth 1 -maxdepth 1 -type d \
            $(foreach d,$(ALLLINUXFIRMWARES_QCOM_KEEP),! -name '$(d)') \
            -exec rm -rf {} +; \
    fi

    # RK3588 specific: Keep only Bluetooth 'ibt-*' and iwlwifi from the Intel folder
    if [ "$(BR2_PACKAGE_BATOCERA_TARGET_RK3588)" = "y" ] || [ "$(BR2_PACKAGE_BATOCERA_TARGET_RK3588_SDIO)" = "y" ] || [ "$(BR2_PACKAGE_BATOCERA_TARGET_RK3588_MAINLINE)" = "y" ]; then \
        find $(@D)/intel -type f ! -name 'ibt-*' ! -path '*/iwlwifi/*' -delete; \
    fi

    # iwlwifi loads only the newest API it supports, keep one spare
    $(ALLLINUXFIRMWARES_PKGDIR)/prune-iwlwifi.sh $(@D) $(LINUX_DIR)

    # -n is mandatory while some other packages provides firmwares too
    # this is not ideal, but i don't know how to tell to buildroot to install this package first
    # (and not worry about all packages installing firmwares)
    rsync -au --checksum $(@D)/ $(TARGET_DIR)/lib/firmware/

    # Logic for X86_64: Prune ARM blobs inside folders used by both
    if [ "$(BR2_PACKAGE_BATOCERA_TARGET_X86_64_ANY)" = "y" ]; then \
        find $(TARGET_DIR)/lib/firmware/mediatek -name "mt81*" -prune -exec rm -rf {} +; \
        rm -rf $(TARGET_DIR)/lib/firmware/mediatek/sof*; \
        rm -rf $(TARGET_DIR)/lib/firmware/mrvl/cpt*; \
        rm -f $(TARGET_DIR)/lib/firmware/a300_*.fw; \
        rm -f $(TARGET_DIR)/lib/firmware/*.inp; \
        rm -f $(TARGET_DIR)/lib/firmware/lt9611uxc_fw.bin; \
        find $(TARGET_DIR)/lib/firmware/ti -maxdepth 1 -type f -delete; \
    fi
    
    # Logic for ARM SM8250: drop older Adreno firmware
    if [ "$(BR2_PACKAGE_BATOCERA_TARGET_SM8250)" = "y" ]; then \
        rm -f $(TARGET_DIR)/lib/firmware/a300_*.fw; \
        rm -f $(TARGET_DIR)/lib/firmware/a420_*.fw; \
        rm -f $(TARGET_DIR)/lib/firmware/a530_*.fw; \
        rm -f $(TARGET_DIR)/lib/firmware/yamato_*.fw; \
        rm -f $(TARGET_DIR)/lib/firmware/leia_*.fw; \
    fi

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

    # tqftpserv serves wlanmdsp.mbn from any remoteproc dir, keep only the qrb4210 adsp
    if [ "$(BR2_PACKAGE_BATOCERA_TARGET_SM6115)" = "y" ]; then \
        find $(TARGET_DIR)/lib/firmware/qcom/qrb4210 ! -type d ! -name "adsp*" -delete; \
    fi
endef

# Qualcomm Wi-Fi board files for Steam Deck OLED and other x86 handhelds
define ALLLINUXFIRMWARES_LINK_QCA_WIFI_BT
    mkdir -p $(TARGET_DIR)/lib/firmware/ath11k/QCA2066
    cp -rf $(BR2_EXTERNAL_BATOCERA_PATH)/package/batocera/firmwares/alllinuxfirmwares/QCA206X/* \
        $(TARGET_DIR)/lib/firmware/ath11k/QCA2066
endef

# symlink AMD GPU firmware for 890M devices
define ALLLINUXFIRMWARES_FIX_AMD_890M
    ln -sf /lib/firmware/amdgpu/isp_4_1_1.bin \
        $(TARGET_DIR)/lib/firmware/amdgpu/isp_4_1_0.bin
endef

# Realtek BT symlinks for RK3588 kernel compatibility
define ALLLINUXFIRMWARES_LINK_RTL_BT
    ln -sf /lib/firmware/rtl_bt/rtl8852bu_fw.bin $(TARGET_DIR)/lib/firmware/rtl8852bu_fw
    ln -sf /lib/firmware/rtl_bt/rtl8852bu_config.bin $(TARGET_DIR)/lib/firmware/rtl8852bu_config
endef

# Apply hooks based on architecture
ifeq ($(BR2_x86_64),y)
    ALLLINUXFIRMWARES_POST_INSTALL_TARGET_HOOKS += ALLLINUXFIRMWARES_LINK_QCA_WIFI_BT
    ALLLINUXFIRMWARES_POST_INSTALL_TARGET_HOOKS += ALLLINUXFIRMWARES_FIX_AMD_890M
endif

ifeq ($(BR2_PACKAGE_BATOCERA_TARGET_RK3588)$(BR2_PACKAGE_BATOCERA_TARGET_RK3588_SDIO)$(BR2_PACKAGE_BATOCERA_TARGET_RK3588_MAINLINE),y)
    ALLLINUXFIRMWARES_POST_INSTALL_TARGET_HOOKS += ALLLINUXFIRMWARES_LINK_RTL_BT
endif

$(eval $(generic-package))
