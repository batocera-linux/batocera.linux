################################################################################
#
# Scummvm
#
################################################################################

SCUMMVM_VERSION = gles_custom

SCUMMVM_SITE = $(call github,vanfanel,scummvm,$(SCUMMVM_VERSION))

SCUMMVM_LICENSE = GPL2
SCUMMVM_DEPENDENCIES = sdl zlib jpeg-turbo libmpeg2 libogg libvorbis flac libmad libpng libtheora \
	faad2 fluidsynth freetype 

SCUMMVM_ADDITIONAL_FLAGS= -I$(STAGING_DIR)/usr/include -I$(STAGING_DIR)/usr/include/interface/vcos/pthreads -I$(STAGING_DIR)/usr/include/interface/vmcs_host/linux -lpthread -lm -L$(STAGING_DIR)/usr/lib -lbcm_host -lGLESv2 -lEGL -lvchostif 


define SCUMMVM_RPI_FIXUP
        $(SED) 's|/opt/vc/include|$(STAGING_DIR)/usr/include|g' $(@D)/configure
        $(SED) 's|-lGLESv1_CM|-lGLESv2|g' $(@D)/configure
endef

ifeq ($(BR2_cortex_a7),y)
        SCUMMVM_PRE_CONFIGURE_HOOKS += $(SED) 's|-march=armv6zk|-march=armv7-a|g' $(@D)/configure
endif

ifeq ($(BR2_ARM_FPU_NEON_VFPV4),y)
        SCUMMVM_PRE_CONFIGURE_HOOKS += $(SED) 's|-march=vfpu|-mfpu=neon|g' $(@D)/configure
endif

SCUMMVM_PRE_CONFIGURE_HOOKS += SCUMMVM_RPI_FIXUP



define SCUMMVM_CONFIGURE_CMDS 
	(cd $(@D); rm -rf config.cache; \
                $(TARGET_CONFIGURE_ARGS) \
                $(TARGET_CONFIGURE_OPTS) \
                CFLAGS="$(TARGET_CFLAGS) $(SCUMMVM_ADDITIONAL_FLAGS)" \
                CXXFLAGS="$(TARGET_CXXFLAGS) $(SCUMMVM_ADDITIONAL_FLAGS)" \
		CPPFLAGS="$(SCUMMVM_ADDITIONAL_FLAGS)" \
                LDFLAGS="$(TARGET_LDFLAGS) $(SCUMMVM_ADDITIONAL_FLAGS)" \
                CROSS_COMPILE="$(HOST_DIR)/usr/bin/" \
		GLES_RPI_CXXFLAGS="$(CXXFLAGS) $(SCUMMVM_ADDITIONAL_FLAGS)" \
                GLES_RPI_LIBS="$(SCUMMVM_ADDITIONAL_FLAGS)" \
		OPENGL_CFLAGS="$(SCUMMVM_ADDITIONAL_FLAGS)" \
		OPENGL_LIBS="$(SCUMMVM_ADDITIONAL_FLAGS)" \
                ./configure \
		--enable-gles-rpi --disable-debug --enable-release --enable-optimizations --disable-mt32emu --enable-flac --disable-mad --disable-vorbis --disable-tremor \
		--disable-fluidsynth --disable-taskbar --disable-timidity --disable-alsa \
                --prefix=/usr --host=arm --with-sdl-prefix="$(STAGING_DIR)/usr/bin/" --enable-release --host=arm-linux-gnueabi \
        )	
endef

define SCUMMVM_BUILD_CMDS
	$(MAKE) AS="$(TARGET_AS)" STRIP="$(TARGET_STRIP)" RANLIB="$(TARGET_RANLIB)" AR="$(TARGET_AR) cru" -C $(@D)
endef 

$(eval $(autotools-package))
