from __future__ import annotations

import json
import logging
import shutil
from pathlib import Path
from typing import Final

from PIL import Image

from batocera_common.dataclasses import cached_dataclass
from batocera_common.paths import BATOCERA_SHARE_DIR
from batocera_launch import BezelFiles, create_gun_border_image, create_transparent_image, get_image_size
from batocera_launch_mame_common import get_machine_size

from .base import MAMEBase

_logger: Final = logging.getLogger(__name__)


@cached_dataclass
class MAMEBezels(MAMEBase):
    async def prepare_bezel(self) -> Path | None:
        try:
            await self.__write_bezel_config(self.bezel_set)
        except Exception:
            await self.__write_bezel_config(None)

    async def __write_bezel_config(self, bezel_set: str | None, /) -> None:
        mess_system_name = self.mess_system_info.name if self.mess_system_info else None

        tmp_zip_dir = Path('/var/run/mame_artwork') / (mess_system_name if mess_system_name else self.rom.stem)

        # clean, in case no bezel is set, and in case we want to recreate it
        if tmp_zip_dir.exists():
            shutil.rmtree(tmp_zip_dir)

        gun_border_dimensions = self.gun_border_dimensions

        if bezel_set is None and gun_border_dimensions is None:
            return

        if (float(self.resolution.width) / float(self.resolution.height) < 1.6) and gun_border_dimensions is None:
            return

        # let's generate the zip file
        tmp_zip_dir.mkdir(parents=True)

        # bezels infos
        if bezel_set is None:
            if gun_border_dimensions is not None:
                bezel_files = None
            else:
                return
        else:
            bezel_files = self.bezel_files
            if bezel_files is None and gun_border_dimensions is None:
                return

        # create an empty bezel
        if bezel_files is None:
            overlay_png_file = Path('/tmp/bezel_transmame_black.png')
            create_transparent_image(overlay_png_file, self.resolution.width, self.resolution.height)
            bezel_files = BezelFiles(overlay_png_file)

        # copy the png inside
        if bezel_files.mame_zip is not None and bezel_files.mame_zip.exists():
            art_file = Path('/var/run/mame_artwork') / f'{mess_system_name if mess_system_name else self.rom.stem}.zip'

            if art_file.exists():
                art_file.unlink()

            art_file.symlink_to(bezel_files.mame_zip)

            # hum, not nice if guns need borders
            return

        if bezel_files.layout is not None and bezel_files.layout.exists():
            (tmp_zip_dir / 'default.lay').symlink_to(bezel_files.layout)
            png_file = tmp_zip_dir / bezel_files.png.name
            png_file.symlink_to(bezel_files.png)
            image_width, image_height = get_image_size(bezel_files.png)
        else:
            png_file = tmp_zip_dir / 'default.png'
            png_file.symlink_to(bezel_files.png)

            if bezel_files.info is not None and bezel_files.info.exists():
                bz_info_data = json.loads(bezel_files.info.read_text())

                image_width: int = bz_info_data['width']
                image_height: int = bz_info_data['height']
                bz_y: int = bz_info_data['top']
                bz_x: int = bz_info_data['left']
                bz_bottom: int = bz_info_data['bottom']
                bz_right: int = bz_info_data['right']
                bz_alpha: float = bz_info_data.get('opacity', 1.0)  # Just in case it's not set in the info file

                bz_width = image_width - bz_x - bz_right
                bz_height = image_height - bz_y - bz_bottom
            else:
                image_width, image_height = get_image_size(bezel_files.png)
                _, _, rotate = await get_machine_size(self.rom.stem, tmp_zip_dir)

                # assumes that all bezels are setup for 4:3H or 3:4V aspects
                if rotate == 270 or rotate == 90:
                    bz_width = int(image_height * (3 / 4))
                else:
                    bz_width = int(image_height * (4 / 3))
                bz_height = image_height
                bz_x = int((image_width - bz_width) / 2)
                bz_y = 0
                bz_alpha = 1.0

            (tmp_zip_dir / 'default.lay').write_text(f'''<mamelayout version="2">
    <element name="bezel"><image file="default.png" /></element>
    <view name="bezel">
        <screen index="0"><bounds x="{bz_x}" y="{bz_y}" width="{bz_width}" height="{bz_height}" /></screen>
        <element ref="bezel"><bounds x="0" y="0" width="{image_width}" height="{image_height}" alpha="{bz_alpha}" /></element>
    </view>
</mamelayout>
''')
        if (bezel_tattoo := self.config.get_str('bezel.tattoo', '0')) != '0':
            tattoo: Image.Image | None = None

            if bezel_tattoo == 'system':
                tattoo_file = BATOCERA_SHARE_DIR / 'controller-overlays' / f'{self.system}.png'
                if not tattoo_file.exists():
                    tattoo_file = BATOCERA_SHARE_DIR / 'controller-overlays' / 'generic.png'

                try:
                    tattoo = Image.open(tattoo_file)
                except Exception:
                    _logger.error('Error opening controller overlay: %s', tattoo_file)

            elif (
                bezel_tattoo == 'custom'
                and (bezel_tattoo_file := self.config.get_str('bezel.tattoo_file'))
                and (tattoo_file := Path(bezel_tattoo_file)).exists()
            ):
                try:
                    tattoo = Image.open(tattoo_file)
                except Exception:
                    _logger.error('Error opening custom file: %s', tattoo_file)
            else:
                tattoo_file = BATOCERA_SHARE_DIR / 'controller-overlays' / 'generic.png'
                try:
                    tattoo = Image.open(tattoo_file)
                except Exception:
                    _logger.error('Error opening custom file: %s', tattoo_file)

            if tattoo is not None:
                output_png_file = Path('/tmp/bezel_tattooed.png')
                back = Image.open(png_file)
                tattoo = tattoo.convert('RGBA')
                back = back.convert('RGBA')
                tw, th = get_image_size(tattoo_file)
                tatwidth = int(
                    240 / 1920 * image_width
                )  # 240 = half of the difference between 4:3 and 16:9 on 1920px (0.5*1920/16*4)
                pcent = float(tatwidth / tw)
                tatheight = int(float(th) * pcent)
                tattoo = tattoo.resize((tatwidth, tatheight), Image.Resampling.LANCZOS)  # pyright: ignore[reportUnknownMemberType]
                alphatat = tattoo.split()[-1]
                corner = self.config.get_str('bezel.tattoo_corner', 'NW')
                if corner.upper() == 'NE':
                    back.paste(tattoo, (image_width - tatwidth, 20), alphatat)  # 20 pixels vertical margins (on 1080p)
                elif corner.upper() == 'SE':
                    back.paste(tattoo, (image_width - tatwidth, image_height - tatheight - 20), alphatat)
                elif corner.upper() == 'SW':
                    back.paste(tattoo, (0, image_height - tatheight - 20), alphatat)
                else:  # default = NW
                    back.paste(tattoo, (0, 20), alphatat)
                imgnew = Image.new('RGBA', (image_width, image_height), (0, 0, 0, 255))
                imgnew.paste(back, (0, 0, image_width, image_height))
                imgnew.save(output_png_file, mode='RGBA', format='PNG')

                try:
                    png_file.unlink()
                except Exception:
                    pass

                png_file.symlink_to(output_png_file)

        # borders for guns
        if gun_border_dimensions is not None:
            output_png_file = Path('/tmp/bezel_gunborders.png')
            create_gun_border_image(
                png_file,
                output_png_file,
                gun_border_dimensions,
                self.guns_border_ratio,
                inner_color=self.gun_borders_color,
            )

            try:
                png_file.unlink()
            except Exception:
                pass

            png_file.symlink_to(output_png_file)
