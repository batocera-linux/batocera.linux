################################################################################
#
# alllinuxfirmwares
#
################################################################################

ALLLINUXFIRMWARES_VERSION = 20220509
ALLLINUXFIRMWARES_SITE = http://git.kernel.org/pub/scm/linux/kernel/git/firmware/linux-firmware.git
ALLLINUXFIRMWARES_SITE_METHOD = git

define ALLLINUXFIRMWARES_INSTALL_TARGET_CMDS
    mkdir -p $(TARGET_DIR)/lib/firmware

    # exclude some dirs not required on batocera
    rm -rf $(@D)/liquidio
    rm -rf $(@D)/netronome

    # -n is mandatory while some other packages provides firmwares too
    # this is not ideal, but i don't know how to tell to buildroot to install this package first (and not worry about all packages installing firmwares)
    cp -prn $(@D)/* $(TARGET_DIR)/lib/firmware/
endef

# because it adds so non required files on the rpi ; we prefer the specific rpi firmware packages
define ALLLINUXFIRMWARES_DELETE_BRCM
    rm -rf $(@D)/brcm
endef

ifeq ($(BR2_PACKAGE_BATOCERA_RPI_ANY),y)
    ALLLINUXFIRMWARES_PRE_INSTALL_TARGET_HOOKS += ALLLINUXFIRMWARES_DELETE_BRCM
endif

# realtek uses symbolic links for some firmware between different cards
define ALLLINUXFIRMWARES_REALTEK_POST_PROCESS
    # create realtek wifi symbolic links
    cd $(TARGET_DIR)/lib/firmware/rtlwifi ; \
    ln -sf rtl8192eu_nic.bin rtl8192eefw.bin ; \
    ln -sf rtl8723bu_ap_wowlan.bin rtl8723bs_ap_wowlan.bin ; \
    ln -sf rtl8723bu_nic.bin rtl8723bs_nic.bin
    # create realtek bluetooth symbolic links
    cd $(TARGET_DIR)/lib/firmware/rtl_bt ; \
    ln -sf rtl8723bs_config-OBDA8723.bin rtl8723bs_config-OBDA0623.bin ; \
    ln -sf rtl8821c_config.bin rtl8821a_config.bin
endef

ALLLINUXFIRMWARES_POST_INSTALL_TARGET_HOOKS += ALLLINUXFIRMWARES_REALTEK_POST_PROCESS

$(eval $(generic-package))
