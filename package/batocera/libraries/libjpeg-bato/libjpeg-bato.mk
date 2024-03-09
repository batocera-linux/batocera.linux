################################################################################
#
# libjpeg
#
################################################################################

LIBJPEG_BATO_VERSION = 9e
LIBJPEG_BATO_SITE = http://www.ijg.org/files
LIBJPEG_BATO_SOURCE = jpegsrc.v$(LIBJPEG_BATO_VERSION).tar.gz
LIBJPEG_BATO_LICENSE = IJG
LIBJPEG_BATO_LICENSE_FILES = README
LIBJPEG_BATO_INSTALL_STAGING = YES

define LIBJPEG_BATO_REMOVE_USELESS_TOOLS
	rm -f $(addprefix $(TARGET_DIR)/usr/bin/,cjpeg djpeg jpegtran rdjpgcom wrjpgcom)
endef

LIBJPEG_BATO_POST_INSTALL_TARGET_HOOKS += LIBJPEG_BATO_REMOVE_USELESS_TOOLS

define LIBJPEG_BATO_INSTALL_STAGING_PC
	$(INSTALL) -D -m 0644 package/libjpeg/libjpeg.pc.in \
		$(STAGING_DIR)/usr/lib/pkgconfig/libjpeg.pc
	version=`sed -e '/^PACKAGE_VERSION/!d;s/PACKAGE_VERSION = \(.*\)/\1/' $(@D)/Makefile` ; \
		$(SED) "s/@PACKAGE_VERSION@/$${version}/" $(STAGING_DIR)/usr/lib/pkgconfig/libjpeg.pc
endef

LIBJPEG_BATO_POST_INSTALL_STAGING_HOOKS += LIBJPEG_BATO_INSTALL_STAGING_PC

$(eval $(autotools-package))
$(eval $(host-autotools-package))
