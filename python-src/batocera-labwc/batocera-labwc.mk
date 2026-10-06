################################################################################
#
# batocera-labwc
#
################################################################################
BATOCERA_LABWC_SETUP_TYPE=hatch
BATOCERA_LABWC_DEPENDENCIES=host-batocera-labwc python-batocera-common
# build_rule_sets.py is only needed in the host package to build the .labwc-rules.yml files
BATOCERA_LABWC_LOCAL_PYTHON_EXCLUSIONS=batocera_labwc/build_rule_sets.py

HOST_BATOCERA_LABWC_DEPENDENCIES=host-python-batocera-common

define BATOCERA_LABWC_BUILD_RULE_SETS
	@echo '$(EMULATOR_INFO_PATHS)' > $(BATOCERA_LABWC_DIR)/info_files.txt

	mkdir -p $(TARGET_DIR)/usr/share/batocera/labwc
	$(HOST_DIR)/bin/python3 -m batocera_labwc.build_rule_sets \
		$(BATOCERA_LABWC_DIR)/info_files.txt \
		$(TARGET_DIR)/usr/share/batocera/labwc
endef

BATOCERA_LABWC_POST_INSTALL_TARGET_HOOKS += BATOCERA_LABWC_BUILD_RULE_SETS

$(eval $(local-python-package))
$(eval $(host-local-python-package))
