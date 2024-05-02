################################################################################
#
# d8vk
#
################################################################################

D8VK_VERSION = d8vk-v1.0
D8VK_SOURCE = $(D8VK_VERSION).tar.gz
D8VK_SITE = https://github.com/AlpyneDreams/d8vk/releases/download/$(D8VK_VERSION)
D8VK_LICENSE = zlib
D8VK_LICENSE_FILES = LICENSE

D8VK_DEPENDENCIES = dxvk

define D8VK_INSTALL_TARGET_CMDS
    mkdir -p $(TARGET_DIR)/usr/wine/dxvk/x32
    cp -af $(@D)/d3d8.dll $(TARGET_DIR)/usr/wine/dxvk/x32
endef

$(eval $(generic-package))
