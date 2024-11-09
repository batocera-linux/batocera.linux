################################################################################
#
# cannonball
#
################################################################################
# Version.: Commits on Jan 31, 2022
CANNONBALL_VERSION = 27493ebf62be3498dff93ed6a45e8e2db819bae1
CANNONBALL_SITE = $(call github,djyt,cannonball,$(CANNONBALL_VERSION))
CANNONBALL_LICENSE = GPLv2
CANNONBALL_DEPENDENCIES = sdl2 boost
CANNONBALL_SUPPORTS_IN_SOURCE_BUILD = NO
CANNONBALL_SUBDIR = cmake

CANNONBALL_CONF_OPTS += -DCMAKE_BUILD_TYPE=Release
CANNONBALL_CONF_OPTS += -DTARGET=$(CANNONBALL_TARGET)
# Enabling LTO as hires mode tends to be slow, it does help video rendering loops
CANNONBALL_EXE_LINKER_FLAGS += -flto
CANNONBALL_SHARED_LINKER_FLAGS += -flto
CANNONBALL_CONF_OPTS += -DCMAKE_CXX_FLAGS=-flto
CANNONBALL_CONF_OPTS += -DCMAKE_EXE_LINKER_FLAGS="$(CANNONBALL_EXE_LINKER_FLAGS)"
CANNONBALL_CONF_OPTS += -DCMAKE_SHARED_LINKER_FLAGS="$(CANNONBALL_SHARED_LINKER_FLAGS)"

ifeq ($(BR2_PACKAGE_BATOCERA_TARGET_X86_64_ANY),y)
CANNONBALL_TARGET = linux.cmake
else ifeq ($(BR2_PACKAGE_BATOCERA_GLES2)$(BR2_PACKAGE_BATOCERA_GLES3),y)
CANNONBALL_TARGET = pi4-opengles.cmake
CANNONBALL_RPI := $(subst ",,$(BR2_TARGET_OPTIMIZATION))
CANNONBALL_PRE_CONFIGURE_HOOKS += CANNONBALL_SETUP_CMAKE
endif

# Cannonball cmake files are hopelessly broken.
# Link libmali manually. Ideally we should fix cannonball to use pkg-config instead.
ifeq ($(BR2_PACKAGE_HAS_LIBMALI),y)
CANNONBALL_DEPENDENCIES += libmali
CANNONBALL_EXE_LINKER_FLAGS += -lmali
CANNONBALL_SHARED_LINKER_FLAGS += -lmali
endif

define CANNONBALL_SETUP_CMAKE
    # Arm compilation
	$(SED) 's|-mtune=cortex-a72|$(CANNONBALL_RPI)|g' $(@D)/cmake/pi4-opengles.cmake
endef

CANNONBALL_SOURCE_FILES = $(@D)/$(CANNONBALL_SUBDIR)/buildroot-build

define CANNONBALL_INSTALL_TARGET_CMDS
	$(INSTALL) -D $(CANNONBALL_SOURCE_FILES)/cannonball $(TARGET_DIR)/usr/bin/
	mkdir -p $(TARGET_DIR)/usr/share/batocera/datainit/system/configs/cannonball/res/
	$(INSTALL) -D $(CANNONBALL_SOURCE_FILES)/res/tilemap.bin \
	    $(TARGET_DIR)/usr/share/batocera/datainit/system/configs/cannonball/
	$(INSTALL) -D $(CANNONBALL_SOURCE_FILES)/res/tilepatch.bin \
	    $(TARGET_DIR)/usr/share/batocera/datainit/system/configs/cannonball/
	$(INSTALL) -D $(CANNONBALL_SOURCE_FILES)/config.xml \
	    $(TARGET_DIR)/usr/share/batocera/datainit/system/configs/cannonball/config_help.txt
endef

define CANNONBALL_EVMAPY
	mkdir -p $(TARGET_DIR)/usr/share/evmapy
	cp -prn $(BR2_EXTERNAL_BATOCERA_PATH)/package/batocera/ports/cannonball/cannonball.keys \
		$(TARGET_DIR)/usr/share/evmapy
endef

CANNONBALL_POST_INSTALL_TARGET_HOOKS = CANNONBALL_EVMAPY

$(eval $(cmake-package))
