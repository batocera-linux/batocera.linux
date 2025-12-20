################################################################################
#
# xpadneo
#
################################################################################
# Version: Commits on Dec 18, 2025
XPADNEO_VERSION = 886a83d3987a435dedf9bf9db995b5ec5363f0ce
XPADNEO_SITE = $(call github,atar-axis,xpadneo,$(XPADNEO_VERSION))
XPADNEO_DEPENDENCIES = host-libcurl host-cabextract bluez5_utils
XPADNEO_MODULE_SUBDIRS = hid-xpadneo/src

XPADNEO_USER_EXTRA_CFLAGS = -w -Wno-error=unused-function

XPADNEO_MODULE_MAKE_OPTS = \
	KCFLAGS="$$KCFLAGS $(XPADNEO_USER_EXTRA_CFLAGS)"

define XPADNEO_INSTALL_TARGET_CMDS
	mkdir -p $(TARGET_DIR)/etc/udev/rules.d/
	mkdir -p $(TARGET_DIR)/etc/modprobe.d/
	cp -v $(@D)/hid-xpadneo/etc-udev-rules.d/*.rules $(TARGET_DIR)/etc/udev/rules.d/
	cp -v $(@D)/hid-xpadneo/etc-modprobe.d/*.conf $(TARGET_DIR)/etc/modprobe.d/
	echo "options bluetooth disable_ertm=1" >> $(TARGET_DIR)/etc/modprobe.d/xpadneo.conf
	echo "options hid_xpadneo disable_shift_mode=1" >> $(TARGET_DIR)/etc/modprobe.d/xpadneo.conf
endef

$(eval $(kernel-module))
$(eval $(generic-package))
