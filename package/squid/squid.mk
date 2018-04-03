################################################################################
#
# squid
#
################################################################################

SQUID_VERSION_MAJOR = 3.5
SQUID_VERSION = $(SQUID_VERSION_MAJOR).27
SQUID_SOURCE = squid-$(SQUID_VERSION).tar.xz
SQUID_SITE = http://www.squid-cache.org/Versions/v3/$(SQUID_VERSION_MAJOR)
SQUID_LICENSE = GPL-2.0+
SQUID_LICENSE_FILES = COPYING
# For 0001-assume-get-certificate-ok.patch
SQUID_AUTORECONF = YES
SQUID_DEPENDENCIES = libcap host-libcap host-pkgconf \
	$(if $(BR2_PACKAGE_LIBNETFILTER_CONNTRACK),libnetfilter_conntrack)
SQUID_CONF_ENV = \
	ac_cv_epoll_works=yes \
	ac_cv_func_setresuid=yes \
	ac_cv_func_va_copy=yes \
	ac_cv_func___va_copy=yes \
	ac_cv_func_strnstr=no \
	ac_cv_have_squid=yes \
	BUILDCXX="$(HOSTCXX)" \
	BUILDCXXFLAGS="$(HOST_CXXFLAGS)"
SQUID_CONF_OPTS = \
	--enable-async-io=8 \
	$(if $(BR2_TOOLCHAIN_USES_MUSL),--disable-linux-netfilter,--enable-linux-netfilter) \
	--enable-removal-policies="lru,heap" \
	--with-filedescriptors=1024 \
	--disable-ident-lookups \
	--without-mit-krb5 \
	--enable-auth-basic="fake getpwnam" \
	--enable-auth-digest="file" \
	--enable-auth-negotiate="wrapper" \
	--enable-auth-ntlm="fake" \
	--disable-strict-error-checking \
	--enable-external-acl-helpers="file_userip" \
	--with-logdir=/var/log/squid/ \
	--with-pidfile=/var/run/squid.pid \
	--with-swapdir=/var/cache/squid/ \
	--with-default-user=squid

# Atomics in Squid use __sync built-ins on 4 and 8 bytes. However, the
# configure script tests them using AC_TRY_RUN, so we have to give
# some hints.
ifeq ($(BR2_TOOLCHAIN_HAS_SYNC_4)$(BR2_TOOLCHAIN_HAS_SYNC_8),yy)
SQUID_CONF_ENV += squid_cv_gnu_atomics=yes
else
SQUID_CONF_ENV += squid_cv_gnu_atomics=no
endif

ifeq ($(BR2_PACKAGE_OPENSSL),y)
SQUID_CONF_OPTS += --with-openssl
SQUID_DEPENDENCIES += openssl
else
SQUID_CONF_OPTS += --without-openssl
endif

ifeq ($(BR2_PACKAGE_GNUTLS),y)
SQUID_CONF_OPTS += --with-gnutls
SQUID_DEPENDENCIES += gnutls
else
SQUID_CONF_OPTS += --without-gnutls
endif

define SQUID_CLEANUP_TARGET
	rm -f $(addprefix $(TARGET_DIR)/usr/bin/, \
		RunCache RunAccel)
	rm -f $(addprefix $(TARGET_DIR)/etc/, \
		cachemgr.conf mime.conf.default squid.conf.default)
endef

SQUID_POST_INSTALL_TARGET_HOOKS += SQUID_CLEANUP_TARGET

define SQUID_USERS
	squid -1 squid -1 * - - - Squid proxy cache
endef

define SQUID_INSTALL_INIT_SYSV
	$(INSTALL) -m 755 -D package/squid/S97squid \
		$(TARGET_DIR)/etc/init.d/S97squid
endef

define SQUID_INSTALL_INIT_SYSTEMD
	$(INSTALL) -D -m 0644 $(@D)/tools/systemd/squid.service \
		$(TARGET_DIR)/usr/lib/systemd/system/squid.service
	mkdir -p $(TARGET_DIR)/etc/systemd/system/multi-user.target.wants
	ln -sf ../../../..//usr/lib/systemd/system/squid.service \
		$(TARGET_DIR)/etc/systemd/system/multi-user.target.wants/squid.service
endef

$(eval $(autotools-package))
