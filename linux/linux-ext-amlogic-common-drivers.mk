ifeq ($(BR2_PACKAGE_AMLOGIC_COMMON_DRIVERS),y)

LINUX_DEPENDENCIES += amlogic-common-drivers

define AMLOGIC_COMMON_DRIVERS_PREPARE_KERNEL
	@$(call MESSAGE,"Injecting Amlogic common drivers into kernel tree")
	rm -rf $(@D)/common_drivers
	cp -r $(AMLOGIC_COMMON_DRIVERS_DIR) $(LINUX_DIR)/common_drivers
endef
LINUX_POST_EXTRACT_HOOKS += AMLOGIC_COMMON_DRIVERS_PREPARE_KERNEL

endif
