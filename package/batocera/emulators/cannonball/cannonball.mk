################################################################################
#
# cannonball
#
################################################################################
# Version.: Commits on Jun 24, 2020
CANNONBALL_VERSION = b6aa525ddd552f96b43b3b3a6f69326a277206bd
CANNONBALL_SITE = $(call github,djyt,cannonball,$(CANNONBALL_VERSION))
CANNONBALL_LICENSE = GPLv2
CANNONBALL_DEPENDENCIES = sdl2 boost

CANNONBALL_TARGET = sdl2gles

ifeq ($(BR2_PACKAGE_BATOCERA_TARGET_RPI4),y)
        CANNONBALL_TARGET = sdl2gles_rpi
else ifeq ($(BR2_PACKAGE_BATOCERA_TARGET_RPI3),y)
        CANNONBALL_TARGET = sdl2gles_rpi
else ifeq ($(BR2_PACKAGE_BATOCERA_TARGET_X86),y)
        CANNONBALL_TARGET = sdl2gl
else ifeq ($(BR2_PACKAGE_BATOCERA_TARGET_X86_64),y)
        CANNONBALL_TARGET = sdl2gl
endif

# Build as release with proper target and paths
CANNONBALL_CONF_OPTS += -DCMAKE_BUILD_TYPE=Release -DTARGET=$(CANNONBALL_TARGET)
CANNONBALL_CONF_OPTS += -Droms_directory=/userdata/roms/cannonball/ -Dxml_directory=/userdata/system/configs/cannonball/ -Dres_directory=/userdata/system/configs/cannonball/


# Cannonball cmake files are hopelessly broken.
# Link libmali manually. Ideally we should fix cannonball to use pkg-config instead.
ifeq ($(BR2_PACKAGE_HAS_LIBMALI),y)
CANNONBALL_EXE_LINKER_FLAGS += -lmali
CANNONBALL_SHARED_LINKER_FLAGS += -lmali
endif

# Enabling LTO as hires mode tends to be slow, it does help video rendering loops
CANNONBALL_EXE_LINKER_FLAGS += -flto
CANNONBALL_SHARED_LINKER_FLAGS += -flto
CANNONBALL_CONF_OPTS += -DCMAKE_CXX_FLAGS=-flto -DCMAKE_EXE_LINKER_FLAGS="$(CANNONBALL_EXE_LINKER_FLAGS)" -DCMAKE_SHARED_LINKER_FLAGS="$(CANNONBALL_SHARED_LINKER_FLAGS)"

# We need to build out-of-tree
CANNONBALL_SUPPORTS_IN_SOURCE_BUILD = NO

define CANNONBALL_SETUP_CMAKE
	cp $(@D)/cmake/* $(@D)/
	$(SED) "s+../res/config+\./res/config+g" $(@D)/CMakeLists.txt
	$(SED) "s+../src/main+\./src/main+g" $(@D)/CMakeLists.txt
	$(SED) "s+../res/tilemap.bin+\./res/tilemap.bin +g" $(@D)/CMakeLists.txt
	$(SED) "s+../res/tilepatch.bin+\./res/tilepatch.bin +g" $(@D)/CMakeLists.txt
        $(SED) "s+/usr+$(STAGING_DIR)/usr+g" $(@D)/CMakeLists.txt
        $(SED) "s+/usr+$(STAGING_DIR)/usr+g" $(@D)/sdl2.cmake
        $(SED) "s+/usr+$(STAGING_DIR)/usr+g" $(@D)/sdl2gl.cmake
        $(SED) "s+/usr+$(STAGING_DIR)/usr+g" $(@D)/sdl2gles.cmake
        $(SED) "s+/usr+$(STAGING_DIR)/usr+g" $(@D)/sdl2gles_rpi.cmake

	# Rpi4 64-bit compilation
	$(SED) "s+-mfpu=neon-fp-armv8++g" $(@D)/sdl2gles_rpi.cmake
	$(SED) "s+-mfloat-abi=hard++g" $(@D)/sdl2gles_rpi.cmake

        #$(SED) "s+set(xml+#set(xml+g" $(@D)/sdl2.cmake
        #$(SED) "s+set(xml+#set(xml+g" $(@D)/sdl2gl.cmake
        #$(SED) "s+set(xml+#set(xml+g" $(@D)/sdl2gles.cmake
        #$(SED) "s+set(xml+#set(xml+g" $(@D)/sdl2gles_rpi.cmake
endef

CANNONBALL_PRE_CONFIGURE_HOOKS += CANNONBALL_SETUP_CMAKE

define CANNONBALL_INSTALL_TARGET_CMDS
	$(INSTALL) -D $(@D)/buildroot-build/cannonball $(TARGET_DIR)/usr/bin/
	mkdir -p $(TARGET_DIR)/usr/share/batocera/datainit/system/configs/cannonball/res/
	$(INSTALL) -D $(@D)/buildroot-build/res/tilemap.bin $(TARGET_DIR)/usr/share/batocera/datainit/system/configs/cannonball/
	$(INSTALL) -D $(@D)/buildroot-build/res/tilepatch.bin $(TARGET_DIR)/usr/share/batocera/datainit/system/configs/cannonball/
	$(INSTALL) -D $(@D)/buildroot-build/config.xml $(TARGET_DIR)/usr/share/batocera/datainit/system/configs/cannonball/config_help.txt
endef

$(eval $(cmake-package))
