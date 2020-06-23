################################################################################
#
# rpi-userland-tools
#
################################################################################
# Version.: Commits on May 28, 2020
RPI_USERLAND_TOOLS_VERSION = f97b1af1b3e653f9da2c1a3643479bfd469e3b74
RPI_USERLAND_TOOLS_SITE = $(call github,raspberrypi,userland,$(RPI_USERLAND_TOOLS_VERSION))
RPI_USERLAND_TOOLS_LICENSE = BSD-3-Clause
RPI_USERLAND_TOOLS_LICENSE_FILES = LICENCE

RPI_USERLAND_TOOLS_CONF_OPTS = -DALL_APPS=OFF \
                               -DBUILD_MMAL=OFF \
                               -DBUILD_MMAL_APPS=OFF

define RPI_USERLAND_TOOLS_POST_TARGET_CLEANUP
	rm -Rf $(TARGET_DIR)/usr/src
    rm -Rf $(TARGET_DIR)/opt
endef
RPI_USERLAND_TOOLS_POST_INSTALL_TARGET_HOOKS += RPI_USERLAND_TOOLS_POST_TARGET_CLEANUP

define RPI_USERLAND_TOOLS_INSTALL_TARGET_CMDS
    # Install tvservice
    $(INSTALL) -D $(@D)/build/bin/tvservice       $(TARGET_DIR)/usr/bin/tvservice
    $(INSTALL) -D $(@D)/build/lib/libvchostif.so  $(TARGET_DIR)/usr/lib/libvchostif.so
    $(INSTALL) -D $(@D)/build/lib/libvchiq_arm.so $(TARGET_DIR)/usr/lib/libvchiq_arm.so
    $(INSTALL) -D $(@D)/build/lib/libvcos.so      $(TARGET_DIR)/usr/lib/libvcos.so

    # Install vcgencmd
    $(INSTALL) -D $(@D)/build/bin/vcgencmd        $(TARGET_DIR)/usr/bin/vcgencmd

    # Install dtoverlay
    $(INSTALL) -D $(@D)/build/bin/dtoverlay       $(TARGET_DIR)/usr/bin/dtoverlay
    $(INSTALL) -D $(@D)/build/lib/libdtovl.so     $(TARGET_DIR)/usr/lib/libdtovl.so
    $(INSTALL) -D $(@D)/build/lib/libfdt.so       $(TARGET_DIR)/usr/lib/libfdt.so
endef

$(eval $(cmake-package))
