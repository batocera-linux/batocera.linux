################################################################################
#
# quagga
#
################################################################################

QUAGGA_VERSION = 1.2.4
QUAGGA_SITE = http://download.savannah.gnu.org/releases/quagga
QUAGGA_DEPENDENCIES = host-gawk host-pkgconf
QUAGGA_LICENSE = GPL-2.0+
QUAGGA_LICENSE_FILES = COPYING

# We need to override the sysconf and localstate directories so that
# quagga can create files as the quagga user without extra
# intervention
QUAGGA_CONF_OPTS = \
	--program-transform-name='' \
	--sysconfdir=/etc/quagga \
	--localstatedir=/var/run/quagga

# quagga has its own internal copy of getopt_long. To avoid conflicts with libc's
# getopt, we need to make sure that the getopt function itself is also built.
QUAGGA_CONF_ENV = \
	CFLAGS="$(TARGET_CFLAGS) -DREALLY_NEED_PLAIN_GETOPT"

ifeq ($(BR2_PACKAGE_LIBCAP),y)
QUAGGA_CONF_OPTS += --enable-capabilities
QUAGGA_DEPENDENCIES += libcap
else
QUAGGA_CONF_OPTS += --disable-capabilities
endif

ifeq ($(BR2_PACKAGE_PROTOBUF_C),y)
QUAGGA_CONF_OPTS += --enable-protobuf
QUAGGA_DEPENDENCIES += protobuf-c
else
QUAGGA_CONF_OPTS += --disable-protobuf
endif

QUAGGA_CONF_OPTS += $(if $(BR2_PACKAGE_QUAGGA_ZEBRA),--enable-zebra,--disable-zebra)
QUAGGA_CONF_OPTS += $(if $(BR2_PACKAGE_QUAGGA_BGPD),--enable-bgpd,--disable-bgpd)
QUAGGA_CONF_OPTS += $(if $(BR2_PACKAGE_QUAGGA_RIPD),--enable-ripd,--disable-ripd)
QUAGGA_CONF_OPTS += $(if $(BR2_PACKAGE_QUAGGA_RIPNGD),--enable-ripngd,--disable-ripngd)
QUAGGA_CONF_OPTS += $(if $(BR2_PACKAGE_QUAGGA_OSPFD),--enable-ospfd,--disable-ospfd --disable-ospfapi)
QUAGGA_CONF_OPTS += $(if $(BR2_PACKAGE_QUAGGA_OSPF6D),--enable-ospf6d,--disable-ospf6d)
QUAGGA_CONF_OPTS += $(if $(BR2_PACKAGE_QUAGGA_PIMD),--enable-pimd,--disable-pimd)
QUAGGA_CONF_OPTS += $(if $(BR2_PACKAGE_QUAGGA_WATCHQUAGGA),--enable-watchquagga,--disable-watchquagga)
QUAGGA_CONF_OPTS += $(if $(BR2_PACKAGE_QUAGGA_ISISD),--enable-isisd,--disable-isisd)
QUAGGA_CONF_OPTS += $(if $(BR2_PACKAGE_QUAGGA_BGP_ANNOUNCE),--enable-bgp-announce,--disable-bgp-announce)
QUAGGA_CONF_OPTS += $(if $(BR2_PACKAGE_QUAGGA_TCP_ZEBRA),--enable-tcp-zebra,--disable-tcp-zebra)

define QUAGGA_USERS
	quagga -1 quagga -1 * - - - Quagga priv drop user
endef

# Set the permissions of /etc/quagga such that quagga (through vtysh)
# can save the configuration - set the folder recursively as the files
# need to be 600, and then set the folder (non-recursively) to 755 so
# it can used.  Quagga also needs to write to the folder as it moves
# and creates, rather than overwriting.
define QUAGGA_PERMISSIONS
	/etc/quagga r 600 quagga quagga - - - - -
	/etc/quagga d 755 quagga quagga - - - - -
endef

# In order for the QUAGGA_PERMISSIONS variable above to work,
# /etc/quagga has to exist. However, this package without any
# sub-option enabled will not create /etc/quagga, so let's create it
# unconditionally in a post-install hook, in case it hasn't been
# already created by the quagga installation.
define QUAGGA_CREATE_ETC_QUAGGA
	mkdir -p $(TARGET_DIR)/etc/quagga
endef
QUAGGA_POST_INSTALL_TARGET_HOOKS += QUAGGA_CREATE_ETC_QUAGGA

ifeq ($(BR2_PACKAGE_QUAGGA_NHRPD),y)
QUAGGA_CONF_OPTS += --enable-nhrpd
QUAGGA_DEPENDENCIES += c-ares
else
QUAGGA_CONF_OPTS += --disable-nhrpd
endif

ifeq ($(BR2_PACKAGE_QUAGGA_SNMP),y)
QUAGGA_CONF_ENV += ac_cv_path_NETSNMP_CONFIG=$(STAGING_DIR)/usr/bin/net-snmp-config
QUAGGA_CONF_OPTS += --enable-snmp=agentx
QUAGGA_DEPENDENCIES += netsnmp
endif

ifeq ($(BR2_PACKAGE_QUAGGA_VTYSH),y)
QUAGGA_CONF_OPTS += --enable-vtysh
QUAGGA_DEPENDENCIES += readline
else
QUAGGA_CONF_OPTS += --disable-vtysh
endif

ifeq ($(BR2_TOOLCHAIN_SUPPORTS_PIE),)
QUAGGA_CONF_OPTS += --disable-pie
endif

define QUAGGA_INSTALL_INIT_SYSTEMD
	$(INSTALL) -D -m 644 package/quagga/quagga_tmpfiles.conf \
		$(TARGET_DIR)/usr/lib/tmpfiles.d/quagga.conf
	$(INSTALL) -D -m 644 package/quagga/quagga@.service \
		$(TARGET_DIR)/usr/lib/systemd/system/quagga@.service
endef

$(eval $(autotools-package))
