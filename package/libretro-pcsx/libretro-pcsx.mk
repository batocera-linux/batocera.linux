################################################################################
#
# PCSXREARMED
#
################################################################################
LIBRETRO_PCSX_VERSION = 871bf1c4bfb98db8e58e3d2b37bb777ae2f41f43
LIBRETRO_PCSX_SITE = $(call github,libretro,pcsx_rearmed,$(LIBRETRO_PCSX_VERSION))
PCSX_INCLUDES=-I$(STAGING_DIR)/usr/include -I$(STAGING_DIR)/usr/include/interface/vcos/pthreads -I$(STAGING_DIR)/usr/include/interface/vmcs_host/linux

define LIBRETRO_PCSX_CONFIGURE_CMDS
	$(SED) "s|/opt/vc/include|$(STAGING_DIR)/usr/include|g" $(@D)/configure
	$(SED) "s|/opt/vc/lib|$(STAGING_DIR)/usr/lib|g" $(@D)/configure
	$(SED) "s|/opt/vc/include/interface/vcos/pthreads|$(STAGING_DIR)/usr/include/interface/vcos/pthreads|g" $(@D)/configure
	$(SED) "s|/opt/vc/include/interface/vmcs_host/linux|$(STAGING_DIR)/usr/include/interface/vmcs_host/linux|g" $(@D)/configure
	$(SED) "s|-lGLESv1_CM|-lGLESv2|g" $(@D)/configure
	$(SED) "/need_xlib=\"yes\"/d"  $(@D)/configure
 	( cd $(@D) && \
      	LDFLAGS="$(TARGET_LDFLAGS)" AS="$(TARGET_AS)" CXX="$(TARGET_CXX)" CC="$(TARGET_CC)" CFLAGS="$(TARGET_CFLAGS)" CXXFLAGS="$(TARGET_CXXFLAGS)" ./configure --platform=libretro )	
endef

define LIBRETRO_PCSX_BUILD_CMDS
	CFLAGS="$(TARGET_CFLAGS)" CXXFLAGS="$(TARGET_CXXFLAGS)" $(MAKE) CXX="$(TARGET_CXX)" CC="$(TARGET_CC)" AR="$(TARGET_AR)" \
	-C $(@D)
endef

define LIBRETRO_PCSX_INSTALL_TARGET_CMDS
	$(INSTALL) -D $(@D)/libretro.so \
		$(TARGET_DIR)/usr/lib/libretro/pcsx_rearmed_libretro.so
endef

$(eval $(generic-package))
