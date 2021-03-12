################################################################################
#
# mali g31
#
################################################################################
# Version.: Commits on Nov 13, 2019
MALI_G31_VERSION = d4000def121b818ae0f583d8372d57643f723fdc
MALI_G31_SITE = $(call github,LibreELEC,libmali,$(MALI_G31_VERSION))
MALI_G31_INSTALL_STAGING = YES
MALI_G31_PROVIDES = libegl libgles libmali
MALI_G31_DEPENDENCIES = mali-bifrost-module

MALI_G31_BLOB_FILENAME="libmali-bifrost-g31-r16p0-gbm.so"

ifeq ($(BR2_arm),y)
MALI_G31_ARCH="arm-linux-gnueabihf"
else
MALI_G31_ARCH="aarch64-linux-gnu"
endif

# We need to build the gbm wrapper
define MALI_G31_BUILD_CMDS
	cd $(@D)/src
	$(TARGET_CC) $(@D)/src/gbm.c -I$(STAGING_DIR)/usr/include/libdrm -L$(STAGING_DIR)/usr/lib -I$(@D)/include -ldrm -fPIC -shared -o $(@D)/libgbm.so
endef

define MALI_G31_INSTALL_STAGING_CMDS
	mkdir -p $(STAGING_DIR)/usr/lib/pkgconfig

	cp $(@D)/lib/$(MALI_G31_ARCH)/$(MALI_G31_BLOB_FILENAME) $(STAGING_DIR)/usr/lib/libmali.so
	cp $(@D)/libgbm.so $(STAGING_DIR)/usr/lib/libgbm.so

	(cd $(STAGING_DIR)/usr/lib && ln -sf libmali.so libMali.so)
	(cd $(STAGING_DIR)/usr/lib && ln -sf libmali.so libEGL.so)
	(cd $(STAGING_DIR)/usr/lib && ln -sf libmali.so libEGL.so.1)
	(cd $(STAGING_DIR)/usr/lib && ln -sf libmali.so libGLESv1_CM.so)
	(cd $(STAGING_DIR)/usr/lib && ln -sf libmali.so libGLESv1_CM.so.1)
	(cd $(STAGING_DIR)/usr/lib && ln -sf libmali.so libGLESv2.so)
	(cd $(STAGING_DIR)/usr/lib && ln -sf libmali.so libGLESv2.so.2)
	
	cp -pr $(@D)/include    $(STAGING_DIR)/usr

	# Use GBM wrapper
	cp $(@D)/src/gbm.h 	$(STAGING_DIR)/usr/include/gbm.h
	cp $(@D)/src/gbm.pc.cmake $(@D)/pkgconfig/gbm.pc.cmake

	for X in gbm egl glesv1_cm glesv2; \
	do \
		cp $(@D)/pkgconfig/$${X}.pc.cmake                 	$(STAGING_DIR)/usr/lib/pkgconfig/$${X}.pc; \
		sed -i -e s+@CMAKE_INSTALL_INCLUDEDIR@+include+g 	$(STAGING_DIR)/usr/lib/pkgconfig/$${X}.pc; \
		sed -i -e s+@CMAKE_INSTALL_LIBDIR@+lib+g         	$(STAGING_DIR)/usr/lib/pkgconfig/$${X}.pc; \
	done
endef

define MALI_G31_INSTALL_TARGET_CMDS
	mkdir -p $(TARGET_DIR)/usr/lib

	cp $(@D)/lib/$(MALI_G31_ARCH)/$(MALI_G31_BLOB_FILENAME) $(TARGET_DIR)/usr/lib/libmali.so
	cp $(@D)/libgbm.so $(TARGET_DIR)/usr/lib/libgbm.so

	(cd $(TARGET_DIR)/usr/lib && ln -sf libmali.so libMali.so)
	(cd $(TARGET_DIR)/usr/lib && ln -sf libmali.so libEGL.so)
	(cd $(TARGET_DIR)/usr/lib && ln -sf libmali.so libEGL.so.1)
	(cd $(TARGET_DIR)/usr/lib && ln -sf libmali.so libGLESv1_CM.so)
	(cd $(TARGET_DIR)/usr/lib && ln -sf libmali.so libGLESv1_CM.so.1)
	(cd $(TARGET_DIR)/usr/lib && ln -sf libmali.so libGLESv2.so)
	(cd $(TARGET_DIR)/usr/lib && ln -sf libmali.so libGLESv2.so.2)
endef

$(eval $(generic-package))
