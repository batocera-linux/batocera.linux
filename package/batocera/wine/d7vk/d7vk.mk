################################################################################
#
# d7vk
#
################################################################################

D7VK_VERSION = 2.2
D7VK_SOURCE = d7vk-v$(D7VK_VERSION).zip
D7VK_SITE = https://github.com/WinterSnowfall/d7vk/releases/download/v$(D7VK_VERSION)
D7VK_LICENSE = zlib/libpng

define D7VK_EXTRACT_CMDS
	mkdir -p $(@D) && cd $(@D) && unzip -x $(DL_DIR)/$(D7VK_DL_SUBDIR)/$(D7VK_SOURCE)
endef

# ddraw is 32bit only, it goes next to the dxvk dlls the wine script already
# knows about
define D7VK_INSTALL_TARGET_CMDS
	mkdir -p $(TARGET_DIR)/usr/wine/dxvk/x32
	cp -p $(@D)/d7vk-v$(D7VK_VERSION)/x32/ddraw.dll $(TARGET_DIR)/usr/wine/dxvk/x32/
endef

$(eval $(generic-package))
