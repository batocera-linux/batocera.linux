################################################################################
#
# openvmtools
#
################################################################################

OPENVMTOOLS_VERSION_MAJOR = 10.3.5
OPENVMTOOLS_VERSION = $(OPENVMTOOLS_VERSION_MAJOR)-10430147
OPENVMTOOLS_SITE = https://github.com/vmware/open-vm-tools/releases/download/stable-$(OPENVMTOOLS_VERSION_MAJOR)
OPENVMTOOLS_SOURCE = open-vm-tools-$(OPENVMTOOLS_VERSION).tar.gz
OPENVMTOOLS_LICENSE = LGPL-2.1
OPENVMTOOLS_LICENSE_FILES = COPYING

# configure.ac is patched
OPENVMTOOLS_AUTORECONF = YES
OPENVMTOOLS_CONF_OPTS = --with-dnet \
	--without-icu --without-x --without-gtk2 \
	--without-gtkmm --without-kernel-modules \
	--disable-deploypkg --without-xerces
OPENVMTOOLS_CONF_ENV += CUSTOM_DNET_CPPFLAGS=" "
OPENVMTOOLS_DEPENDENCIES = host-nfs-utils libglib2 libdnet

ifeq ($(BR2_PACKAGE_LIBTIRPC),y)
OPENVMTOOLS_DEPENDENCIES += libtirpc
endif

# When libfuse is available, openvmtools can build vmblock-fuse, so
# make sure that libfuse gets built first
ifeq ($(BR2_PACKAGE_LIBFUSE),y)
OPENVMTOOLS_DEPENDENCIES += libfuse
endif

ifeq ($(BR2_PACKAGE_OPENSSL),y)
OPENVMTOOLS_CONF_OPTS += --with-ssl
OPENVMTOOLS_DEPENDENCIES += openssl
else
OPENVMTOOLS_CONF_OPTS += --without-ssl
endif

ifeq ($(BR2_PACKAGE_OPENVMTOOLS_PROCPS),y)
OPENVMTOOLS_CONF_OPTS += --with-procps
OPENVMTOOLS_DEPENDENCIES += procps-ng
else
OPENVMTOOLS_CONF_OPTS += --without-procps
endif

ifeq ($(BR2_PACKAGE_OPENVMTOOLS_PAM),y)
OPENVMTOOLS_CONF_OPTS += --with-pam
OPENVMTOOLS_DEPENDENCIES += linux-pam
else
OPENVMTOOLS_CONF_OPTS += --without-pam
endif

ifeq ($(BR2_PACKAGE_OPENVMTOOLS_RESOLUTIONKMS),y)
OPENVMTOOLS_CONF_OPTS += --enable-resolutionkms
OPENVMTOOLS_DEPENDENCIES += libdrm udev
else
OPENVMTOOLS_CONF_OPTS += --disable-resolutionkms
endif

# symlink needed by lib/system/systemLinux.c (or will cry in /var/log/messages)
# defined in lib/misc/hostinfoPosix.c
# /sbin/shutdown needed for Guest OS restart/shutdown from hypervisor
define OPENVMTOOLS_POST_INSTALL_TARGET_THINGIES
	ln -fs os-release $(TARGET_DIR)/etc/lfs-release
	if [ ! -e $(TARGET_DIR)/sbin/shutdown ]; then \
		$(INSTALL) -D -m 755 package/openvmtools/shutdown \
			$(TARGET_DIR)/sbin/shutdown; \
	fi
endef

OPENVMTOOLS_POST_INSTALL_TARGET_HOOKS += OPENVMTOOLS_POST_INSTALL_TARGET_THINGIES

define OPENVMTOOLS_INSTALL_INIT_SYSV
	$(INSTALL) -D -m 755 package/openvmtools/S10vmtoolsd \
		$(TARGET_DIR)/etc/init.d/S10vmtoolsd
endef

define OPENVMTOOLS_INSTALL_INIT_SYSTEMD
	$(INSTALL) -D -m 644 package/openvmtools/vmtoolsd.service \
		$(TARGET_DIR)/usr/lib/systemd/system/vmtoolsd.service
	mkdir -p $(TARGET_DIR)/etc/systemd/system/multi-user.target.wants
	ln -fs ../../../../usr/lib/systemd/system/vmtoolsd.service \
		$(TARGET_DIR)/etc/systemd/system/multi-user.target.wants/vmtoolsd.service
endef

$(eval $(autotools-package))
