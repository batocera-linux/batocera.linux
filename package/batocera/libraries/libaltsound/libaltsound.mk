################################################################################
#
# libaltsound
#
################################################################################
# Version: Commits on Jul 2, 2024
LIBALTSOUND_VERSION = b8f397858cbc7a879f7392c14a509f00c8bdc7dd
LIBALTSOUND_SITE = $(call github,vpinball,libaltsound,$(LIBALTSOUND_VERSION))
LIBALTSOUND_LICENSE = BSD-3-Clause
LIBALTSOUND_LICENSE_FILES = LICENSE
LIBALTSOUND_DEPENDENCIES = host-libcurl
LIBALTSOUND_SUPPORTS_IN_SOURCE_BUILD = NO

LIBALTSOUND_CONF_OPTS += -DCMAKE_BUILD_TYPE=Release
LIBALTSOUND_CONF_OPTS += -DBUILD_STATIC=OFF
LIBALTSOUND_CONF_OPTS += -DPLATFORM=linux
LIBALTSOUND_CONF_OPTS += -DARCH=$(BUILD_ARCH)

# handle supported target platforms
ifeq ($(BR2_PACKAGE_BATOCERA_TARGET_RK3588),y)
    BUILD_ARCH = aarch64
    BASS_ARCH = aarch64
endif

ifeq ($(BR2_PACKAGE_BATOCERA_TARGET_BCM2711)$(BR2_PACKAGE_BATOCERA_TARGET_BCM2712),y)
    BUILD_ARCH = aarch64
    BASS_ARCH = aarch64
endif

ifeq ($(BR2_PACKAGE_BATOCERA_TARGET_X86_64_ANY),y)
    BUILD_ARCH = x64
    BASS_ARCH = x86_64
endif

define LIBALTSOUND_BASS_HACKS
    ## derived from platforms/linux/$(BUILD_ARCH)/external.sh ##
    # make tmp
    rm -rf $(@D)/tmp
    mkdir $(@D)/tmp
    # bass24 - this is ugly...
    cd $(@D)/tmp && $(HOST_DIR)/bin/curl -s \
        https://www.un4seen.com/files/bass24-linux.zip -o bass.zip
    cd $(@D)/tmp && unzip -x bass.zip
    cp $(@D)/tmp/bass.h $(@D)/third-party/include
    cp $(@D)/tmp/libs/$(BASS_ARCH)/libbass.so \
        $(@D)/third-party/runtime-libs/linux/$(BUILD_ARCH)
endef

# Install to staging to build Visual Pinball Standalone
LIBALTSOUND_INSTALL_STAGING = YES

LIBALTSOUND_PRE_CONFIGURE_HOOKS += LIBALTSOUND_BASS_HACKS

$(eval $(cmake-package))
