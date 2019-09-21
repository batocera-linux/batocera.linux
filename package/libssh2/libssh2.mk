################################################################################
#
# libssh2
#
################################################################################

LIBSSH2_VERSION = 1.9.0
LIBSSH2_SITE = https://www.libssh2.org/download
LIBSSH2_LICENSE = BSD
LIBSSH2_LICENSE_FILES = COPYING
LIBSSH2_INSTALL_STAGING = YES
LIBSSH2_CONF_OPTS = --disable-examples-build

# building from a git clone
LIBSSH2_AUTORECONF = YES

ifeq ($(BR2_PACKAGE_LIBSSH2_MBEDTLS),y)
LIBSSH2_DEPENDENCIES += mbedtls
LIBSSH2_CONF_OPTS += --with-libmbedcrypto-prefix=$(STAGING_DIR)/usr \
	--with-crypto=mbedtls
else ifeq ($(BR2_PACKAGE_LIBSSH2_LIBGCRYPT),y)
LIBSSH2_DEPENDENCIES += libgcrypt
LIBSSH2_CONF_OPTS += --with-libgcrypt-prefix=$(STAGING_DIR)/usr \
	--with-crypto=libgcrypt
# configure.ac forgets to link to dependent libraries of gcrypt breaking static
# linking
LIBSSH2_CONF_ENV += LIBS="`$(STAGING_DIR)/usr/bin/libgcrypt-config --libs`"
else ifeq ($(BR2_PACKAGE_LIBSSH2_OPENSSL),y)
LIBSSH2_DEPENDENCIES += host-pkgconf openssl
LIBSSH2_CONF_OPTS += --with-libssl-prefix=$(STAGING_DIR)/usr \
	--with-crypto=openssl
# configure.ac forgets to link to dependent libraries of openssl breaking static
# linking
LIBSSH2_CONF_ENV += LIBS=`$(PKG_CONFIG_HOST_BINARY) --libs openssl`
endif

# Add zlib support if enabled
ifeq ($(BR2_PACKAGE_ZLIB),y)
LIBSSH2_DEPENDENCIES += zlib
LIBSSH2_CONF_OPTS += --with-libz \
	--with-libz-prefix=$(STAGING_DIR)/usr
else
LIBSSH2_CONF_OPTS += --without-libz
endif

HOST_LIBSSH2_DEPENDENCIES += host-openssl
HOST_LIBSSH2_CONF_OPTS += --with-openssl \
	--with-libssl-prefix=$(HOST_DIR) \
	--without-libgcrypt

$(eval $(autotools-package))
$(eval $(host-autotools-package))
