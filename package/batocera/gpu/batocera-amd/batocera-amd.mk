################################################################################
#
# batocera-amd
#
################################################################################

BATOCERA_AMD_VERSION = 1.0
BATOCERA_AMD_SOURCE =

define BATOCERA_AMD_INSTALL_TARGET_CMDS
	install -m 0755 $(BR2_EXTERNAL_BATOCERA_PATH)/package/batocera/gpu/batocera-amd/S05amd-check \
	    $(TARGET_DIR)/etc/init.d/S05amd-check
	# List
	mkdir -p $(TARGET_DIR)/usr/share/amd
	install -m 0644 $(BR2_EXTERNAL_BATOCERA_PATH)/package/batocera/gpu/batocera-amd/islands.list \
	    $(TARGET_DIR)/usr/share/amd
	# Modules
	ln -sf /var/run/amd/modprobe/amdgpu.conf $(TARGET_DIR)/etc/modprobe.d/amdgpu.conf
	ln -sf /var/run/amd/modprobe/radeon.conf $(TARGET_DIR)/etc/modprobe.d/radeon.conf
endef

$(eval $(generic-package))
