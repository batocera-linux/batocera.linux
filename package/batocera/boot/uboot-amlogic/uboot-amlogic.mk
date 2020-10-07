################################################################################
#
# U-Boot files for Amlogic Board (Khadas VIM3 and Odroid N2)
#
################################################################################
# Version: Commits on Jul 19, 2020
UBOOT_AMLOGIC_VERSION = 27c705a98e0131384ab3962a6a5ab7ce02aa1109
UBOOT_AMLOGIC_SITE = $(call github,LibreELEC,amlogic-boot-fip,$(UBOOT_AMLOGIC_VERSION))
UBOOT_AMLOGIC_DEPENDS = uboot

UBOOT_AMLOGIC_BUILD_DIR="$(@D)/fip"

ifeq ($(BR2_PACKAGE_BATOCERA_TARGET_S912)$(BR2_PACKAGE_BATOCERA_TARGET_VIM2),y)
UBOOT_AMLOGIC_FIPDIR="$(@D)/khadas-vim2"
UBOOT_AMLOGIC_ENCRYPT_BIN="aml_encrypt_gxl"
endif
ifeq ($(BR2_PACKAGE_BATOCERA_TARGET_VIM3),y)
UBOOT_AMLOGIC_FIPDIR="$(@D)/khadas-vim3"
UBOOT_AMLOGIC_ENCRYPT_BIN="aml_encrypt_g12b"
endif
ifeq ($(BR2_PACKAGE_BATOCERA_TARGET_ODROIDN2),y)
UBOOT_AMLOGIC_FIPDIR="$(@D)/odroid-n2"
UBOOT_AMLOGIC_ENCRYPT_BIN="aml_encrypt_g12b"
endif
ifeq ($(BR2_PACKAGE_BATOCERA_TARGET_ODROIDC4),y)
UBOOT_AMLOGIC_FIPDIR="$(@D)/odroid-c4"
UBOOT_AMLOGIC_ENCRYPT_BIN="aml_encrypt_g12a"
endif

