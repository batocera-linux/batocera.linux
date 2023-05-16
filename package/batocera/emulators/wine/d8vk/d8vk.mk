################################################################################
#
# d8vk
#
################################################################################

D8VK_VERSION = 1.0
D8VK_SOURCE = d8vk-v$(D8VK_VERSION).tar.gz
D8VK_SITE = https://github.com/AlpyneDreams/d8vk/releases/download/d8vk-v$(D8VK_VERSION)
D8VK_LICENSE = zlib
D8VK_LICENSE_FILES = LICENSE
D8VK_DEPENDENCIES = dxvk

define D8VK_EXTRACT_CMDS
	mkdir -p $(@D)/target && cd $(@D)/target && tar xf $(DL_DIR)/$(D8VK_DL_SUBDIR)/$(D8VK_SOURCE)
endef

define D8VK_INSTALL_TARGET_CMDS
    mkdir -p $(TARGET_DIR)/usr/wine/dxvk
    cp -pr $(@D)/target/d8vk-v$(D8VK_VERSION)/x32 $(TARGET_DIR)/usr/wine/dxvk/
endef

$(eval $(generic-package))
