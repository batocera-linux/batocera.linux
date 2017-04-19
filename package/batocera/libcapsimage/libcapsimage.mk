################################################################################
#
# LIBCAPSIMAGE
#
################################################################################

LIBCAPSIMAGE_SOURCE = ipfdec_source$(LIBCAPSIMAGE_VERSION).zip
LIBCAPSIMAGE_VERSION = 4.2
LIBCAPSIMAGE_SITE = http://www.kryoflux.com/download
LIBCAPSIMAGE_SITE_METHOD = wget
LIBCAPSIMAGE_SUBDIR = CAPSImage

LIBCAPSIMAGE_INSTALL_STAGING = YES

define LIBCAPSIMAGE_EXTRACT_CMDS
	$(UNZIP) $(DL_DIR)/$(LIBCAPSIMAGE_SOURCE) -d $(@D)
endef

define LIBCAPSIMAGE_INSTALL_STAGING_CMDS
	mkdir -p $(STAGING_DIR)/usr/lib/capsimage
	cp $(@D)/CAPSImage/libcapsimage.so.4.2 \
		$(STAGING_DIR)/usr/lib
	cp -r $(@D)/CAPSImage/include/caps \
		$(STAGING_DIR)/usr/lib/capsimage
	ln -sf $(STAGING_DIR)/usr/lib/libcapsimage.so.4.2 $(STAGING_DIR)/usr/lib/libcapsimage.so
endef

define LIBCAPSIMAGE_INSTALL_TARGET_CMDS
	mkdir -p $(STAGING_DIR)/usr/lib/capsimage
	cp $(@D)/CAPSImage/libcapsimage.so.4.2 \
		$(TARGET_DIR)/usr/lib
	ln -sf /usr/lib/libcapsimage.so.4.2 $(TARGET_DIR)/usr/lib/libcapsimage.so.4
endef

define LIBCAPSIMAGE_PRE_CONFIGURE_FIXUP
	chmod u+x $(@D)/CAPSImage/configure
endef

LIBCAPSIMAGE_PRE_CONFIGURE_HOOKS += LIBCAPSIMAGE_PRE_CONFIGURE_FIXUP

$(eval $(autotools-package))
