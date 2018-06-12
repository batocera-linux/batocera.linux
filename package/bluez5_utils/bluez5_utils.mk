################################################################################
#
# bluez5_utils
#
################################################################################

BLUEZ5_UTILS_VERSION = 5.49
BLUEZ5_UTILS_SOURCE = bluez-$(BLUEZ5_UTILS_VERSION).tar.xz
BLUEZ5_UTILS_SITE = $(BR2_KERNEL_MIRROR)/linux/bluetooth
BLUEZ5_UTILS_INSTALL_STAGING = YES
BLUEZ5_UTILS_DEPENDENCIES = dbus libglib2
BLUEZ5_UTILS_LICENSE = GPL-2.0+, LGPL-2.1+
BLUEZ5_UTILS_LICENSE_FILES = COPYING COPYING.LIB
# 0001-bt_shell-APIs-shall-only-be-build-if-readline-is-pre.patch
BLUEZ5_UTILS_AUTORECONF = YES

BLUEZ5_UTILS_CONF_OPTS = \
	--enable-tools \
	--enable-library \
	--disable-cups

ifeq ($(BR2_PACKAGE_BLUEZ5_UTILS_OBEX),y)
BLUEZ5_UTILS_CONF_OPTS += --enable-obex
BLUEZ5_UTILS_DEPENDENCIES += libical
else
BLUEZ5_UTILS_CONF_OPTS += --disable-obex
endif

ifeq ($(BR2_PACKAGE_BLUEZ5_UTILS_CLIENT),y)
BLUEZ5_UTILS_CONF_OPTS += --enable-client
BLUEZ5_UTILS_DEPENDENCIES += readline
else
BLUEZ5_UTILS_CONF_OPTS += --disable-client
endif

# experimental plugins
ifeq ($(BR2_PACKAGE_BLUEZ5_UTILS_EXPERIMENTAL),y)
BLUEZ5_UTILS_CONF_OPTS += --enable-experimental
else
BLUEZ5_UTILS_CONF_OPTS += --disable-experimental
endif

# enable health plugin
ifeq ($(BR2_PACKAGE_BLUEZ5_UTILS_PLUGINS_HEALTH),y)
BLUEZ5_UTILS_CONF_OPTS += --enable-health
else
BLUEZ5_UTILS_CONF_OPTS += --disable-health
endif

# enable midi profile
ifeq ($(BR2_PACKAGE_BLUEZ5_UTILS_PLUGINS_MIDI),y)
BLUEZ5_UTILS_CONF_OPTS += --enable-midi
BLUEZ5_UTILS_DEPENDENCIES += alsa-lib
else
BLUEZ5_UTILS_CONF_OPTS += --disable-midi
endif

# enable nfc plugin
ifeq ($(BR2_PACKAGE_BLUEZ5_UTILS_PLUGINS_NFC),y)
BLUEZ5_UTILS_CONF_OPTS += --enable-nfc
else
BLUEZ5_UTILS_CONF_OPTS += --disable-nfc
endif

# enable sap plugin
ifeq ($(BR2_PACKAGE_BLUEZ5_UTILS_PLUGINS_SAP),y)
BLUEZ5_UTILS_CONF_OPTS += --enable-sap
else
BLUEZ5_UTILS_CONF_OPTS += --disable-sap
endif

# enable sixaxis plugin
ifeq ($(BR2_PACKAGE_BLUEZ5_UTILS_PLUGINS_SIXAXIS),y)
BLUEZ5_UTILS_CONF_OPTS += --enable-sixaxis
else
BLUEZ5_UTILS_CONF_OPTS += --disable-sixaxis
endif

# install gatttool (For some reason upstream choose not to do it by default)
ifeq ($(BR2_PACKAGE_BLUEZ5_UTILS_DEPRECATED),y)
define BLUEZ5_UTILS_INSTALL_GATTTOOL
	$(INSTALL) -D -m 0755 $(@D)/attrib/gatttool $(TARGET_DIR)/usr/bin/gatttool
endef
BLUEZ5_UTILS_POST_INSTALL_TARGET_HOOKS += BLUEZ5_UTILS_INSTALL_GATTTOOL
# hciattach_bcm43xx defines default firmware path in `/etc/firmware`, but
# Broadcom firmware blobs are usually located in `/lib/firmware`.
BLUEZ5_UTILS_CONF_ENV += \
	CPPFLAGS='$(TARGET_CPPFLAGS) -DFIRMWARE_DIR=\"/lib/firmware\"'
BLUEZ5_UTILS_CONF_OPTS += --enable-deprecated
else
BLUEZ5_UTILS_CONF_OPTS += --disable-deprecated
endif

# enable test
ifeq ($(BR2_PACKAGE_BLUEZ5_UTILS_TEST),y)
BLUEZ5_UTILS_CONF_OPTS += --enable-test
else
BLUEZ5_UTILS_CONF_OPTS += --disable-test
endif

# use udev if available
ifeq ($(BR2_PACKAGE_HAS_UDEV),y)
BLUEZ5_UTILS_CONF_OPTS += --enable-udev
BLUEZ5_UTILS_DEPENDENCIES += udev
else
BLUEZ5_UTILS_CONF_OPTS += --disable-udev
endif

# integrate with systemd if available
ifeq ($(BR2_PACKAGE_SYSTEMD),y)
BLUEZ5_UTILS_CONF_OPTS += --enable-systemd
BLUEZ5_UTILS_DEPENDENCIES += systemd
else
BLUEZ5_UTILS_CONF_OPTS += --disable-systemd
endif

define BLUEZ5_UTILS_INSTALL_INIT_SYSTEMD
	mkdir -p $(TARGET_DIR)/etc/systemd/system/bluetooth.target.wants
	ln -fs ../../../../usr/lib/systemd/system/bluetooth.service \
		$(TARGET_DIR)/etc/systemd/system/bluetooth.target.wants/bluetooth.service
	ln -fs ../../../usr/lib/systemd/system/bluetooth.service \
		$(TARGET_DIR)/etc/systemd/system/dbus-org.bluez.service
endef

$(eval $(autotools-package))
