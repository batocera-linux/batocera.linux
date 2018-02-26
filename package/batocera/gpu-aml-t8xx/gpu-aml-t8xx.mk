################################################################################
#
# amlogic t8xx gpu driver
#
################################################################################
LINUX_VERSION_PROBED = `$(MAKE) $(LINUX_MAKE_FLAGS) -C $(LINUX_DIR) --no-print-directory -s kernelrelease 2>/dev/null`
GPU_AML_T8XX_VERSION = fe7a4d8
GPU_AML_T8XX_SITE    = https://github.com/khadas/android_hardware_arm_gpu/archive
GPU_AML_T8XX_SOURCE  = $(GPU_AML_T8XX_VERSION).tar.gz
GPU_AML_T8XX_MODULE_DIR = kernel/amlogic/gpu
GPU_AML_T8XX_INSTALL_DIR = $(TARGET_DIR)/lib/modules/$(LINUX_VERSION_PROBED)/$(GPU_AML_T8XX_MODULE_DIR)
GPU_AML_T8XX_DEPENDENCIES = linux

MALI_T8XX_BUILD_CMD = \
	$(TARGET_CONFIGURE_OPTS) $(MAKE) -C $(LINUX_DIR) M=$(@D)/t83x/kernel/drivers/gpu/arm/midgard \
	ARCH=$(KERNEL_ARCH) CROSS_COMPILE=$(TARGET_CROSS) \
	CONFIG_MALI_MIDGARD=m CONFIG_MALI_PLATFORM_DEVICETREE=y CONFIG_MALI_MIDGARD_DVFS=y CONFIG_MALI_BACKEND=gpu \
	EXTRA_CFLAGS="-DCONFIG_MALI_PLATFORM_DEVICETREE -DCONFIG_MALI_MIDGARD_DVFS -DCONFIG_MALI_BACKEND=gpu" modules

MALI_T8XX_INSTALL_TARGETS_CMDS = \
	$(INSTALL) -m 0666 $(@D)/t83x/kernel/drivers/gpu/arm/midgard/mali_kbase.ko $(GPU_AML_T8XX_INSTALL_DIR); \
	echo $(GPU_AML_T8XX_MODULE_DIR)/mali_kbase.ko: >> $(TARGET_DIR)/lib/modules/$(LINUX_VERSION_PROBED)/modules.dep;

define GPU_AML_T8XX_BUILD_CMDS
	$(MALI_T8XX_BUILD_CMD)
endef

define GPU_AML_T8XX_INSTALL_TARGET_CMDS
	mkdir -p $(GPU_AML_T8XX_INSTALL_DIR);
	$(MALI_T8XX_INSTALL_TARGETS_CMDS)
endef

$(eval $(generic-package))

