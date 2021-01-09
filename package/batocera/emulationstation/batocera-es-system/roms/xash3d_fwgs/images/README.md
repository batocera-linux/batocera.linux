The image files here were copied from the Steam installation (Steam/appcache/librarycache) and are also displayed on the Steam web store.

| file                         | `Steam/appcache/librarycache` file                                          |
| ---------------------------- | --------------------------------------------------------------------------- |
| cstrike.jpg                  | [10_header.jpg](https://steamcdn-a.akamaihd.net/steam/apps/10/header.jpg)   |
| dmc.jpg                      | [40_header.jpg](https://steamcdn-a.akamaihd.net/steam/apps/40/header.jpg)   |
| half-life.jpg                | [70_header.jpg](https://steamcdn-a.akamaihd.net/steam/apps/70/header.jpg)   |
| half-life_opposing-force.jpg | [50_header.jpg](https://steamcdn-a.akamaihd.net/steam/apps/50/header.jpg)   |
| half-life_blue-shift.jpg     | [130_header.jpg](https://steamcdn-a.akamaihd.net/steam/apps/130/header.jpg) |

The images files were then optimized with

```sh
jpegoptim --strip-all *.jpg
for f in *.jpg; do jpegtran -progressive -copy none -outfile $f -optimize $f; done
```
