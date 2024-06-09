################################################################################
#
# r8168
#
################################################################################
# Version: 8.053.00
R8168_VERSION = 503086686ea7b08b8b9b323ab52991987dfd9f6a
R8168_SITE = $(call github,mtorromeo,r8168,$(R8168_VERSION))
R8168_LICENSE = GPL-2.0
R8168_LICENSE_FILES = LICENSE
R8168_MODULE_SUBDIRS = src

R8168_MODULE_MAKE_OPTS += ENABLE_USE_FIRMWARE_FILE=y
R8168_MODULE_MAKE_OPTS += CONFIG_R8168_NAPI=y
R8168_MODULE_MAKE_OPTS += CONFIG_R8168_VLAN=y
R8168_MODULE_MAKE_OPTS += CONFIG_ASPM=y
R8168_MODULE_MAKE_OPTS += ENABLE_S5WOL=y
R8168_MODULE_MAKE_OPTS += ENABLE_EEE=y
R8168_MODULE_MAKE_OPTS += \
    USER_EXTRA_CFLAGS="-DCONFIG_$(call qstrip,$(BR2_ENDIAN))_ENDIAN -Wno-error"

define R8168_MAKE_SUBDIR
    (cd $(@D)/src; ln -s . r8168)
endef

define R8168_BLACKLIST_R8168
    cp $(BR2_EXTERNAL_BATOCERA_PATH)/package/batocera/network/r8168/r816x.conf \
        $(TARGET_DIR)/etc/modprobe.d/
endef

R8168_PRE_CONFIGURE_HOOKS += R8168_MAKE_SUBDIR
R8168_POST_INSTALL_TARGET_HOOKS += R8168_BLACKLIST_R8168

$(eval $(kernel-module))
$(eval $(generic-package))
