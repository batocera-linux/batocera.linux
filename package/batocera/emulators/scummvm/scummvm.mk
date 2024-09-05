################################################################################
#
# scummvm
#
################################################################################
# Version: 2.8.1 - "Oh MMy!"
SCUMMVM_VERSION = v2.8.1
SCUMMVM_SITE = $(call github,scummvm,scummvm,$(SCUMMVM_VERSION))
SCUMMVM_LICENSE = GPLv2
SCUMMVM_DEPENDENCIES += sdl2 zlib libmpeg2 libogg libvorbis flac libmad
SCUMMVM_DEPENDENCIES += libpng libtheora faad2 freetype libjpeg-bato fluidsynth

SCUMMVM_ADDITIONAL_FLAGS += -I$(STAGING_DIR)/usr/include -lpthread -lm
SCUMMVM_ADDITIONAL_FLAGS += -L$(STAGING_DIR)/usr/lib -lGLESv2 -lEGL

ifeq ($(BR2_PACKAGE_RPI_USERLAND),y)
    SCUMMVM_ADDITIONAL_FLAGS += -I$(STAGING_DIR)/usr/include/interface/vcos/pthreads \
        -I$(STAGING_DIR)/usr/include/interface/vmcs_host/linux -lbcm_host -lvchostif
    SCUMMVM_CONF_OPTS += --host=raspberrypi
endif

ifeq ($(BR2_aarch64)$(BR2_arm),y)
    SCUMMVM_CONF_OPTS += --host=arm-linux
else ifeq ($(BR2_riscv),y)
    SCUMMVM_CONF_OPTS += --host=riscv64-linux
else
    SCUMMVM_CONF_OPTS += --host=$(GNU_TARGET_NAME)
endif

SCUMMVM_CONF_ENV += RANLIB="$(TARGET_RANLIB)" STRIP="$(TARGET_STRIP)"
SCUMMVM_CONF_ENV += AR="$(TARGET_AR) cru" AS="$(TARGET_AS)"

SCUMMVM_CONF_OPTS += --opengl-mode=auto --disable-debug --enable-optimizations \
    --enable-mt32emu --enable-flac --enable-mad --enable-vorbis --disable-tremor \
    --enable-all-engines --enable-fluidsynth --disable-taskbar --disable-timidity \
    --disable-alsa --enable-vkeybd --enable-release --disable-eventrecorder \
    --prefix=/usr --with-sdl-prefix="$(STAGING_DIR)/usr"

ifeq ($(BR2_PACKAGE_LIBMPEG2),y)
    SCUMMVM_CONF_OPTS += --enable-mpeg2 --with-mpeg2-prefix="$(STAGING_DIR)/usr/lib"
endif

SCUMMVM_MAKE_OPTS += RANLIB="$(TARGET_RANLIB)" STRIP="$(TARGET_STRIP)"
SCUMMVM_MAKE_OPTS += AR="$(TARGET_AR) cru" AS="$(TARGET_AS)" LD="$(TARGET_CXX)"

define SCUMMVM_CONFIGURE_CMDS
    (cd $(@D) && rm -rf config.cache && \
	$(TARGET_CONFIGURE_OPTS) \
	$(TARGET_CONFIGURE_ARGS) \
	$(SCUMMVM_CONF_ENV) \
	./configure \
		--prefix=/usr \
		--exec-prefix=/usr \
		--sysconfdir=/etc \
		--localstatedir=/var \
		--program-prefix="" \
        $(SCUMMVM_CONF_OPTS) \
	)
endef

define SCUMMVM_ADD_VIRTUAL_KEYBOARD
    cp -f $(@D)/backends/vkeybd/packs/vkeybd_default.zip \
        $(TARGET_DIR)/usr/share/scummvm
    cp -f $(@D)/backends/vkeybd/packs/vkeybd_small.zip \
        $(TARGET_DIR)/usr/share/scummvm
    mkdir -p $(TARGET_DIR)/usr/share/evmapy/
    cp -f $(BR2_EXTERNAL_BATOCERA_PATH)/package/batocera/emulators/scummvm/scummvm.keys \
        $(TARGET_DIR)/usr/share/evmapy/
endef

SCUMMVM_POST_INSTALL_TARGET_HOOKS += SCUMMVM_ADD_VIRTUAL_KEYBOARD

$(eval $(autotools-package))
