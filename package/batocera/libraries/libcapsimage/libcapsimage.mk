################################################################################
#
# LIBCAPSIMAGE
#
################################################################################

LIBCAPSIMAGE_SOURCE = spsdeclib_$(LIBCAPSIMAGE_VERSION)_source.zip
LIBCAPSIMAGE_VERSION = 5.1
LIBCAPSIMAGE_SITE = http://www.kryoflux.com/download
LIBCAPSIMAGE_SITE_METHOD = wget
LIBCAPSIMAGE_SUBDIR = capsimg_source_linux_macosx/CAPSImg

LIBCAPSIMAGE_INSTALL_STAGING = YES

define LIBCAPSIMAGE_EXTRACT_CMDS
	$(UNZIP) $(DL_DIR)/$(LIBCAPSIMAGE_DL_SUBDIR)/$(LIBCAPSIMAGE_SOURCE) -d $(@D)
	$(UNZIP) -x $(@D)/capsimg_source_linux_macosx.zip  -d $(@D)
endef

define LIBCAPSIMAGE_INSTALL_STAGING_CMDS
	mkdir -p $(STAGING_DIR)/usr/include/caps
	cp -r $(@D)/capsimg_source_linux_macosx/CAPSImg/*.h \
		$(STAGING_DIR)/usr/include/caps
	cp -r $(@D)/capsimg_source_linux_macosx/Codec/*.h \
		$(STAGING_DIR)/usr/include/caps
	cp -r $(@D)/capsimg_source_linux_macosx/Compatibility/*.h \
		$(STAGING_DIR)/usr/include/caps
	cp -r $(@D)/capsimg_source_linux_macosx/Core/*.h \
		$(STAGING_DIR)/usr/include/caps
	cp -r $(@D)/capsimg_source_linux_macosx/Device/*.h \
		$(STAGING_DIR)/usr/include/caps
	cp -r $(@D)/capsimg_source_linux_macosx/LibIPF/*.h \
		$(STAGING_DIR)/usr/include/caps
	mkdir -p $(STAGING_DIR)/usr/lib/capsimage
	cp $(@D)/capsimg_source_linux_macosx/CAPSImg/libcapsimage.so.5.1 \
		$(STAGING_DIR)/usr/lib
	ln -sf $(STAGING_DIR)/usr/lib/libcapsimage.so.5.1 $(STAGING_DIR)/usr/lib/libcapsimage.so
endef

define LIBCAPSIMAGE_INSTALL_TARGET_CMDS
	# Target generic install
	mkdir -p $(TARGET_DIR)/usr/lib/capsimage
	cp $(@D)/capsimg_source_linux_macosx/CAPSImg/libcapsimage.so.5.1 \
		$(TARGET_DIR)/usr/lib
	ln -sf /usr/lib/libcapsimage.so.5.1 $(TARGET_DIR)/usr/lib/libcapsimage.so.5

	# FS-UAE specific install
	mkdir -p $(TARGET_DIR)/usr/share/fs-uae/Plugins
	ln -sf /usr/lib/libcapsimage.so.5.1 \
		$(TARGET_DIR)/usr/share/fs-uae/Plugins/capsimg.so
        echo "$(CAPSIMG_VERSION)" > $(TARGET_DIR)/usr/share/fs-uae/Plugins/Version.txt
endef

define LIBCAPSIMAGE_PRE_CONFIGURE_FIXUP
	chmod u+x $(@D)/capsimg_source_linux_macosx/CAPSImg/configure
endef

LIBCAPSIMAGE_PRE_CONFIGURE_HOOKS += LIBCAPSIMAGE_PRE_CONFIGURE_FIXUP

$(eval $(autotools-package))
