################################################################################
#
# ti-cgt-pru
#
################################################################################

TI_CGT_PRU_VERSION = 2.2.1
TI_CGT_PRU_SOURCE = ti_cgt_pru_$(TI_CGT_PRU_VERSION)_linux_installer_x86.bin
TI_CGT_PRU_SITE = http://downloads.ti.com/codegen/esd/cgt_public_sw/PRU/$(TI_CGT_PRU_VERSION)
TI_CGT_PRU_LICENSE = TI Technology and Software Publicly Available License (compiler + PRU library), \
	BSL-1.0 (compiler), BSD-2-Clause, BSD-3-Clause, MIT, AFL-3.0, Hewlett-Packard (PRU library)
TI_CGT_PRU_LICENSE_FILES = PRU_Code_Generation_Tools_2.2.x_manifest.html \
	pru_rts_2_2_0_82167478-F8C9-49b2-82BD-12F8550770F9.spdx

define HOST_TI_CGT_PRU_EXTRACT_CMDS
	chmod +x $(DL_DIR)/$(TI_CGT_PRU_SOURCE)
	$(DL_DIR)/$(TI_CGT_PRU_SOURCE) --prefix $(@D) --mode unattended
	mv $(@D)/ti-cgt-pru_$(TI_CGT_PRU_VERSION)/* $(@D)
	rmdir $(@D)/ti-cgt-pru_$(TI_CGT_PRU_VERSION)/
endef

# Since this is largely prebuilt toolchain and likes to live in its
# own directory, put it in $(HOST_DIR)/share/ti-cgt-pru/.
# Packages wanting to use this toolchain need to use this path as TI's
# standard PRU_CGT path e.g. make PRU_CGT=$(TI_CGT_PRU_INSTALLDIR)...
TI_CGT_PRU_INSTALLDIR = $(HOST_DIR)/share/ti-cgt-pru

define HOST_TI_CGT_PRU_INSTALL_CMDS
	mkdir -p $(TI_CGT_PRU_INSTALLDIR)
	cp -dpfr $(@D)/* $(TI_CGT_PRU_INSTALLDIR)
endef

$(eval $(host-generic-package))
