################################################################################
#
# RetroLX Samsung Exynos 5422 kernel package
#
################################################################################
KERNEL_EXYNOS5422_VERSION = 5.10.47
KERNEL_EXYNOS5422_SITE = https://github.com/RetroLX/kernel-exynos5422.git
KERNEL_EXYNOS5422_SITE_METHOD = git

define KERNEL_EXYNOS5422_INSTALL_TARGET_CMDS
	cp $(@D)/*      $(BINARIES_DIR)/
endef

$(eval $(generic-package))
