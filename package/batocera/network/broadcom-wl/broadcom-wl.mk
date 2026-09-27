################################################################################
#
# broadcom-wl
#
################################################################################

BROADCOM_WL_VERSION = 6_30_223_271
BROADCOM_WL_SOURCE = hybrid-v35_64-nodebug-pcoem-$(BROADCOM_WL_VERSION).tar.gz
BROADCOM_WL_SITE = https://docs.broadcom.com/docs-and-downloads/docs/linux_sta
BROADCOM_WL_LICENSE = PROPRIETARY
BROADCOM_WL_LICENSE_FILES = lib/LICENSE.txt

define BROADCOM_WL_EXTRACT_CMDS
	$(TAR) -xf $(BROADCOM_WL_DL_DIR)/$(BROADCOM_WL_SOURCE) -C $(@D)
endef

# the gcc >= 4.9 check misreads two-digit gcc majors
define BROADCOM_WL_FIX_MAKEFILE
	$(SED) '/BRCM_WLAN_IFNAME/s/eth/wlan/' $(@D)/src/wl/sys/wl_linux.c
	$(SED) '/GE_49 :=/s/:= .*/:= 1/' $(@D)/Makefile
endef
BROADCOM_WL_POST_PATCH_HOOKS += BROADCOM_WL_FIX_MAKEFILE

define BROADCOM_WL_INSTALL_TARGET_CMDS
	$(INSTALL) -D -m 0644 $(BROADCOM_WL_PKGDIR)/blacklist-wl.conf \
	    $(TARGET_DIR)/etc/modprobe.d/blacklist-wl.conf
	ln -sf /var/run/broadcom-wl/modprobe.conf \
	    $(TARGET_DIR)/etc/modprobe.d/broadcom-wl.conf
	$(INSTALL) -D -m 0755 $(BROADCOM_WL_PKGDIR)/S05broadcom-wl \
	    $(TARGET_DIR)/etc/init.d/S05broadcom-wl
endef

$(eval $(kernel-module))
$(eval $(generic-package))
