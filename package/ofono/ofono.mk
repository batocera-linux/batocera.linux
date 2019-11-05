################################################################################
#
# ofono
#
################################################################################

OFONO_VERSION = 1.30
OFONO_SOURCE = ofono-$(OFONO_VERSION).tar.xz
OFONO_SITE = $(BR2_KERNEL_MIRROR)/linux/network/ofono
OFONO_LICENSE = GPL-2.0
OFONO_LICENSE_FILES = COPYING
OFONO_DEPENDENCIES = \
	host-pkgconf \
	dbus \
	libglib2 \
	libcap-ng \
	mobile-broadband-provider-info

OFONO_CONF_OPTS = \
	--disable-test \
	--with-dbusconfdir=/etc \
	$(if $(BR2_INIT_SYSTEMD),--with-systemdunitdir=/usr/lib/systemd/system)

# N.B. Qualcomm QMI modem support requires O_CLOEXEC; so
# make sure that it is defined.
OFONO_CONF_ENV += CFLAGS="$(TARGET_CFLAGS) -D_GNU_SOURCE"

define OFONO_INSTALL_INIT_SYSV
	$(INSTALL) -m 0755 -D package/ofono/S46ofono $(TARGET_DIR)/etc/init.d/S46ofono
endef

define OFONO_INSTALL_INIT_SYSTEMD
	mkdir -p $(TARGET_DIR)/etc/systemd/systemd/multi-user.target.wants
	ln -fs ../../../../usr/lib/systemd/system/ofono.service \
		$(TARGET_DIR)/etc/systemd/system/multi-user.target.wants
endef

ifeq ($(BR2_PACKAGE_HAS_UDEV),y)
OFONO_CONF_OPTS += --enable-udev
OFONO_DEPENDENCIES += udev
else
OFONO_CONF_OPTS += --disable-udev
endif

ifeq ($(BR2_PACKAGE_BLUEZ_UTILS),y)
OFONO_CONF_OPTS += --enable-bluetooth
OFONO_DEPENDENCIES += bluez_utils
else
OFONO_CONF_OPTS += --disable-bluetooth
endif

# required by 0003-build-Add-check-for-explicit_bzero-support.patch
OFONO_AUTORECONF = YES

$(eval $(autotools-package))
