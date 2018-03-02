################################################################################
#
# device-trees-aml-s9xx
#
################################################################################
DEVICE_TREES_AML_S9XX_VERSION = master
DEVICE_TREES_AML_S9XX_SITE = $(call github,suzuke,device-trees-amlogic,$(DEVICE_TREES_AML_S9XX_VERSION))

DEVICE_TREES_AML_S9XX_DEPENDENCIES = linux host-aml-dtbtools
DEVICE_TREES_AML_S9XX_INSTALL_IMAGES = YES

DEVICE_TREES_AML_S9XX_ARCH = ${ARCH}
ifeq ($(BR2_aarch64),y)
        DEVICE_TREES_AML_S9XX_ARCH = arm64
endif

ifeq ($(BR2_arm),y)
        DEVICE_TREES_AML_S9XX_ARCH = arm
endif

DTS_PATH = $(LINUX_DIR)/arch/$(DEVICE_TREES_AML_S9XX_ARCH)/boot/dts/amlogic/

ifeq ($(BR2_PACKAGE_RECALBOX_TARGET_S912),y)
	DEVICE_TREES_AML_S9XX_DTS += $(foreach f,$(notdir $(wildcard $(@D)/gxm*.dts)),$f)
endif

ifeq ($(BR2_PACKAGE_RECALBOX_TARGET_S905),y)
	DEVICE_TREES_AML_S9XX_DTS += $(foreach f,$(notdir $(wildcard $(@D)/gxbb*.dts)),$f)
	DEVICE_TREES_AML_S9XX_DTS += $(foreach f,$(notdir $(wildcard $(@D)/gxl*.dts)),$f)
endif

DEVICE_TREES_AML_S9XX_DTS_NAME =$(basename $(DEVICE_TREES_AML_S9XX_DTS))
DEVICE_TREES_AML_S9XX_DTBS = $(addprefix amlogic/, $(addsuffix .dtb,$(DEVICE_TREES_AML_S9XX_DTS_NAME)))

define DEVICE_TREES_AML_S9XX_BUILD_CMDS
	for f in $(DEVICE_TREES_AML_S9XX_DTS_NAME) ; do \
		sed -i '/le-dt-id/d' $(@D)/$$f.dts; \
		sed -i '/amlogic-dt-id/d' $(@D)/$$f.dts; \
		echo -e "/ {\n\tamlogic-dt-id = \"$$f\";\n};" >> $(@D)/$$f.dts; \
	done
	cp -f $(@D)/* $(DTS_PATH); \
	$(MAKE) -C $(LINUX_DIR) ARCH=$(KERNEL_ARCH) \
                CROSS_COMPILE=$(TARGET_CROSS) $(DEVICE_TREES_AML_S9XX_DTBS) ; \
	$(HOST_DIR)/bin/dtbTool -o $(LINUX_DIR)/arch/$(DEVICE_TREES_AML_S9XX_ARCH)/boot/dts/dtb.img $(DTS_PATH);
endef

define DEVICE_TREES_AML_S9XX_INSTALL_IMAGES_CMDS
	cp -f $(LINUX_DIR)/arch/$(DEVICE_TREES_AML_S9XX_ARCH)/boot/dts/dtb.img $(BINARIES_DIR);
endef

#define DEVICE_TREES_AML_S9XX_INSTALL_IMAGES_CMDS
#	for f in $(DEVICE_TREES_AML_S9XX_DTBS) ; do \
#		cp -f $(LINUX_DIR)/arch/$(DEVICE_TREES_AML_S9XX_ARCH)/boot/dts/$$f $(BINARIES_DIR); \
#	done
#endef

$(eval $(generic-package))
