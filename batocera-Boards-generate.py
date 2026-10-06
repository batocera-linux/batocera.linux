#!/usr/bin/env python3

# todo:
# image.infos without genimage.cfg and vice and versa

from pathlib import Path
import yaml

def images_info_to_board_line(filepath: Path) -> str:
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
            print(f"  [\"arch\"=> \"{image["name"]}\", \"path\" => \"{path}\", \"family\" => \"{image["family"]}\", \"name\" => \"{hardware["name"]}\", \"vendor\" => \"{hardware["vendor"]}\", \"type\" => \"{hardware["type"]}\"],")

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

print("<?php")
print("$boards = [")
for images_info in images_infos:
    images_info_to_board_line(images_info)
print("];")
print("?>")
