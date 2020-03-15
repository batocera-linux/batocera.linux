################################################################################
#
# mupen64plus core
#
################################################################################
# Version.: Commits on Feb 28, 2020
MUPEN64PLUS_CORE_VERSION = f799c5165b1248e6299097399633d733809b8098
MUPEN64PLUS_CORE_SITE = $(call github,mupen64plus,mupen64plus-core,$(MUPEN64PLUS_CORE_VERSION))
MUPEN64PLUS_CORE_LICENSE = GPLv2
MUPEN64PLUS_CORE_DEPENDENCIES = sdl2 alsa-lib freetype dejavu
MUPEN64PLUS_CORE_INSTALL_STAGING = YES

MUPEN64PLUS_GL_CFLAGS = -I$(STAGING_DIR)/usr/include -L$(STAGING_DIR)/usr/lib

ifeq ($(BR2_PACKAGE_LIBGLU),y)
    MUPEN64PLUS_CORE_DEPENDENCIES += libglu
	MUPEN64PLUS_GL_LDLIBS = -lGL
else
	MUPEN64PLUS_GL_LDLIBS = -lGLESv2 -lEGL
	MUPEN64PLUS_PARAMS = USE_GLES=1
endif

ifeq ($(BR2_PACKAGE_RPI_USERLAND),y)
	MUPEN64PLUS_CORE_DEPENDENCIES += rpi-userland
	MUPEN64PLUS_GL_LDLIBS += -lbcm_host
	MUPEN64PLUS_PARAMS += VC=1
endif

ifeq ($(BR2_arm),y)
	MUPEN64PLUS_HOST_CPU = armv7
endif

ifeq ($(BR2_aarch64),y)
	MUPEN64PLUS_HOST_CPU = aarch64
	MUPEN64PLUS_PARAMS += NEON=1
	MUPEN64PLUS_PARAMS += NO_ASM=1
endif

ifeq ($(BR2_ARM_CPU_HAS_NEON),y)
	MUPEN64PLUS_PARAMS += NEON=1
endif

ifeq ($(BR2_PACKAGE_BATOCERA_TARGET_X86),y)
	MUPEN64PLUS_HOST_CPU = i586
endif

ifeq ($(BR2_PACKAGE_BATOCERA_TARGET_X86_64),y)
	MUPEN64PLUS_HOST_CPU = x86_64
endif

define MUPEN64PLUS_CORE_BUILD_CMDS
	CFLAGS="$(TARGET_CFLAGS)" CXXFLAGS="$(TARGET_CXXFLAGS)" \
        $(MAKE)  CXX="$(TARGET_CXX)" CC="$(TARGET_CC)" LD="$(TARGET_LD)" RANLIB="$(TARGET_RANLIB)" AR="$(TARGET_AR)" CROSS_COMPILE="$(STAGING_DIR)/usr/bin/" \
        AS="$(HOST_DIR)/bin/nasm" \
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
	mkdir -p $(TARGET_DIR)/usr/lib
	$(INSTALL) -m 0644 $(@D)/projects/unix/libmupen64plus.so.2.0.0 $(TARGET_DIR)/usr/lib
	mkdir -p $(TARGET_DIR)/usr/share/mupen64plus
	ln -sf /usr/share/fonts/dejavu/DejaVuSans.ttf $(TARGET_DIR)/usr/share/mupen64plus/font.ttf
	cp $(@D)/data/mupen64plus.ini $(TARGET_DIR)/usr/share/mupen64plus/mupen64plus.ini
	cp $(@D)/data/mupencheat.txt "$(TARGET_DIR)/usr/share/mupen64plus/mupencheat.txt"

	# input.xml
	mkdir -p $(TARGET_DIR)/usr/share/batocera/datainit/system/configs/mupen64
	cp $(BR2_EXTERNAL_BATOCERA_PATH)/package/batocera/emulators/mupen64plus/mupen64plus-core/controllers/input.xml \
		$(TARGET_DIR)/usr/share/batocera/datainit/system/configs/mupen64
endef

define MUPEN64PLUS_CORE_CROSS_FIXUP
	$(SED) 's|/opt/vc/include|$(STAGING_DIR)/usr/include|g' $(@D)/projects/unix/Makefile
	$(SED) 's|/opt/vc/lib|$(STAGING_DIR)/usr/lib|g' $(@D)/projects/unix/Makefile
endef

MUPEN64PLUS_CORE_PRE_CONFIGURE_HOOKS += MUPEN64PLUS_CORE_CROSS_FIXUP

$(eval $(generic-package))
