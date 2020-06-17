################################################################################
#
# cannonball
#
################################################################################
# Version.: Commits on Oct 19, 2019
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

CANNONBALL_CONF_OPTS += -DCMAKE_BUILD_TYPE=Release -DTARGET=$(CANNONBALL_TARGET)

CANNONBALL_SUPPORTS_IN_SOURCE_BUILD = NO

define CANNONBALL_SETUP_CMAKE
	#cd $(@D)
	cp $(@D)/cmake/* $(@D)/
	#mkdir -p $(@D)/buildroot-build
	#cd $(@D)/buildroot-build/
	#cp $(@D)/res/* $(@D)/buildroot-build/res/
	#$(SED) "s+../res+\${CMAKE_CURRENT_BUILD_DIR}/res+g" $(@D)/CMakeLists.txt
	$(SED) "s+../res/config+\./res/config+g" $(@D)/CMakeLists.txt
	$(SED) "s+../src/main+\./src/main+g" $(@D)/CMakeLists.txt
	$(SED) "s+../res/tilemap.bin+\./res/tilemap.bin +g" $(@D)/CMakeLists.txt
	$(SED) "s+../res/tilepatch.bin+\./res/tilepatch.bin +g" $(@D)/CMakeLists.txt
        $(SED) "s+/usr+$(STAGING_DIR)/usr+g" $(@D)/CMakeLists.txt
        $(SED) "s+/usr+$(STAGING_DIR)/usr+g" $(@D)/sdl2.cmake
        $(SED) "s+/usr+$(STAGING_DIR)/usr+g" $(@D)/sdl2gl.cmake
        $(SED) "s+/usr+$(STAGING_DIR)/usr+g" $(@D)/sdl2gles.cmake
        $(SED) "s+/usr+$(STAGING_DIR)/usr+g" $(@D)/sdl2gles_rpi.cmake
endef

CANNONBALL_PRE_CONFIGURE_HOOKS += CANNONBALL_SETUP_CMAKE

define CANNONBALL_INSTALL_TARGET_CMDS
	$(INSTALL) -D $(@D)/buildroot-build/cannonball $(TARGET_DIR)/usr/bin/
	mkdir -p $(TARGET_DIR)/usr/share/cannonball/res/
	$(INSTALL) -D $(@D)/buildroot-build/config.xml $(TARGET_DIR)/usr/share/cannonball/
	$(INSTALL) -D $(@D)/buildroot-build/res/tilemap.bin $(TARGET_DIR)/usr/share/cannonball/res/
	$(INSTALL) -D $(@D)/buildroot-build/res/tilepatch.bin $(TARGET_DIR)/usr/share/cannonball/res/
endef

$(eval $(cmake-package))
