################################################################################
#
# xwiimote
#
################################################################################

XWIIMOTE_VERSION = f2be57e24fc24652308840cec2ed702b9d1138df
XWIIMOTE_SITE = $(call github,dvdhrm,xwiimote,$(XWIIMOTE_VERSION))

XWIIMOTE_DEPENDENCIES = udev

define XWIIMOTE_AUTOGEN
    cd $(@D); PKG_CONFIG="$(HOST_DIR)/usr/bin/pkg-config" ./autogen.sh
endef

XWIIMOTE_PRE_CONFIGURE_HOOKS += XWIIMOTE_AUTOGEN


$(eval $(autotools-package))
