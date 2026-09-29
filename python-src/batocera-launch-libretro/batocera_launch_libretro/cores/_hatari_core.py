from __future__ import annotations

from batocera_common.configparser import CaseSensitiveConfigParser
from batocera_common.paths import CONFIGS
from batocera_launch_libretro import Core


class HatariConfigMixin(Core):
    def generate_special_configs(self) -> None:
        super().generate_special_configs()

        # Create/update hatari.cfg
        if self.system == 'atarist':
            hatari_conf = CONFIGS / 'hatari' / 'hatari.cfg'
            hatari_config = CaseSensitiveConfigParser(interpolation=None)

            if hatari_conf.exists():
                hatari_config.read(hatari_conf)

            # update the configuration file
            hatari_conf.parent.mkdir(parents=True, exist_ok=True)
            with hatari_conf.open('w') as configfile:
                hatari_config.write(configfile)
