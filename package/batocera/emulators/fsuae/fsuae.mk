################################################################################
#
# fsuae
#
################################################################################

FSUAE_VERSION = v3.2.35
FSUAE_SITE = $(call github,FrodeSolheim,fs-uae,$(FSUAE_VERSION))
FSUAE_LICENSE = GPLv2
FSUAE_DEPENDENCIES += libpng libmpeg2 libglib2 libcapsimage openal
FSUAE_DEPENDENCIES += sdl2 sdl2_ttf zlib
FSUAE_EMULATOR_INFO = fsuae.emulator.yml

FSUAE_AUTORECONF = YES

FSUAE_CONF_OPTS += --disable-static

FSUAE_MAKE_OPTS += \
    CXX_FOR_BUILD="$(HOSTCXX)" \
    CC_FOR_BUILD="$(HOSTCC)" \
    CXXFLAGS_FOR_BUILD="$(HOST_CXXFLAGS)" \
    CPPFLAGS_FOR_BUILD="$(HOST_CPPFLAGS)" \
    LDFLAGS_FOR_BUILD="$(HOST_LDFLAGS)"

define FSUAE_INSTALL_EVMAPY
	mkdir -p $(TARGET_DIR)/usr/share/evmapy
	$(INSTALL) -D -m 0644 \
	    $(BR2_EXTERNAL_BATOCERA_PATH)/package/batocera/emulators/fsuae/*.keys \
	        $(TARGET_DIR)/usr/share/evmapy/
endef

FSUAE_POST_INSTALL_TARGET_HOOKS = FSUAE_INSTALL_EVMAPY

$(eval $(autotools-package))
$(eval $(emulator-info-package))
