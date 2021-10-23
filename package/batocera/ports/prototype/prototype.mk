################################################################################
#
# Prototype (R-Type Clone)
#
################################################################################
# Version.: Commits on Dec 20, 2020
PROTOTYPE_VERSION = 12d2de8639982db12091ca37eeee9036b54f3fa7
PROTOTYPE_SITE = $(call github,ptitSeb,prototype,$(PROTOTYPE_VERSION))

PROTOTYPE_DEPENDENCIES = sdl2 sdl2_mixer gl4es glu
PROTOTYPE_LICENSE = GPL-2.0

define PROTOTYPE_BUILD_CMDS
		$(TARGET_CONFIGURE_OPTS) $(MAKE) \
		CPP="$(TARGET_CPP)" CXX="$(TARGET_CXX)" CC="$(TARGET_CC)" \
		AS="$(TARGET_CC)" LD="$(TARGET_CXX)" STRIP="$(TARGET_STRIP)" \
		-C $(@D) -f Makefile SDL2=1 RPI4=1 \
		LDFLAGS="-L$(HOST_DIR)/aarch64-buildroot-linux-gnu/sysroot/lib64 -lm -L$(HOST_DIR)/aarch64-buildroot-linux-gnu/sysroot/usr/lib -lSDL2 -lSDL2_mixer -lGL"
endef

define PROTOTYPE_INSTALL_TARGET_CMDS
	mkdir -p $(TARGET_DIR)/usr/share/prototype
	$(INSTALL) -D $(@D)/prototype $(TARGET_DIR)/usr/bin/prototype
	chmod 0755 $(TARGET_DIR)/usr/bin/prototype
    cp -av $(@D)/Data $(TARGET_DIR)/usr/share/prototype
	cp $(BR2_EXTERNAL_BATOCERA_PATH)/package/batocera/ports/prototype/prototype.keys $(TARGET_DIR)/usr/share/evmapy
endef

$(eval $(generic-package))

