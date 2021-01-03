################################################################################
#
# L3AFPAD
#
################################################################################

L3AFPAD_VERSION = v0.8.18.1.11
L3AFPAD_SITE = $(call github,stevenhoneyman,l3afpad,$(L3AFPAD_VERSION))

L3AFPAD_DEPENDENCIES = libgtk3 host-intltool harfbuzz
L3AFPAD_LICENSE = GPL-2.0+
L3AFPAD_LICENSE_FILES = COPYING

define L3AFPAD_CONFIGURE_CMDS
    cd $(@D); PATH=$(HOST_DIR)/bin:$(PATH) ./autogen.sh ; \
    $(TARGET_CONFIGURE_OPTS) PREFIX=$(STAGING_DIR) CFLAGS="-I$(STAGING_DIR)/usr/include" LDFLAGS="-L$(STAGING_DIR)/usr/lib" ./configure --disable-nls --prefix=/usr
endef

$(eval $(autotools-package))
