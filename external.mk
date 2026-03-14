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

SYSTEMS_REPORT_TMPDIR := /tmp/systems-report
SYSTEMS_REPORT_DIR := $(BASE_DIR)/systems-report

$(SYSTEMS_REPORT_TMPDIR)/%/.config:
	@$(MAKE) O=$(@D) -C $(CANONICAL_CURDIR) BR2_EXTERNAL="$(BR2_EXTERNAL)" batocera-$*_defconfig

$(SYSTEMS_REPORT_TMPDIR)/%/info_files.txt:
	@echo "$(TERM_BOLD)>>> Generating system report data for target $(call qstrip,$*)$(TERM_RESET)"
	@mkdir -p $(@D)
	$(MAKE) --no-print-directory -s -C $(SYSTEMS_REPORT_TMPDIR)/$* printvars VARS=EMULATOR_INFO_PATHS | sed 's/^EMULATOR_INFO_PATHS=//' > $@

ifdef SYSTEMS_REPORT_TARGETS
define inner-systems-report-targets
$(SYSTEMS_REPORT_TMPDIR)/$(1)/info_files.txt: $(SYSTEMS_REPORT_TMPDIR)/$(1)/.config
systems-report: $(SYSTEMS_REPORT_TMPDIR)/$(1)/info_files.txt
endef

$(foreach target,$(filter-out x86_wow64,$(SYSTEMS_REPORT_TARGETS)),$(eval $(call inner-systems-report-targets,$(target))))
endif

systems-report: host-batocera-es-system
ifdef SYSTEMS_REPORT_TARGETS
	@mkdir -p $(SYSTEMS_REPORT_DIR)
	@echo "$(EMULATOR_INFO_PATHS_ALL)" > $(SYSTEMS_REPORT_TMPDIR)/all_info_files.txt

	$(HOST_DIR)/bin/batocera-systems-report \
		$(SYSTEMS_REPORT_TMPDIR) \
		$(BATOCERA_ES_SYSTEM_PKGDIR)/es_systems.yml \
		$(BATOCERA_ES_SYSTEM_PKGDIR)/systems-explanations.yml \
		$(BATOCERA_CONFIGGEN_PKGDIR)/configs \
		$(SYSTEMS_REPORT_DIR)/batocera_systemsReport.json

	cp $(BATOCERA_ES_SYSTEM_PKGDIR)/batocera_systemsReport.html $(SYSTEMS_REPORT_DIR)
else
	@$(error "No SYSTEMS_REPORT_TARGETS defined!")
endif

.PHONY: clean-po-files \
	update-po-files \
	systems-report
