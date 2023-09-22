################################################################################
#
# eduke32
#
################################################################################
# July 02, 2023
EDUKE32_VERSION = 77e6bb66fc27b54f9b2fa448a138047c71fab02e
EDUKE32_SITE = https://voidpoint.io/terminx/eduke32/-/archive/$(EDUKE32_VERSION)
EDUKE32_DEPENDENCIES = sdl2 flac libvpx
EDUKE32_LICENSE = GPL-2.0

# Some build options are documented here: https://wiki.eduke32.com/wiki/Building_EDuke32_on_Linux
EDUKE32_BUILD_ARGS = STARTUP_WINDOW=0
EDUKE32_BUILD_ARGS += HAVE_GTK2=0
ifeq ($(BR2_aarch64)$(BR2_riscv),y)
    EDUKE32_BUILD_ARGS += USE_OPENGL=0
    EDUKE32_BUILD_ARGS += OPTOPT="-ffast-math"
endif

define EDUKE32_BUILD_CMDS
    $(MAKE) $(TARGET_CONFIGURE_OPTS) $(EDUKE32_BUILD_ARGS) -C $(@D)
    $(RM) -r $(@D)/obj
    $(MAKE) $(TARGET_CONFIGURE_OPTS) $(EDUKE32_BUILD_ARGS) FURY=1 -C $(@D)
endef

define EDUKE32_INSTALL_TARGET_CMDS
    $(INSTALL) -D -m 0755 $(@D)/eduke32 $(TARGET_DIR)/usr/bin/eduke32
    $(INSTALL) -D -m 0755 $(@D)/fury $(TARGET_DIR)/usr/bin/fury
    mkdir -p $(TARGET_DIR)/usr/share/evmapy
    cp $(BR2_EXTERNAL_BATOCERA_PATH)/package/batocera/ports/eduke32/eduke32.keys $(TARGET_DIR)/usr/share/evmapy
    cp $(BR2_EXTERNAL_BATOCERA_PATH)/package/batocera/ports/eduke32/eduke32.keys $(TARGET_DIR)/usr/share/evmapy/fury.keys
endef

$(eval $(generic-package))
