################################################################################
#
# freeimage
#
################################################################################
FREEIMAGE_VERSION = 3.16.0
FREEIMAGE_LIB_VERSION = 3
FREEIMAGE_SITE = http://downloads.sourceforge.net/freeimage
FREEIMAGE_SOURCE = FreeImage3160.zip
FREEIMAGE_LICENSE = GPLv2
FREEIMAGE_INSTALL_STAGING = YES

FREEIMAGE_CFLAGS= 

define FREEIMAGE_EXTRACT_CMDS
	unzip -q -o -d $(BUILD_DIR) $(DL_DIR)/$(FREEIMAGE_SOURCE)
	cp -r $(BUILD_DIR)/FreeImage/* $(@D)
	rm -rf $(BUILD_DIR)/FreeImage
endef

ifeq ($(BR2_ARM_CPU_HAS_NEON),y)
	FREEIMAGE_CFLAGS=$(TARGET_CFLAGS) -DPNG_ARM_NEON_OPT=0
endif

define FREEIMAGE_BUILD_CMDS
	CXXFLAGS="$(FREEIMAGE_CFLAGS)" CFLAGS="$(FREEIMAGE_CFLAGS)" $(MAKE) CC="$(TARGET_CC)" CXX="$(TARGET_CXX)" LD="$(TARGET_LD)" -C $(@D)
endef

define FREEIMAGE_INSTALL_STAGING_CMDS
	$(INSTALL) -D -m 644 package/freeimage/freeimage.pc \
		$(STAGING_DIR)/usr/lib/pkgconfig/freeimage.pc
	$(INSTALL) -D -m 644 "$(@D)/Source/FreeImage.h" \
		"$(STAGING_DIR)/usr/include/FreeImage.h"
	$(INSTALL) -D -m 755 "$(@D)/libfreeimage-$(FREEIMAGE_VERSION).so" \
		"$(STAGING_DIR)/usr/lib/libfreeimage.so.$(FREEIMAGE_LIB_VERSION)"
	ln -sf "libfreeimage.so.$(FREEIMAGE_LIB_VERSION)" \
		"$(STAGING_DIR)/usr/lib/libfreeimage.so"
endef

define FREEIMAGE_INSTALL_TARGET_CMDS
	$(INSTALL) -D -m 644 package/freeimage/freeimage.pc \
		$(TARGET_DIR)/usr/lib/pkgconfig/freeimage.pc
	$(INSTALL) -D -m 644 "$(@D)/Source/FreeImage.h" \
		"$(TARGET_DIR)/usr/include/FreeImage.h"
	$(INSTALL) -D -m 755 "$(@D)/libfreeimage-$(FREEIMAGE_VERSION).so" \
		"$(TARGET_DIR)/usr/lib/libfreeimage.so.$(FREEIMAGE_LIB_VERSION)"
	ln -sf "libfreeimage.so.$(FREEIMAGE_LIB_VERSION)" \
		"$(TARGET_DIR)/usr/lib/libfreeimage.so"
endef

$(eval $(generic-package))
