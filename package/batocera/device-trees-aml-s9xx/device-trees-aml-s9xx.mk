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
	ifeq ($(BR2_PACKAGE_DEVICE_TREES_AML_S9XX_GXM_KVIM2),y)
		DEVICE_TREES_AML_S9XX_DTS += $(foreach f,$(notdir $(wildcard $(@D)/gxm_kvim2*.dts)),$f)
	endif

	ifeq ($(BR2_PACKAGE_DEVICE_TREES_AML_S9XX_GXM_Q20X)),y)
		DEVICE_TREES_AML_S9XX_DTS += $(foreach f,$(notdir $(wildcard $(@D)/gxm_q20*.dts)),$f)
	endif
endif

ifeq ($(BR2_PACKAGE_RECALBOX_TARGET_S905),y)
	ifeq ($(BR2_PACKAGE_DEVICE_TREES_AML_S9XX_GXBB_P200),y)
		DEVICE_TREES_AML_S9XX_DTS += $(foreach f,$(notdir $(wildcard $(@D)/gxbb_p200*.dts)),$f)
	endif

	ifeq ($(BR2_PACKAGE_DEVICE_TREES_AML_S9XX_GXBB_P201),y)
		DEVICE_TREES_AML_S9XX_DTS += $(foreach f,$(notdir $(wildcard $(@D)/gxbb_p201*.dts)),$f)
	endif

	ifeq ($(BR2_PACKAGE_DEVICE_TREES_AML_S9XX_GXL_P212),y)
		DEVICE_TREES_AML_S9XX_DTS += $(foreach f,$(notdir $(wildcard $(@D)/gxl_p212*.dts)),$f)
	endif

        ifeq ($(BR2_PACKAGE_DEVICE_TREES_AML_S9XX_GXL_P230),y)
                DEVICE_TREES_AML_S9XX_DTS += $(foreach f,$(notdir $(wildcard $(@D)/gxl_p230*.dts)),$f)
        endif

        ifeq ($(BR2_PACKAGE_DEVICE_TREES_AML_S9XX_GXL_P231),y)
                DEVICE_TREES_AML_S9XX_DTS += $(foreach f,$(notdir $(wildcard $(@D)/gxl_p231*.dts)),$f)
        endif

        ifeq ($(BR2_PACKAGE_DEVICE_TREES_AML_S9XX_GXL_P281),y)
                DEVICE_TREES_AML_S9XX_DTS += $(foreach f,$(notdir $(wildcard $(@D)/gxl_p281*.dts)),$f)
        endif
endif

DEVICE_TREES_AML_S9XX_DTS_NAME =$(basename $(DEVICE_TREES_AML_S9XX_DTS))
DEVICE_TREES_AML_S9XX_DTBS = $(addprefix amlogic/, $(addsuffix .dtb,$(DEVICE_TREES_AML_S9XX_DTS_NAME)))

PREPARE_DTS_CMD = \
	for f in $(DEVICE_TREES_AML_S9XX_DTS_NAME) ; do \
                sed -i '/le-dt-id/d' $(@D)/$$f.dts \
                && sed -i '/amlogic-dt-id/d' $(@D)/$$f.dts \
                && echo -e "/ {\n\tamlogic-dt-id = \"$$f\";\n};" >> $(@D)/$$f.dts; \
        done

COPY_DTS_CMD = cp -f $(@D)/* $(DTS_PATH)

BUILD_DTS_CMD = \
	$(MAKE) -C $(LINUX_DIR) ARCH=$(KERNEL_ARCH) \
                CROSS_COMPILE=$(TARGET_CROSS) $(DEVICE_TREES_AML_S9XX_DTBS)

COMBINE_DTS_CMD = \
	$(HOST_DIR)/bin/dtbTool -o $(LINUX_DIR)/arch/$(DEVICE_TREES_AML_S9XX_ARCH)/boot/dts/dtb.img $(DTS_PATH)

define DEVICE_TREES_AML_S9XX_BUILD_CMDS
	${PREPARE_DTS_CMD}
	${COPY_DTS_CMD}
	${BUILD_DTS_CMD}
	${COMBINE_DTS_CMD}
endef

define DEVICE_TREES_AML_S9XX_INSTALL_IMAGES_CMDS
	cp -f $(LINUX_DIR)/arch/$(DEVICE_TREES_AML_S9XX_ARCH)/boot/dts/dtb.img $(BINARIES_DIR);
endef

$(eval $(generic-package))
