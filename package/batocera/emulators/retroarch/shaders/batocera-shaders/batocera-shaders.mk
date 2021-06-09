################################################################################
#
# batocera shaders
#
################################################################################

BATOCERA_SHADERS_VERSION = 1.0
BATOCERA_SHADERS_SOURCE=
BATOCERA_SHADERS_DEPENDENCIES= glsl-shaders

ifeq ($(BR2_PACKAGE_BATOCERA_TARGET_RPI1),y)
	BATOCERA_SHADERS_SYSTEM=rpi1
else ifeq ($(BR2_PACKAGE_BATOCERA_TARGET_RPI2),y)
	BATOCERA_SHADERS_SYSTEM=rpi2
else ifeq ($(BR2_PACKAGE_BATOCERA_TARGET_RPI3),y)
	BATOCERA_SHADERS_SYSTEM=rpi3
else ifeq ($(BR2_PACKAGE_BATOCERA_TARGET_XU4),y)
	BATOCERA_SHADERS_SYSTEM=xu4
else ifeq ($(BR2_PACKAGE_BATOCERA_TARGET_S905GEN3),y)
	BATOCERA_SHADERS_SYSTEM=c4
else ifeq ($(BR2_PACKAGE_BATOCERA_TARGET_S812),y)
	BATOCERA_SHADERS_SYSTEM=s812
else ifeq ($(BR2_PACKAGE_BATOCERA_TARGET_S905),y)
	BATOCERA_SHADERS_SYSTEM=s905
else ifeq ($(BR2_PACKAGE_BATOCERA_TARGET_S912),y)
	BATOCERA_SHADERS_SYSTEM=s912
else ifeq ($(BR2_PACKAGE_BATOCERA_TARGET_X86)$(BR2_PACKAGE_BATOCERA_TARGET_X86_64),y)
	BATOCERA_SHADERS_SYSTEM=x86
else ifeq ($(BR2_PACKAGE_BATOCERA_TARGET_RK3288),y)
	BATOCERA_SHADERS_SYSTEM=rk3288
else ifeq ($(BR2_PACKAGE_BATOCERA_TARGET_RK3399),y)
	BATOCERA_SHADERS_SYSTEM=rk3399
else ifeq ($(BR2_PACKAGE_BATOCERA_TARGET_S922X),y)
	BATOCERA_SHADERS_SYSTEM=odroidn2
else ifeq ($(BR2_PACKAGE_BATOCERA_TARGET_TRITIUM_H5),y)
	BATOCERA_SHADERS_SYSTEM=tritium_h5
else ifeq ($(BR2_PACKAGE_BATOCERA_TARGET_ORANGEPI_PC),y)
	BATOCERA_SHADERS_SYSTEM=orangepi_pc
else ifeq ($(BR2_PACKAGE_BATOCERA_TARGET_CHA),y)
	BATOCERA_SHADERS_SYSTEM=cha
endif

BATOCERA_SHADERS_DIRIN=$(BR2_EXTERNAL_BATOCERA_PATH)/package/batocera/emulators/retroarch/shaders/batocera-shaders/configs

define BATOCERA_SHADERS_INSTALL_TARGET_CMDS
	mkdir -p $(TARGET_DIR)/usr/share/batocera/shaders/configs

	# general
	cp $(BATOCERA_SHADERS_DIRIN)/rendering-defaults.yml           $(TARGET_DIR)/usr/share/batocera/shaders/configs/
	if test -e $(BATOCERA_SHADERS_DIRIN)/rendering-defaults-$(BATOCERA_SHADERS_SYSTEM).yml; then \
		cp $(BATOCERA_SHADERS_DIRIN)/rendering-defaults-$(BATOCERA_SHADERS_SYSTEM).yml $(TARGET_DIR)/usr/share/batocera/shaders/configs/rendering-defaults-arch.yml; \
	fi

	# sets
	for set in retro scanlines enhanced curvature zfast flatten-glow; do \
		mkdir -p $(TARGET_DIR)/usr/share/batocera/shaders/configs/$$set; \
		cp $(BATOCERA_SHADERS_DIRIN)/$$set/rendering-defaults.yml     $(TARGET_DIR)/usr/share/batocera/shaders/configs/$$set/; \
		if test -e $(BATOCERA_SHADERS_DIRIN)/$$set/rendering-defaults-$(BATOCERA_SHADERS_SYSTEM).yml; then \
			cp $(BATOCERA_SHADERS_DIRIN)/$$set/rendering-defaults-$(BATOCERA_SHADERS_SYSTEM).yml $(TARGET_DIR)/usr/share/batocera/shaders/configs/$$set/rendering-defaults-arch.yml; \
		fi \
	done

endef

$(eval $(generic-package))
