################################################################################
#
# batocera-nvidia
#
################################################################################

BATOCERA_NVIDIA_VERSION = 1
BATOCERA_NVIDIA_LICENCE = GPL
BATOCERA_NVIDIA_SOURCE =

define BATOCERA_NVIDIA_INSTALL_TARGET_CMDS
	# common files => links to /var
	mkdir -p $(TARGET_DIR)/usr/lib
	mkdir -p $(TARGET_DIR)/lib32
	mkdir -p $(TARGET_DIR)/usr/lib/xorg/modules/extensions
	mkdir -p $(TARGET_DIR)/usr/lib/xorg/modules/drivers
	mkdir -p $(TARGET_DIR)/usr/share/vulkan/implicit_layer.d
	mkdir -p $(TARGET_DIR)/usr/share/glvnd/egl_vendor.d
	mkdir -p $(TARGET_DIR)/usr/share/X11/xorg.conf.d
	mkdir -p $(TARGET_DIR)/usr/share/vulkan/icd.d
	#mkdir -p $(TARGET_DIR)/lib/modules/$(BR2_LINUX_KERNEL_VERSION)/extra
	mkdir -p $(TARGET_DIR)/usr/lib/xorg/modules/extensions

	ln -sf /var/run/nvidia/lib/libGLX_nvidia.so         	      $(TARGET_DIR)/usr/lib/libGLX_nvidia.so
	ln -sf /var/run/nvidia/lib/libGLX_nvidia.so.0       	      $(TARGET_DIR)/usr/lib/libGLX_nvidia.so.0
	ln -sf /var/run/nvidia/lib/libEGL_nvidia.so         	      $(TARGET_DIR)/usr/lib/libEGL_nvidia.so
	ln -sf /var/run/nvidia/lib/libEGL_nvidia.so.0       	      $(TARGET_DIR)/usr/lib/libEGL_nvidia.so.0
	ln -sf /var/run/nvidia/lib/libGLESv1_CM_nvidia.so   	      $(TARGET_DIR)/usr/lib/libGLESv1_CM_nvidia.so
	ln -sf /var/run/nvidia/lib/libGLESv1_CM_nvidia.so.1 	      $(TARGET_DIR)/usr/lib/libGLESv1_CM_nvidia.so.1
	ln -sf /var/run/nvidia/lib/libGLESv2_nvidia.so      	      $(TARGET_DIR)/usr/lib/libGLESv2_nvidia.so
	ln -sf /var/run/nvidia/lib/libGLESv2_nvidia.so.2    	      $(TARGET_DIR)/usr/lib/libGLESv2_nvidia.so.2
	ln -sf /var/run/nvidia/lib/libnvidia-eglcore.so     	      $(TARGET_DIR)/usr/lib/libnvidia-eglcore.so
	ln -sf /var/run/nvidia/lib/libnvidia-glcore.so      	      $(TARGET_DIR)/usr/lib/libnvidia-glcore.so
	ln -sf /var/run/nvidia/lib/libnvidia-glsi.so        	      $(TARGET_DIR)/usr/lib/libnvidia-glsi.so
	ln -sf /var/run/nvidia/lib/libnvidia-tls.so         	      $(TARGET_DIR)/usr/lib/libnvidia-tls.so
	ln -sf /var/run/nvidia/lib/libvdpau_nvidia.so       	      $(TARGET_DIR)/usr/lib/libvdpau_nvidia.so
	ln -sf /var/run/nvidia/lib/libvdpau_nvidia.so.1     	      $(TARGET_DIR)/usr/lib/libvdpau_nvidia.so.1
	ln -sf /var/run/nvidia/lib/libnvidia-ml.so          	      $(TARGET_DIR)/usr/lib/libnvidia-ml.so
	ln -sf /var/run/nvidia/lib/libnvidia-ml.so.1        	      $(TARGET_DIR)/usr/lib/libnvidia-ml.so.1
	ln -sf /var/run/nvidia/lib/libnvidia-glvkspirv.so   	      $(TARGET_DIR)/usr/lib/libnvidia-glvkspirv.so

	ln -sf /var/run/nvidia/lib32/libGLX_nvidia.so         	      $(TARGET_DIR)/lib32/libGLX_nvidia.so
	ln -sf /var/run/nvidia/lib32/libGLX_nvidia.so.0       	      $(TARGET_DIR)/lib32/libGLX_nvidia.so.0
	ln -sf /var/run/nvidia/lib32/libEGL_nvidia.so         	      $(TARGET_DIR)/lib32/libEGL_nvidia.so
	ln -sf /var/run/nvidia/lib32/libEGL_nvidia.so.0       	      $(TARGET_DIR)/lib32/libEGL_nvidia.so.0
	ln -sf /var/run/nvidia/lib32/libGLESv1_CM_nvidia.so   	      $(TARGET_DIR)/lib32/libGLESv1_CM_nvidia.so
	ln -sf /var/run/nvidia/lib32/libGLESv1_CM_nvidia.so.1 	      $(TARGET_DIR)/lib32/libGLESv1_CM_nvidia.so.1
	ln -sf /var/run/nvidia/lib32/libGLESv2_nvidia.so      	      $(TARGET_DIR)/lib32/libGLESv2_nvidia.so
	ln -sf /var/run/nvidia/lib32/libGLESv2_nvidia.so.2    	      $(TARGET_DIR)/lib32/libGLESv2_nvidia.so.2
	ln -sf /var/run/nvidia/lib32/libnvidia-eglcore.so     	      $(TARGET_DIR)/lib32/libnvidia-eglcore.so
	ln -sf /var/run/nvidia/lib32/libnvidia-glcore.so      	      $(TARGET_DIR)/lib32/libnvidia-glcore.so
	ln -sf /var/run/nvidia/lib32/libnvidia-glsi.so        	      $(TARGET_DIR)/lib32/libnvidia-glsi.so
	ln -sf /var/run/nvidia/lib32/libnvidia-tls.so         	      $(TARGET_DIR)/lib32/libnvidia-tls.so
	ln -sf /var/run/nvidia/lib32/libvdpau_nvidia.so       	      $(TARGET_DIR)/lib32/libvdpau_nvidia.so
	ln -sf /var/run/nvidia/lib32/libvdpau_nvidia.so.1     	      $(TARGET_DIR)/lib32/libvdpau_nvidia.so.1
	ln -sf /var/run/nvidia/lib32/libnvidia-ml.so          	      $(TARGET_DIR)/lib32/libnvidia-ml.so
	ln -sf /var/run/nvidia/lib32/libnvidia-ml.so.1        	      $(TARGET_DIR)/lib32/libnvidia-ml.so.1
	ln -sf /var/run/nvidia/lib32/libnvidia-glvkspirv.so   	      $(TARGET_DIR)/lib32/libnvidia-glvkspirv.so

	ln -sf /var/run/nvidia/lib/libglxserver_nvidia.so   	      $(TARGET_DIR)/usr/lib/xorg/modules/extensions/libglxserver_nvidia.so
	ln -sf /var/run/nvidia/lib/libglxserver_nvidia.so.1 	      $(TARGET_DIR)/usr/lib/xorg/modules/extensions/libglxserver_nvidia.so.1
	ln -sf /var/run/nvidia/lib/nvidia_drv.so            	      $(TARGET_DIR)/usr/lib/xorg/modules/drivers/nvidia_drv.so

	ln -sf /var/run/nvidia/configs/nvidia_layers.json             $(TARGET_DIR)/usr/share/vulkan/implicit_layer.d/nvidia_layers.json
	ln -sf /var/run/nvidia/configs/10_nvidia.json                 $(TARGET_DIR)/usr/share/glvnd/egl_vendor.d/10_nvidia.json
	ln -sf /var/run/nvidia/configs/10-nvidia-drm-outputclass.conf $(TARGET_DIR)/usr/share/X11/xorg.conf.d/10-nvidia-drm-outputclass.conf

	ln -sf /var/run/nvidia/configs/nvidia_icd.x86_64.json 	      $(TARGET_DIR)/usr/share/vulkan/icd.d/nvidia_icd.x86_64.json
	ln -sf /var/run/nvidia/configs/nvidia_icd.i686.json   	      $(TARGET_DIR)/usr/share/vulkan/icd.d/nvidia_icd.i686.json

	#ln -sf /var/run/nvidia/modules/nvidia.ko         	      $(TARGET_DIR)/lib/modules/$(BR2_LINUX_KERNEL_VERSION)/extra/nvidia.ko
	#ln -sf /var/run/nvidia/modules/nvidia-modeset.ko 	      $(TARGET_DIR)/lib/modules/$(BR2_LINUX_KERNEL_VERSION)/extra/nvidia-modeset.ko
	#ln -sf /var/run/nvidia/modules/nvidia-drm.ko     	      $(TARGET_DIR)/lib/modules/$(BR2_LINUX_KERNEL_VERSION)/extra/nvidia-drm.ko
	#ln -sf /var/run/nvidia/modules/nvidia-uvm.ko     	      $(TARGET_DIR)/lib/modules/$(BR2_LINUX_KERNEL_VERSION)/extra/nvidia-uvm.ko

	# for driver 390
	ln -sf /var/run/nvidia/xorg/libglx.so $(TARGET_DIR)/usr/lib/xorg/modules/extensions/libglx.so

	# switcher
	mkdir -p $(TARGET_DIR)/usr/bin
	install -m 0755 $(BR2_EXTERNAL_BATOCERA_PATH)/package/batocera/gpu/batocera-nvidia/batocera-nvidia $(TARGET_DIR)/usr/bin/

	# xorg
	mkdir -p $(TARGET_DIR)/etc/X11/xorg.conf.d
	ln -fs /userdata/system/99-nvidia.conf $(TARGET_DIR)/etc/X11/xorg.conf.d/99-nvidia.conf

	# modprobe
	ln -sf /var/run/nvidia/modprobe/blacklist-nouveau.conf $(TARGET_DIR)/etc/modprobe.d/blacklist-nouveau.conf
	ln -sf /var/run/nvidia/modprobe/nvidia-drm.conf        $(TARGET_DIR)/etc/modprobe.d/nvidia-drm.conf
endef

$(eval $(generic-package))
