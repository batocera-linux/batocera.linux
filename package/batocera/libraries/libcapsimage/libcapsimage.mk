################################################################################
#
# LIBCAPSIMAGE
#
################################################################################

LIBCAPSIMAGE_VERSION = 549b1955d52a70b9f7egie88a419f6ecfb6ee61142
LIBCAPSIMAGE_SITE = https://github.com/simonowen/capsimage
LIBCAPSIMAGE_SITE_METHOD = git

LIBCAPSIMAGE_INSTALL_STAGING = YES

define LIBCAPSIMAGE_INSTALL_STAGING_CMDS
	mkdir -p $(STAGING_DIR)/usr/lib/capsimage
	cp $(@D)/libcapsimage.so.5.1 \
		$(STAGING_DIR)/usr/lib
	cp  $(@D)/src/LibIPF/*.h \
		$(STAGING_DIR)/usr/lib/capsimage
	cp $(@D)/src/Core/Common*.h $(STAGING_DIR)/usr/lib/capsimage
	cp $(@D)/Caps*.h $(STAGING_DIR)/usr/lib/capsimage
	ln -sf $(STAGING_DIR)/usr/lib/libcapsimage.so.5.1 $(STAGING_DIR)/usr/lib/libcapsimage.so
endef

$(eval $(autotools-package))
