################################################################################
#
# batocera-nvidia
#
################################################################################

BATOCERA_NVIDIA_VERSION = 1.5
BATOCERA_NVIDIA_SOURCE =

define BATOCERA_NVIDIA_INSTALL_TARGET_CMDS
	mkdir -p $(TARGET_DIR)/usr/bin
	install -m 0755 \
	    $(BR2_EXTERNAL_BATOCERA_PATH)/package/batocera/gpu/batocera-nvidia/batocera-nvidia \
	    $(TARGET_DIR)/usr/bin/

	# [Xorg]
	mkdir -p $(TARGET_DIR)/etc/X11/xorg.conf.d
	ln -sf /userdata/system/99-nvidia.conf \
	    $(TARGET_DIR)/etc/X11/xorg.conf.d/99-nvidia.conf

	# [Blacklist & Modprobe]
	mkdir -p $(TARGET_DIR)/etc/modprobe.d
	ln -sf /var/run/nvidia/modprobe/blacklist-nouveau.conf \
	    $(TARGET_DIR)/etc/modprobe.d/blacklist-nouveau.conf
	ln -sf /var/run/nvidia/modprobe/nvidia-drm.conf \
	    $(TARGET_DIR)/etc/modprobe.d/nvidia-drm.conf
endef

$(eval $(generic-package))
