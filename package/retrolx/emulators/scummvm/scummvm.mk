################################################################################
#
# Scummvm
#
################################################################################
# Version.: Commits on Sep 27, 2020
SCUMMVM_VERSION = v2.2.0
SCUMMVM_SITE = $(call github,scummvm,scummvm,$(SCUMMVM_VERSION))
SCUMMVM_LICENSE = GPLv2
SCUMMVM_DEPENDENCIES = sdl2 zlib jpeg libmpeg2 libogg libvorbis flac libmad libpng libtheora faad2 freetype

SCUMMVM_ADDITIONAL_FLAGS= -I$(STAGING_DIR)/usr/include -I$(STAGING_DIR)/usr/include/interface/vcos/pthreads -I$(STAGING_DIR)/usr/include/interface/vmcs_host/linux -lpthread -lm -L$(STAGING_DIR)/usr/lib -lGLESv2 -lEGL

SCUMMVM_PREFIX_DIR = /opt/retrolx/scummvm
SCUMMVM_PKG_DIR = $(TARGET_DIR)/opt/retrolx/scummvm

ifeq ($(BR2_PACKAGE_RPI_USERLAND),y)
	SCUMMVM_ADDITIONAL_FLAGS += -lbcm_host -lvchostif
	SCUMMVM_CONF_OPTS += --host=raspberrypi
endif

SCUMMVM_CONF_ENV += RANLIB="$(TARGET_RANLIB)" STRIP="$(TARGET_STRIP)" AR="$(TARGET_AR) cru" AS="$(TARGET_AS)"
SCUMMVM_CONF_OPTS += --disable-static --enable-c++11 --enable-opengl --disable-debug --enable-optimizations --enable-mt32emu --enable-flac --enable-mad --enable-vorbis --disable-tremor \
					 --enable-fluidsynth --disable-taskbar --disable-timidity --disable-alsa --enable-vkeybd --enable-keymapper --disable-eventrecorder \
                	 --prefix=$(SCUMMVM_PREFIX_DIR) --exec-prefix=$(SCUMMVM_PREFIX_DIR) --with-sdl-prefix="$(STAGING_DIR)/usr/bin/" --enable-release \

SCUMMVM_MAKE_OPTS += RANLIB="$(TARGET_RANLIB)" STRIP="$(TARGET_STRIP)" AR="$(TARGET_AR) cru" AS="$(TARGET_AS)" LD="$(TARGET_CXX)" DESTDIR="$(SCUMMVM_PKG_DIR)"

#define SCUMMVM_ADD_VIRTUAL_KEYBOARD
#	cp $(@D)/backends/vkeybd/packs/vkeybd_default.zip $(TARGET_DIR)/usr/share/scummvm
#	cp $(@D)/backends/vkeybd/packs/vkeybd_small.zip $(TARGET_DIR)/usr/share/scummvm
#endef
#SCUMMVM_POST_INSTALL_TARGET_HOOKS += SCUMMVM_ADD_VIRTUAL_KEYBOARD

define SCUMMVM_MAKEPKG
	# Add virtual keyboard files
	mkdir -p $(SCUMMVM_PKG_DIR)/usr/share/scummvm
	cp $(@D)/backends/vkeybd/packs/vkeybd_default.zip $(SCUMMVM_PKG_DIR)/usr/share/scummvm
	cp $(@D)/backends/vkeybd/packs/vkeybd_small.zip $(SCUMMVM_PKG_DIR)/usr/share/scummvm

	# Build Pacman package
	cd $(SCUMMVM_PKG_DIR) && $(BR2_EXTERNAL_BATOCERA_PATH)/scripts/retrolx-makepkg \
	$(BR2_EXTERNAL_BATOCERA_PATH)/package/retrolx/emulators/scummvm/PKGINFO \
	$(BATOCERA_SYSTEM_ARCH) $(HOST_DIR)
endef

SCUMMVM_POST_INSTALL_TARGET_HOOKS = SCUMMVM_MAKEPKG

$(eval $(autotools-package))
