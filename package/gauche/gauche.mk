################################################################################
#
# gauche
#
################################################################################

GAUCHE_VERSION = 0.9.8
GAUCHE_SOURCE = Gauche-$(GAUCHE_VERSION).tgz
GAUCHE_SITE = http://downloads.sourceforge.net/project/gauche/Gauche
GAUCHE_LICENSE = BSD-3-Clause, Boehm-gc, SRFI (srfi-11.scm), reload (reload.scm)
GAUCHE_LICENSE_FILES = COPYING
GAUCHE_DEPENDENCIES = host-gauche
# We're patching configure.ac
GAUCHE_AUTORECONF = YES

HOST_GAUCHE_CONF_OPTS = --without-zlib
GAUCHE_CONF_OPTS = --without-libatomic-ops

# Enable embedded axTLS
GAUCHE_TLS_LIBS = axtls

ifeq ($(BR2_PACKAGE_MBEDTLS),y)
GAUCHE_TLS_LIBS += mbedtls
GAUCHE_DEPENDENCIES += mbedtls
endif

GAUCHE_CONF_OPTS += --with-tls="$(GAUCHE_TLS_LIBS)"

ifeq ($(BR2_PACKAGE_ZLIB),y)
GAUCHE_CONF_OPTS += --with-zlib=$(STAGING_DIR)
GAUCHE_DEPENDENCIES += zlib
else
GAUCHE_CONF_OPTS += --without-zlib
endif

# Detection of c99 support in configure fails without WCHAR. To enable
# automatic detection of c99 support by configure, we need to enable
# WCHAR in toolchain. But actually we do not need WCHAR at gauche
# runtime. So reuesting WCHAR in toolchain just for automatic detection
# will be overkill. To solve this, explicitly -std=gnu99 is specified
# here.
GAUCHE_CONF_ENV = CFLAGS="$(TARGET_CFLAGS) -std=gnu99"

$(eval $(autotools-package))
$(eval $(host-autotools-package))
