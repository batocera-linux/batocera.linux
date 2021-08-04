################################################################################
#
# CITRA
#
################################################################################
# Version.: Commits on Jul 08, 2020

CITRA_DEPENDENCIES = fmt boost ffmpeg sdl2
CITRA_SITE_METHOD=git
CITRA_GIT_SUBMODULES=YES
CITRA_LICENSE = GPLv2

# Use citra-android for AArch64 (SDL2 only)
ifeq ($(BR2_PACKAGE_BATOCERA_TARGET_S922X),y)
CITRA_VERSION = dad2146e4e65980deb7d273bf1e9c58334847c19
CITRA_SITE = https://github.com/citra-emu/citra-android.git
CITRA_CONF_OPTS += -DENABLE_QT=OFF

# Use citra for x86_64 and enable citra-qt
else
CITRA_VERSION = 842031a2eb0b4bac4a351db914530296812962d1
CITRA_SITE = https://github.com/citra-emu/citra.git
CITRA_CONF_OPTS += -DENABLE_QT=ON
CITRA_CONF_OPTS += -DENABLE_QT_TRANSLATION=ON
CITRA_CONF_OPTS += -DARCHITECTURE=x86_64
CITRA_DEPENDENCIES += qt5base qt5tools qt5multimedia
endif

# Should be set when the package cannot be built inside the source tree but needs a separate build directory.
CITRA_SUPPORTS_IN_SOURCE_BUILD = NO

CITRA_CONF_OPTS += -DCMAKE_BUILD_TYPE=Release
CITRA_CONF_OPTS += -DENABLE_WEB_SERVICE=OFF
CITRA_CONF_OPTS += -DENABLE_FFMPEG=ON
CITRA_CONF_OPTS += -DBUILD_SHARED_LIBS=FALSE

CITRA_CONF_ENV += LDFLAGS=-lpthread

ifeq ($(BR2_PACKAGE_BATOCERA_TARGET_X86_64),y)
define CITRA_INSTALL_TARGET_CMDS
       	mkdir -p $(TARGET_DIR)/usr/bin
        mkdir -p $(TARGET_DIR)/usr/lib
	$(INSTALL) -D $(@D)/buildroot-build/bin/Release/citra-qt \
		$(TARGET_DIR)/usr/bin/
endef
else
define CITRA_INSTALL_TARGET_CMDS
        mkdir -p $(TARGET_DIR)/usr/bin
        mkdir -p $(TARGET_DIR)/usr/lib

	$(INSTALL) -D $(@D)/buildroot-build/bin/citra \
		$(TARGET_DIR)/usr/bin/
endef
endif

define CITRA_EVMAP
	mkdir -p $(TARGET_DIR)/usr/share/evmapy
	
	cp -prn $(BR2_EXTERNAL_BATOCERA_PATH)/package/batocera/emulators/citra/3ds.citra.keys \
		$(TARGET_DIR)/usr/share/evmapy
endef

CITRA_POST_INSTALL_TARGET_HOOKS = CITRA_EVMAP

$(eval $(cmake-package))
