################################################################################
#
# U-Boot files for Khadas VIM3
#
################################################################################
# Version: Commits on Dec 29, 2019
UBOOT_VIM3_VERSION = bfdad4cc520b254813536ebfba8b9749386cd57c
UBOOT_VIM3_SITE = $(call github,LibreELEC,amlogic-boot-fip,$(UBOOT_VIM3_VERSION))
UBOOT_VIM3_DEPENDS = uboot

UBOOT_VIM3_AML_ENCRYPT_BIN="aml_encrypt_g12b"
UBOOT_VIM3_BUILD_DIR="$(@D)/fip"
UBOOT_VIM3_FIPDIR="$(@D)/khadas-vim3"

define UBOOT_VIM3_BUILD_CMDS
	mkdir -p $(UBOOT_VIM3_BUILD_DIR)

	cp $(UBOOT_VIM3_FIPDIR)/bl301.bin $(UBOOT_VIM3_BUILD_DIR)/
	cp $(UBOOT_VIM3_FIPDIR)/acs.bin $(UBOOT_VIM3_BUILD_DIR)/
	cp $(UBOOT_VIM3_FIPDIR)/aml_ddr.fw $(UBOOT_VIM3_BUILD_DIR)/
	cp $(UBOOT_VIM3_FIPDIR)/bl2.bin $(UBOOT_VIM3_BUILD_DIR)/
	cp $(UBOOT_VIM3_FIPDIR)/bl30.bin $(UBOOT_VIM3_BUILD_DIR)/
	cp $(UBOOT_VIM3_FIPDIR)/bl31.img $(UBOOT_VIM3_BUILD_DIR)/
	cp $(UBOOT_VIM3_FIPDIR)/blx_fix.sh $(UBOOT_VIM3_BUILD_DIR)/
	cp $(UBOOT_VIM3_FIPDIR)/ddr3_1d.fw $(UBOOT_VIM3_BUILD_DIR)/
	cp $(UBOOT_VIM3_FIPDIR)/ddr4_1d.fw $(UBOOT_VIM3_BUILD_DIR)/
	cp $(UBOOT_VIM3_FIPDIR)/ddr4_2d.fw $(UBOOT_VIM3_BUILD_DIR)/
	cp $(UBOOT_VIM3_FIPDIR)/diag_lpddr4.fw $(UBOOT_VIM3_BUILD_DIR)/
	cp $(UBOOT_VIM3_FIPDIR)/lpddr3_1d.fw $(UBOOT_VIM3_BUILD_DIR)/
	cp $(UBOOT_VIM3_FIPDIR)/lpddr4_1d.fw $(UBOOT_VIM3_BUILD_DIR)/
	cp $(UBOOT_VIM3_FIPDIR)/lpddr4_2d.fw $(UBOOT_VIM3_BUILD_DIR)/
	cp $(UBOOT_VIM3_FIPDIR)/piei.fw $(UBOOT_VIM3_BUILD_DIR)/
	cp $(BINARIES_DIR)/u-boot.bin $(UBOOT_VIM3_BUILD_DIR)/bl33.bin

	$(UBOOT_VIM3_FIPDIR)/blx_fix.sh $(UBOOT_VIM3_BUILD_DIR)/bl30.bin \
		$(UBOOT_VIM3_BUILD_DIR)/zero_tmp \
		$(UBOOT_VIM3_BUILD_DIR)/bl30_zero.bin \
		$(UBOOT_VIM3_BUILD_DIR)/bl301.bin \
		$(UBOOT_VIM3_BUILD_DIR)/bl301_zero.bin \
		$(UBOOT_VIM3_BUILD_DIR)/bl30_new.bin bl30

	$(UBOOT_VIM3_FIPDIR)/blx_fix.sh $(UBOOT_VIM3_BUILD_DIR)/bl2.bin \
		$(UBOOT_VIM3_BUILD_DIR)/zero_tmp \
		$(UBOOT_VIM3_BUILD_DIR)/bl2_zero.bin \
		$(UBOOT_VIM3_BUILD_DIR)/acs.bin \
		$(UBOOT_VIM3_BUILD_DIR)/bl21_zero.bin \
		$(UBOOT_VIM3_BUILD_DIR)/bl2_new.bin bl2

	$(UBOOT_VIM3_FIPDIR)/$(UBOOT_VIM3_AML_ENCRYPT_BIN) --bl30sig --input $(UBOOT_VIM3_BUILD_DIR)/bl30_new.bin \
		--output $(UBOOT_VIM3_BUILD_DIR)/bl30_new.bin.g12a.enc \
		--level v3
	$(UBOOT_VIM3_FIPDIR)/$(UBOOT_VIM3_AML_ENCRYPT_BIN) --bl3sig  --input $(UBOOT_VIM3_BUILD_DIR)/bl30_new.bin.g12a.enc \
		--output $(UBOOT_VIM3_BUILD_DIR)/bl30_new.bin.enc \
		--level v3 --type bl30
	$(UBOOT_VIM3_FIPDIR)/$(UBOOT_VIM3_AML_ENCRYPT_BIN) --bl3sig  --input $(UBOOT_VIM3_BUILD_DIR)/bl31.img \
		--output $(UBOOT_VIM3_BUILD_DIR)/bl31.img.enc \
		--level v3 --type bl31
	$(UBOOT_VIM3_FIPDIR)/$(UBOOT_VIM3_AML_ENCRYPT_BIN) --bl3sig  --input $(UBOOT_VIM3_BUILD_DIR)/bl33.bin --compress lz4 \
		--output $(UBOOT_VIM3_BUILD_DIR)/bl33.bin.enc \
		--level v3 --type bl33 --compress lz4
	$(UBOOT_VIM3_FIPDIR)/$(UBOOT_VIM3_AML_ENCRYPT_BIN) --bl2sig  --input $(UBOOT_VIM3_BUILD_DIR)/bl2_new.bin \
		--output $(UBOOT_VIM3_BUILD_DIR)/bl2.n.bin.sig
	$(UBOOT_VIM3_FIPDIR)/$(UBOOT_VIM3_AML_ENCRYPT_BIN) --bootmk \
		 --output $(UBOOT_VIM3_BUILD_DIR)/u-boot.bin \
		 --bl2 $(UBOOT_VIM3_BUILD_DIR)/bl2.n.bin.sig \
		 --bl30 $(UBOOT_VIM3_BUILD_DIR)/bl30_new.bin.enc \
		 --bl31 $(UBOOT_VIM3_BUILD_DIR)/bl31.img.enc \
		 --bl33 $(UBOOT_VIM3_BUILD_DIR)/bl33.bin.enc \
		 --ddrfw1 $(UBOOT_VIM3_BUILD_DIR)/ddr4_1d.fw \
		 --ddrfw2 $(UBOOT_VIM3_BUILD_DIR)/ddr4_2d.fw \
		 --ddrfw3 $(UBOOT_VIM3_BUILD_DIR)/ddr3_1d.fw \
		 --ddrfw4 $(UBOOT_VIM3_BUILD_DIR)/piei.fw \
		 --ddrfw5 $(UBOOT_VIM3_BUILD_DIR)/lpddr4_1d.fw \
		 --ddrfw6 $(UBOOT_VIM3_BUILD_DIR)/lpddr4_2d.fw \
		 --ddrfw7 $(UBOOT_VIM3_BUILD_DIR)/diag_lpddr4.fw \
		 --ddrfw8 $(UBOOT_VIM3_BUILD_DIR)/aml_ddr.fw \
		 --ddrfw9 $(UBOOT_VIM3_BUILD_DIR)/lpddr3_1d.fw \
		 --level v3
endef

define UBOOT_VIM3_INSTALL_TARGET_CMDS
	cp $(UBOOT_VIM3_BUILD_DIR)/u-boot.bin.sd.bin $(BINARIES_DIR)/u-boot.bin.sd.bin
endef

$(eval $(generic-package))
