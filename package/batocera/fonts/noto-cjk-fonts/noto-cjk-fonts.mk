################################################################################
#
# noto-cjk-fonts
#
################################################################################

NOTO_CJK_FONTS_VERSION = Sans2.004
NOTO_CJK_FONTS_SITE = https://github.com/notofonts/noto-cjk/releases/download/$(NOTO_CJK_FONTS_VERSION)
NOTO_CJK_FONTS_SOURCE = 02_NotoSansCJK-TTF-VF.zip

NOTO_CJK_FONTS_TARGET_DIR=$(TARGET_DIR)/usr/share/fonts/truetype/noto

define NOTO_CJK_FONTS_EXTRACT_CMDS
	$(UNZIP) -d $(@D) $(NOTO_CJK_FONTS_DL_DIR)/$(NOTO_CJK_FONTS_SOURCE)
endef

define NOTO_CJK_FONTS_INSTALL_TARGET_CMDS
	mkdir -p $(NOTO_CJK_FONTS_TARGET_DIR)
	cp $(@D)/Variable/TTF/Subset/*.ttf $(NOTO_CJK_FONTS_TARGET_DIR)
endef

$(eval $(generic-package))
