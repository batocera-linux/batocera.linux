################################################################################
#
# vpinball
#
################################################################################
# Version: Commits on Oct 5, 2023
# uses standalone tree for now
VPINBALL_VERSION = 1b98109e9605cf0f3698cbdab923757f767e478a
VPINBALL_SITE = $(call github,vpinball,vpinball,$(VPINBALL_VERSION))
VPINBALL_LICENSE = GPLv3+
VPINBALL_LICENSE_FILES = LICENSE
VPINBALL_DEPENDENCIES = libfreeimage libpinmame libserum libzedmd sdl2 sdl2_image sdl2_ttf 
VPINBALL_SUPPORTS_IN_SOURCE_BUILD = NO

# handle supported target platforms
ifeq ($(BR2_PACKAGE_BATOCERA_TARGET_RK3588),y)
    SOURCE = CMakeLists_gl-rk3588-aarch64.txt
    SOURCE_DIR = rk3588
    ARCH = aarch64
endif

ifeq ($(BR2_PACKAGE_BATOCERA_TARGET_BCM2711),y)
    SOURCE = CMakeLists_gl-rpi-aarch64.txt
    SOURCE_DIR = rpi
    ARCH = aarch64
endif

ifeq ($(BR2_PACKAGE_BATOCERA_TARGET_X86_64_ANY),y)
    SOURCE = CMakeLists_gl-linux-x64.txt
    SOURCE_DIR = linux
    ARCH = x86_64
endif

define VPINBALL_CMAKE_HACKS
    ## derived from standalone/linux/external.sh ##
    # copy linux x64
    cp $(@D)/standalone/cmake/$(SOURCE) $(@D)/CMakeLists.txt
    $(SED) 's:$${CMAKE_SOURCE_DIR}/standalone/$(SOURCE_DIR)/external/include:$(STAGING_DIR)/usr/include/:g' $(@D)/CMakeLists.txt
    $(SED) 's:$${CMAKE_SOURCE_DIR}/standalone/$(SOURCE_DIR)/external/lib/:$(STAGING_DIR)/usr/lib/:g' $(@D)/CMakeLists.txt
    # make tmp
    rm -rf $(@D)/tmp
    mkdir $(@D)/tmp
    # bass24 - this is ugly...
    cd $(@D)/tmp && $(HOST_DIR)/bin/curl -s https://www.un4seen.com/files/bass24-linux.zip -o bass.zip
    cd $(@D)/tmp && unzip -x bass.zip
    $(INSTALL) -D -m 0755 $(@D)/tmp/libs/$(ARCH)/libbass.so $(STAGING_DIR)/usr/lib
    $(INSTALL) -D -m 0755 $(@D)/tmp/libs/$(ARCH)/libbass.so $(TARGET_DIR)/usr/lib
endef

VPINBALL_CONF_OPTS += -DCMAKE_BUILD_TYPE=Release
VPINBALL_CONF_OPTS += -DBUILD_SHARED_LIBS=OFF

define VPINBALL_INSTALL_TARGET_CMDS
    mkdir -p $(TARGET_DIR)/usr/bin/vpinball
    # install binary
    $(INSTALL) -D -m 0755 $(@D)/buildroot-build/VPinballX_GL \
        $(TARGET_DIR)/usr/bin/vpinball
    # copy folders
    cp -R $(@D)/buildroot-build/flexdmd $(TARGET_DIR)/usr/bin/vpinball/
    cp -R $(@D)/buildroot-build/res $(TARGET_DIR)/usr/bin/vpinball/
    cp -R $(@D)/buildroot-build/scripts $(TARGET_DIR)/usr/bin/vpinball/
    cp -R $(@D)/buildroot-build/shader $(TARGET_DIR)/usr/bin/vpinball/
endef

define VPINBALL_EVMAPY
	mkdir -p $(TARGET_DIR)/usr/share/evmapy
	cp $(BR2_EXTERNAL_BATOCERA_PATH)/package/batocera/emulators/vpinball/vpinball.keys \
	    $(TARGET_DIR)/usr/share/evmapy
endef

VPINBALL_PRE_CONFIGURE_HOOKS += VPINBALL_CMAKE_HACKS

VPINBALL_POST_INSTALL_TARGET_HOOKS += VPINBALL_EVMAPY

$(eval $(cmake-package))