ifeq ($(BR2_PACKAGE_BATOCERA_TARGET_VIM3)$(BR2_PACKAGE_BATOCERA_TARGET_ODROIDN2)$(BR2_PACKAGE_BATOCERA_TARGET_ODROIDC4),y)
define UBOOT_AMLOGIC_BUILD_CMDS
	mkdir -p $(UBOOT_AMLOGIC_BUILD_DIR)

	cp $(UBOOT_AMLOGIC_FIPDIR)/bl301.bin  $(UBOOT_AMLOGIC_BUILD_DIR)
	cp $(UBOOT_AMLOGIC_FIPDIR)/acs.bin    $(UBOOT_AMLOGIC_BUILD_DIR)
	cp $(UBOOT_AMLOGIC_FIPDIR)/bl2.bin    $(UBOOT_AMLOGIC_BUILD_DIR)
	cp $(UBOOT_AMLOGIC_FIPDIR)/bl30.bin   $(UBOOT_AMLOGIC_BUILD_DIR)
	cp $(UBOOT_AMLOGIC_FIPDIR)/bl31.img   $(UBOOT_AMLOGIC_BUILD_DIR)
	cp $(UBOOT_AMLOGIC_FIPDIR)/blx_fix.sh $(UBOOT_AMLOGIC_BUILD_DIR)
	cp $(UBOOT_AMLOGIC_FIPDIR)/*.fw       $(UBOOT_AMLOGIC_BUILD_DIR)
	cp $(BINARIES_DIR)/u-boot.bin         $(UBOOT_AMLOGIC_BUILD_DIR)/bl33.bin

	$(UBOOT_AMLOGIC_FIPDIR)/blx_fix.sh $(UBOOT_AMLOGIC_BUILD_DIR)/bl30.bin \
		$(UBOOT_AMLOGIC_BUILD_DIR)/zero_tmp \
		$(UBOOT_AMLOGIC_BUILD_DIR)/bl30_zero.bin \
		$(UBOOT_AMLOGIC_BUILD_DIR)/bl301.bin \
		$(UBOOT_AMLOGIC_BUILD_DIR)/bl301_zero.bin \
		$(UBOOT_AMLOGIC_BUILD_DIR)/bl30_new.bin bl30

	$(UBOOT_AMLOGIC_FIPDIR)/blx_fix.sh $(UBOOT_AMLOGIC_BUILD_DIR)/bl2.bin \
		$(UBOOT_AMLOGIC_BUILD_DIR)/zero_tmp \
		$(UBOOT_AMLOGIC_BUILD_DIR)/bl2_zero.bin \
		$(UBOOT_AMLOGIC_BUILD_DIR)/acs.bin \
		$(UBOOT_AMLOGIC_BUILD_DIR)/bl21_zero.bin \
		$(UBOOT_AMLOGIC_BUILD_DIR)/bl2_new.bin bl2

	$(UBOOT_AMLOGIC_FIPDIR)/$(UBOOT_AMLOGIC_ENCRYPT_BIN) --bl30sig --input $(UBOOT_AMLOGIC_BUILD_DIR)/bl30_new.bin \
		--output $(UBOOT_AMLOGIC_BUILD_DIR)/bl30_new.bin.g12a.enc \
		--level v3
	$(UBOOT_AMLOGIC_FIPDIR)/$(UBOOT_AMLOGIC_ENCRYPT_BIN) --bl3sig  --input $(UBOOT_AMLOGIC_BUILD_DIR)/bl30_new.bin.g12a.enc \
		--output $(UBOOT_AMLOGIC_BUILD_DIR)/bl30_new.bin.enc \
		--level v3 --type bl30
	$(UBOOT_AMLOGIC_FIPDIR)/$(UBOOT_AMLOGIC_ENCRYPT_BIN) --bl3sig  --input $(UBOOT_AMLOGIC_BUILD_DIR)/bl31.img \
		--output $(UBOOT_AMLOGIC_BUILD_DIR)/bl31.img.enc \
		--level v3 --type bl31
	$(UBOOT_AMLOGIC_FIPDIR)/$(UBOOT_AMLOGIC_ENCRYPT_BIN) --bl3sig  --input $(UBOOT_AMLOGIC_BUILD_DIR)/bl33.bin --compress lz4 \
		--output $(UBOOT_AMLOGIC_BUILD_DIR)/bl33.bin.enc \
		--level v3 --type bl33 --compress lz4
	$(UBOOT_AMLOGIC_FIPDIR)/$(UBOOT_AMLOGIC_ENCRYPT_BIN) --bl2sig  --input $(UBOOT_AMLOGIC_BUILD_DIR)/bl2_new.bin \
		--output $(UBOOT_AMLOGIC_BUILD_DIR)/bl2.n.bin.sig
	$(UBOOT_AMLOGIC_FIPDIR)/$(UBOOT_AMLOGIC_ENCRYPT_BIN) --bootmk \
		 --output $(UBOOT_AMLOGIC_BUILD_DIR)/u-boot.bin \
		 --bl2 $(UBOOT_AMLOGIC_BUILD_DIR)/bl2.n.bin.sig \
		 --bl30 $(UBOOT_AMLOGIC_BUILD_DIR)/bl30_new.bin.enc \
		 --bl31 $(UBOOT_AMLOGIC_BUILD_DIR)/bl31.img.enc \
		 --bl33 $(UBOOT_AMLOGIC_BUILD_DIR)/bl33.bin.enc \
		 --ddrfw1 $(UBOOT_AMLOGIC_BUILD_DIR)/ddr4_1d.fw \
		 --ddrfw2 $(UBOOT_AMLOGIC_BUILD_DIR)/ddr4_2d.fw \
		 --ddrfw3 $(UBOOT_AMLOGIC_BUILD_DIR)/ddr3_1d.fw \
		 --ddrfw4 $(UBOOT_AMLOGIC_BUILD_DIR)/piei.fw \
		 --ddrfw5 $(UBOOT_AMLOGIC_BUILD_DIR)/lpddr4_1d.fw \
		 --ddrfw6 $(UBOOT_AMLOGIC_BUILD_DIR)/lpddr4_2d.fw \
		 --ddrfw7 $(UBOOT_AMLOGIC_BUILD_DIR)/diag_lpddr4.fw \
		 --ddrfw8 $(UBOOT_AMLOGIC_BUILD_DIR)/aml_ddr.fw \
		 --ddrfw9 $(UBOOT_AMLOGIC_BUILD_DIR)/lpddr3_1d.fw \
		 --level v3
endef
endif

ifeq ($(BR2_PACKAGE_BATOCERA_TARGET_S912)$(BR2_PACKAGE_BATOCERA_TARGET_VIM2),y)
define UBOOT_AMLOGIC_BUILD_CMDS
	mkdir -p $(UBOOT_AMLOGIC_BUILD_DIR)

	cp $(UBOOT_AMLOGIC_FIPDIR)/bl2.bin    $(UBOOT_AMLOGIC_BUILD_DIR)
	cp $(UBOOT_AMLOGIC_FIPDIR)/acs.bin    $(UBOOT_AMLOGIC_BUILD_DIR)
	cp $(UBOOT_AMLOGIC_FIPDIR)/bl21.bin   $(UBOOT_AMLOGIC_BUILD_DIR)
	cp $(UBOOT_AMLOGIC_FIPDIR)/bl30.bin   $(UBOOT_AMLOGIC_BUILD_DIR)
	cp $(UBOOT_AMLOGIC_FIPDIR)/bl301.bin  $(UBOOT_AMLOGIC_BUILD_DIR)
	cp $(UBOOT_AMLOGIC_FIPDIR)/bl31.img   $(UBOOT_AMLOGIC_BUILD_DIR)
	cp $(BINARIES_DIR)/u-boot.bin         $(UBOOT_AMLOGIC_BUILD_DIR)/bl33.bin

	$(UBOOT_AMLOGIC_FIPDIR)/blx_fix.sh $(UBOOT_AMLOGIC_BUILD_DIR)/bl30.bin \
		$(UBOOT_AMLOGIC_BUILD_DIR)/zero_tmp \
		$(UBOOT_AMLOGIC_BUILD_DIR)/bl30_zero.bin \
		$(UBOOT_AMLOGIC_BUILD_DIR)/bl301.bin \
		$(UBOOT_AMLOGIC_BUILD_DIR)/bl301_zero.bin \
		$(UBOOT_AMLOGIC_BUILD_DIR)/bl30_new.bin \
		bl30

	$(HOST_DIR)/bin/python $(UBOOT_AMLOGIC_FIPDIR)/acs_tool.py $(UBOOT_AMLOGIC_BUILD_DIR)/bl2.bin \
		$(UBOOT_AMLOGIC_BUILD_DIR)/bl2_acs.bin \
		$(UBOOT_AMLOGIC_BUILD_DIR)/acs.bin \
		0

	$(UBOOT_AMLOGIC_FIPDIR)/blx_fix.sh $(UBOOT_AMLOGIC_BUILD_DIR)/bl2_acs.bin \
		$(UBOOT_AMLOGIC_BUILD_DIR)/zero_tmp \
		$(UBOOT_AMLOGIC_BUILD_DIR)/bl2_zero.bin \
		$(UBOOT_AMLOGIC_BUILD_DIR)/bl21.bin \
		$(UBOOT_AMLOGIC_BUILD_DIR)/bl21_zero.bin \
		$(UBOOT_AMLOGIC_BUILD_DIR)/bl2_new.bin \
		bl2

	$(UBOOT_AMLOGIC_FIPDIR)/$(UBOOT_AMLOGIC_ENCRYPT_BIN) --bl3enc --input $(UBOOT_AMLOGIC_BUILD_DIR)/bl30_new.bin
	$(UBOOT_AMLOGIC_FIPDIR)/$(UBOOT_AMLOGIC_ENCRYPT_BIN) --bl3enc --input $(UBOOT_AMLOGIC_BUILD_DIR)/bl31.img
	$(UBOOT_AMLOGIC_FIPDIR)/$(UBOOT_AMLOGIC_ENCRYPT_BIN) --bl3enc --input $(UBOOT_AMLOGIC_BUILD_DIR)/bl33.bin
	$(UBOOT_AMLOGIC_FIPDIR)/$(UBOOT_AMLOGIC_ENCRYPT_BIN) --bl2sig --input $(UBOOT_AMLOGIC_BUILD_DIR)/bl2_new.bin \
		--output $(UBOOT_AMLOGIC_BUILD_DIR)/bl2.n.bin.sig

	$(UBOOT_AMLOGIC_FIPDIR)/$(UBOOT_AMLOGIC_ENCRYPT_BIN) --bootmk \
		 --output $(UBOOT_AMLOGIC_BUILD_DIR)/u-boot.bin \
		 --bl2 $(UBOOT_AMLOGIC_BUILD_DIR)/bl2.n.bin.sig \
		 --bl30 $(UBOOT_AMLOGIC_BUILD_DIR)/bl30_new.bin.enc \
		 --bl31 $(UBOOT_AMLOGIC_BUILD_DIR)/bl31.img.enc \
		 --bl33 $(UBOOT_AMLOGIC_BUILD_DIR)/bl33.bin.enc
endef
endif

define UBOOT_AMLOGIC_INSTALL_TARGET_CMDS
	cp $(UBOOT_AMLOGIC_BUILD_DIR)/u-boot.bin.sd.bin $(BINARIES_DIR)/u-boot.bin.sd.bin
endef

$(eval $(generic-package))
