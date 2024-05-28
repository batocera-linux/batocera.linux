################################################################################
#
# libretro-core-info
#
################################################################################

LIBRETRO_CORE_INFO_VERSION = v1.18.0
LIBRETRO_CORE_INFO_SITE = $(call github,libretro,libretro-core-info,$(LIBRETRO_CORE_INFO_VERSION))
LIBRETRO_CORE_INFO_LICENSE = GPL

define LIBRETRO_CORE_INFO_INSTALL_TARGET_CMDS
	mkdir -p $(TARGET_DIR)/usr/share/libretro/info
	cp -r $(@D)/*.info $(TARGET_DIR)/usr/share/libretro/info

	cd $(TARGET_DIR)/usr/share/libretro/info && ln -sf mednafen_saturn_libretro.info	beetle-saturn_libretro.info
	cd $(TARGET_DIR)/usr/share/libretro/info && ln -sf bsnes_hd_beta_libretro.info		bsnes_hd_libretro.info
	cd $(TARGET_DIR)/usr/share/libretro/info && ln -sf genesis_plus_gx_wide_libretro.info	genesisplusgx-wide_libretro.info
	cd $(TARGET_DIR)/usr/share/libretro/info && ln -sf genesis_plus_gx_libretro.info	genesisplusgx_libretro.info
	cd $(TARGET_DIR)/usr/share/libretro/info && ln -sf mame2010_libretro.info		mame0139_libretro.info
	cd $(TARGET_DIR)/usr/share/libretro/info && ln -sf mame2003_plus_libretro.info		mame078plus_libretro.info
	cd $(TARGET_DIR)/usr/share/libretro/info && ln -sf mame_libretro.info			mess_libretro.info
	cd $(TARGET_DIR)/usr/share/libretro/info && ln -sf mupen64plus_next_libretro.info	mupen64plus-next_libretro.info
	cd $(TARGET_DIR)/usr/share/libretro/info && ln -sf mednafen_pce_fast_libretro.info	pce_fast_libretro.info
	cd $(TARGET_DIR)/usr/share/libretro/info && ln -sf mednafen_pce_libretro.info		pce_libretro.info
	cd $(TARGET_DIR)/usr/share/libretro/info && ln -sf mednafen_pcfx_libretro.info		pcfx_libretro.info
	cd $(TARGET_DIR)/usr/share/libretro/info && ln -sf snes9x2002_libretro.info		pocketsnes_libretro.info
	cd $(TARGET_DIR)/usr/share/libretro/info && ln -sf snes9x2010_libretro.info		snes9x_next_libretro.info
	cd $(TARGET_DIR)/usr/share/libretro/info && ln -sf vbam_libretro.info			vba-m_libretro.info
	cd $(TARGET_DIR)/usr/share/libretro/info && ln -sf mednafen_vb_libretro.info		vb_libretro.info
	cd $(TARGET_DIR)/usr/share/libretro/info && ln -sf fbalpha2012_libretro.info		fbalpha_libretro.info
	cd $(TARGET_DIR)/usr/share/libretro/info && ln -sf mame2000_libretro.info		imame4all_libretro.info

	# emuscv_libretro.info         => no info found
	# mamevirtual_libretro.so      => no info found
	# superflappybirds_libretro.so => no info found
	# zc210_libretro.so            => no info found
	# hatarib_libretro.info       => no info found
	touch $(TARGET_DIR)/usr/share/libretro/info/emuscv_libretro.info
	touch $(TARGET_DIR)/usr/share/libretro/info/mamevirtual_libretro.info
	touch $(TARGET_DIR)/usr/share/libretro/info/superflappybirds_libretro.info
	touch $(TARGET_DIR)/usr/share/libretro/info/zc210_libretro.info
	touch $(TARGET_DIR)/usr/share/libretro/info/hatarib_libretro.info

endef

$(eval $(generic-package))
