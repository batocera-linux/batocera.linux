################################################################################
#
# mupen64plus core
#
################################################################################

#MUPEN64PLUS_CORE_VERSION = e58b813f5827c193c1bf5734e5029cf0b41c4b61
#MUPEN64PLUS_CORE_SITE = $(call github,ricrpi,mupen64plus-core,$(MUPEN64PLUS_CORE_VERSION))
MUPEN64PLUS_CORE_VERSION = 2d3d2d0761c9d1f6bab6f4da2ab65ffbbb08332f
MUPEN64PLUS_CORE_SITE = $(call github,mupen64plus,mupen64plus-core,$(MUPEN64PLUS_CORE_VERSION))
MUPEN64PLUS_CORE_LICENSE = MIT
MUPEN64PLUS_CORE_DEPENDENCIES = sdl2 alsa-lib
MUPEN64PLUS_CORE_INSTALL_STAGING = YES

MUPEN64PLUS_GL_CFLAGS = -I$(STAGING_DIR)/usr/include -L$(STAGING_DIR)/usr/lib

ifeq ($(BR2_PACKAGE_XORG7),y)
	# nothing special
else
	MUPEN64PLUS_GL_LDLIBS = -lGLESv2 -lEGL
	MUPEN64PLUS_PARAMS = USE_GLES=1
endif

ifeq ($(BR2_PACKAGE_RPI_USERLAND),y)
	MUPEN64PLUS_CORE_DEPENDENCIES += rpi-userland
	MUPEN64PLUS_GL_LDLIBS += -lbcm_host
	MUPEN64PLUS_PARAMS += VC=1
endif

ifeq ($(BR2_ARM_CPU_HAS_NEON),y)
        MUPEN64PLUS_PARAMS += NEON=1
	MUPEN64PLUS_HOST_CPU = armv7
endif

ifeq ($(BR2_PACKAGE_RECALBOX_TARGET_X86),y)
	MUPEN64PLUS_HOST_CPU = i586
endif

define MUPEN64PLUS_CORE_BUILD_CMDS
        CFLAGS="$(TARGET_CFLAGS)" CXXFLAGS="$(TARGET_CXXFLAGS)" \
        $(MAKE)  CXX="$(TARGET_CXX)" CC="$(TARGET_CC)" LD="$(TARGET_LD)" RANLIB="$(TARGET_RANLIB)" AR="$(TARGET_AR)" CROSS_COMPILE="$(STAGING_DIR)/usr/bin/" \
	PREFIX="$(STAGING_DIR)/usr" \
	PKG_CONFIG="$(HOST_DIR)/usr/bin/pkg-config" \
	HOST_CPU="$(MUPEN64PLUS_HOST_CPU)" \
	-C $(@D)/projects/unix all $(MUPEN64PLUS_PARAMS) OPTFLAGS="$(TARGET_CXXFLAGS)" 
endef

define MUPEN64PLUS_CORE_INSTALL_STAGING_CMDS
        CFLAGS="$(TARGET_CFLAGS)" CXXFLAGS="$(TARGET_CXXFLAGS)" \
        $(MAKE)  CXX="$(TARGET_CXX)" CC="$(TARGET_CC)" LD="$(TARGET_LD)" RANLIB="$(TARGET_RANLIB)" AR="$(TARGET_AR)" CROSS_COMPILE="$(STAGING_DIR)/usr/bin/" \
	PREFIX="$(STAGING_DIR)/usr" \
	PKG_CONFIG="$(HOST_DIR)/usr/bin/pkg-config" \
	HOST_CPU="$(MUPEN64PLUS_HOST_CPU)" \
	INSTALL="/usr/bin/install" \
	INSTALL_STRIP_FLAG="" \
	-C $(@D)/projects/unix all $(MUPEN64PLUS_PARAMS) OPTFLAGS="$(TARGET_CXXFLAGS)" install
endef

define MUPEN64PLUS_CORE_INSTALL_TARGET_CMDS
	$(INSTALL) -m 0644 $(@D)/projects/unix/libmupen64plus.so.2.0.0 $(TARGET_DIR)/usr/lib
endef

define MUPEN64PLUS_CORE_CROSS_FIXUP
        $(SED) 's|/opt/vc/include|$(STAGING_DIR)/usr/include|g' $(@D)/projects/unix/Makefile
        $(SED) 's|/opt/vc/lib|$(STAGING_DIR)/usr/lib|g' $(@D)/projects/unix/Makefile
endef

MUPEN64PLUS_CORE_PRE_CONFIGURE_HOOKS += MUPEN64PLUS_CORE_CROSS_FIXUP

$(eval $(generic-package))
