#!/usr/bin/env python3

# todo:
# image.infos without genimage.cfg and vice and versa

from pathlib import Path
import yaml
import json

def images_info_to_board_line(filepath: Path) -> str:
    res = []
    path = Path(filepath)
  
    with open(path, 'r', encoding='utf-8') as f:
        data = yaml.safe_load(f)

    if len(data["images"]) == 0:
        raise Exception("no image found for infos file")
    for image in data["images"]:
        if len(image["hardwares"]) == 0:
            raise Exception("no hardware found for board")
        for hardware in image["hardwares"]:
            path = filepath.relative_to("board/batocera").parent
            res.append({"arch": f"{image["name"]}",
                        "path": f"{path}",
                        "family": f"{image["family"]}",
                        "name": f"{hardware["name"]}",
                        "vendor": f"{hardware["vendor"]}",
                        "type": f"{hardware["type"]}",
                        })
    return res
images_infos = list(Path("board").rglob("image.infos"))
genimages    = list(Path("board").rglob("genimage.cfg"))

# check 1-1 between image.infos and genimage.cfg
images_infos_dict = {}
for x in images_infos:
    images_infos_dict[Path(x).parent] = {}
genimages_dict = {}
for x in genimages:
    genimages_dict[Path(x).parent] = {}
for x in images_infos_dict:
    if x not in genimages_dict:
        print(f"image.infos without genimage.cfg ({x})")
for x in genimages_dict:
    if x not in images_infos_dict:
        print(f"genimage.cfg without image.infos ({x})")

all = []
for images_info in images_infos:
    all.extend(images_info_to_board_line(images_info))

# id
n = 1
for x, obj in enumerate(all):
    all[x]["id"] = n
    #all[x]["doc"] = ""
    #all[x]["labeled"] = False
    n = n+1

print(json.dumps({"boards": all}, indent=2))
