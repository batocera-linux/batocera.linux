################################################################################
#
# DosBox-X
#
################################################################################
# Version.: Commits on Jul 1, 2021
DOSBOX_X_VERSION = dosbox-x-v0.83.15
DOSBOX_X_SITE = $(call github,joncampbell123,dosbox-x,$(DOSBOX_X_VERSION))
DOSBOX_X_DEPENDENCIES = sdl2 sdl2_net sdl_sound zlib libpng libogg libvorbis
DOSBOX_X_LICENSE = GPLv2

DOSBOX_X_PKG_DIR = $(TARGET_DIR)/opt/retrolx/dosbox-x

define DOSBOX_X_CONFIGURE_CMDS
	# Create directories
	mkdir -p $(DOSBOX_X_PKG_DIR)

	cd $(@D); ./autogen.sh; $(TARGET_CONFIGURE_OPTS) CROSS_COMPILE="$(HOST_DIR)/usr/bin/" LIBS="-lvorbisfile -lvorbis -logg" \
        ./configure --host="$(GNU_TARGET_NAME)" \
                    --enable-core-inline \
                    --enable-dynrec \
                    --enable-unaligned_memory \
                    --prefix=/opt/retrolx/dosbox-x \
                    --disable-sdl \
                    --enable-sdl2 \
                    --with-sdl2-prefix="$(STAGING_DIR)/usr";
endef

define DOSBOX_X_CONFIGURE_CONFIG
    mkdir -p $(TARGET_DIR)/usr/share/batocera/datainit/system/configs/dosbox
    
    cp -rf $(@D)/dosbox-x.reference.conf \
        $(TARGET_DIR)/usr/share/batocera/datainit/system/configs/dosbox/dosboxx.conf
endef

DOSBOX_X_POST_INSTALL_TARGET_HOOKS += DOSBOX_X_CONFIGURE_CONFIG

define DOSBOX_X_MAKE_PKG
	# Build Pacman package
	cd $(DOSBOX_X_PKG_DIR) && $(BR2_EXTERNAL_BATOCERA_PATH)/scripts/retrolx-makepkg \
	$(BR2_EXTERNAL_BATOCERA_PATH)/package/retrolx/emulators/dosbox-x/PKGINFO \
	$(BATOCERA_SYSTEM_ARCH) $(HOST_DIR)
endef

DOSBOX_X_POST_INSTALL_TARGET_HOOKS += DOSBOX_X_MAKE_PKG

$(eval $(autotools-package))
