################################################################################
#
# nanum-font
#
################################################################################

NANUM_FONT_VERSION = 2385eb085e4bf326590a2db6d4514e8477d9922f
NANUM_FONT_SITE = $(call github,bulzipke,nanum-font,$(NANUM_FONT_VERSION))

NANUM_FONT_TARGET_DIR=$(TARGET_DIR)/usr/share/fonts/truetype/nanum

define NANUM_FONT_INSTALL_TARGET_CMDS
	@mkdir -p $(NANUM_FONT_TARGET_DIR)
	@cp $(@D)/ttf/NanumSquare_acB.ttf $(NANUM_FONT_TARGET_DIR)
endef

$(eval $(generic-package))
