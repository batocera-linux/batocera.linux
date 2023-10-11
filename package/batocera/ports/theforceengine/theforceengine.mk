################################################################################
#
# theforceengine
#
################################################################################
# Version: Commits on Oct 8, 2023
THEFORCEENGINE_VERSION = 66a9a979e9749d41a39d76bbac93539654e68233
THEFORCEENGINE_SITE = https://github.com/luciusDXL/TheForceEngine.git
THEFORCEENGINE_SITE_METHOD=git
THEFORCEENGINE_GIT_SUBMODULES=YES
THEFORCEENGINE_LICENSE = GPLv2
THEFORCEENGINE_LICENSE_FILE = LICENSE

# be sure to update configgen if the patch version changes
THEFORCEENGINE_PATCH_VERSION = v3
THEFORCEENGINE_PATCH_SOURCE = $(THEFORCEENGINE_PATCH_VERSION).zip
THEFORCEENGINE_EXTRA_DOWNLOADS = \
    $(addprefix \
    https://df-21.net/downloads/patches/$(THEFORCEENGINE_PATCH_VERSION)/,\
    $(THEFORCEENGINE_PATCH_SOURCE))

THEFORCEENGINE_DEPENDENCIES = libglew sdl2

THEFORCEENGINE_SUPPORTS_IN_SOURCE_BUILD = NO

THEFORCEENGINE_CONF_OPTS += -DCMAKE_BUILD_TYPE=Release
THEFORCEENGINE_CONF_OPTS += -DBUILD_SHARED_LIBS=FALSE
THEFORCEENGINE_CONF_OPTS += -DDISABLE_SYSMIDI=ON

ifeq ($(BR2_PACKAGE_RTMIDI),y)
    THEFORCEENGINE_DEPENDENCIES += rtmidi
    THEFORCEENGINE_CONF_OPTS += -DDISABLE_SYSMIDI=OFF
endif

define THEFORCEENGINE_PATCH_ZIP
    mkdir -p $(TARGET_DIR)/usr/share/TheForceEngine/Mods
    cp $(THEFORCEENGINE_DL_DIR)/$(THEFORCEENGINE_PATCH_SOURCE) \
        $(TARGET_DIR)/usr/share/TheForceEngine/Mods
endef

define THEFORCEENGINE_EVMAPY
    mkdir -p $(TARGET_DIR)/usr/share/evmapy
    cp $(BR2_EXTERNAL_BATOCERA_PATH)/package/batocera/ports/theforceengine/theforceengine.keys \
        $(TARGET_DIR)/usr/share/evmapy
endef

THEFORCEENGINE_POST_INSTALL_TARGET_HOOKS += THEFORCEENGINE_PATCH_ZIP
THEFORCEENGINE_POST_INSTALL_TARGET_HOOKS += THEFORCEENGINE_EVMAPY

$(eval $(cmake-package))
