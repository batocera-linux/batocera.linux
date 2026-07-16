# Directories that are included in the rufomaculata squashfs image. These
# are also excluded from the main squashfs image, so that they are only
# included once in batocera. The variable is exported so it can be used in
# post-build-script.sh.
export BATOCERA_RUFOMACULATA_DIRS := \
	usr/lib/libretro \
	usr/wine \
	usr/share/wine \
	usr/share/lr-mame \
	usr/bin/mame \
	usr/bin/sonic3-air \
	usr/pcsx2 \
	usr/xenia

# This variable needs to be here so that `-e ...` is the very last argument
# appended to it
ROOTFS_SQUASHFS_ARGS += -wildcards -e $(BATOCERA_RUFOMACULATA_DIRS)

include $(BR2_EXTERNAL_BATOCERA_PATH)/package/batocera/pkg-boot.mk
include $(BR2_EXTERNAL_BATOCERA_PATH)/package/batocera/pkg-emulator-info.mk
include $(sort $(wildcard $(BR2_EXTERNAL_BATOCERA_PATH)/package/batocera/*/*.mk $(BR2_EXTERNAL_BATOCERA_PATH)/package/batocera/*/*/*.mk $(BR2_EXTERNAL_BATOCERA_PATH)/package/batocera/*/*/*/*.mk $(BR2_EXTERNAL_BATOCERA_PATH)/package/batocera/*/*/*/*/*.mk))

UPDATE_PO_FILES_BUILD_DIR := $(BUILD_DIR)/batocera-locale-update

clean-po-files:
	rm -rf $(UPDATE_PO_FILES_BUILD_DIR)

update-po-files: clean-po-files host-batocera-es-system
	@mkdir -p $(UPDATE_PO_FILES_BUILD_DIR)
	@echo '$(EMULATOR_INFO_PATHS_ALL)' > $(UPDATE_PO_FILES_BUILD_DIR)/info_files.txt

	$(HOST_DIR)/bin/batocera-generate-es-headers \
		--locales-dir=$(BATOCERA_ES_SYSTEM_PKGDIR)/locales \
		--keys-dir=$(BR2_EXTERNAL_BATOCERA_PATH)/package/batocera \
		--output=$(UPDATE_PO_FILES_BUILD_DIR) \
		$(UPDATE_PO_FILES_BUILD_DIR)/info_files.txt

	$(call BATOCERA_ES_SYSTEM_BUILD_PO_FILES,$(UPDATE_PO_FILES_BUILD_DIR),$(BATOCERA_ES_SYSTEM_PKGDIR)/locales)

-include $(BASE_DIR)/.systems_report_targets.mk

SYSTEMS_REPORT_DATADIR := $(BASE_DIR)/data

$(SYSTEMS_REPORT_DATADIR)/%/.config:
	@$(MAKE) O=$(@D) -C $(CANONICAL_CURDIR) BR2_EXTERNAL="$(BR2_EXTERNAL)" batocera-$*_defconfig

$(SYSTEMS_REPORT_DATADIR)/%/info_files.txt:
	@echo "$(TERM_BOLD)>>> Generating system report data for target $(call qstrip,$*)$(TERM_RESET)"
	@mkdir -p $(@D)
	$(MAKE) --no-print-directory -s -C $(SYSTEMS_REPORT_DATADIR)/$* printvars VARS=EMULATOR_INFO_PATHS | sed 's/^EMULATOR_INFO_PATHS=//' > $@

$(SYSTEMS_REPORT_DATADIR)/all_info_files.txt:
	@echo "$(TERM_BOLD)>>> Generating system report data for all targets$(TERM_RESET)"
	@mkdir -p $(@D)
	@echo "$(EMULATOR_INFO_PATHS_ALL)" > $@

ifdef SYSTEMS_REPORT_TARGETS
define inner-systems-report-targets
$(SYSTEMS_REPORT_DATADIR)/$(1)/info_files.txt: $(SYSTEMS_REPORT_DATADIR)/$(1)/.config
systems-report-data: $(SYSTEMS_REPORT_DATADIR)/$(1)/info_files.txt
endef

$(foreach target,$(filter-out x86_wow64,$(SYSTEMS_REPORT_TARGETS)),$(eval $(call inner-systems-report-targets,$(target))))
endif

systems-report-data: $(SYSTEMS_REPORT_DATADIR)/all_info_files.txt

.PHONY: clean-po-files \
	update-po-files \
	systems-report-data
