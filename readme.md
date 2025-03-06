# gimp-whitebalance
(not to be confused with [gimp-colortemp](https://github.com/Hierosoft/gimp-colortemp))


### GIMP 3
The WIP Python version is the only GIMP 3 version for now.

#### Install
- GIMP 3.0 plug-ins must be installed in their own folder with the same name as the script:
  - Windows: `%APPDATA%\GIMP\3.0\plug-ins\whitebalance\whitebalance.py`
  - Linux: `~/.config/GIMP/3.0/plug-ins/whitebalance/whitebalance.py`
- Restart GIMP after installing or upgrading the script.
- If it is installed, it will be under "Color", "White Balance from Brush" (enabled when an image is opened).

#### Use
- Load an image
  - The image must be RGB or RGBA.
- Use GIMP's eye dropper to click a gray area (Turn on the "average" option and set range to enough pixels to average any noise well).
- "Color", "White Balance from Brush"


### SCM (GIMP 2.x)
>
> **whitebalance** is a Gimp script for changing the white balance of images. This script-fu script can be used to convert the foreground color to either a neutral gray, or to the color of the background. The conversions are performed in the sRGB color space. In Gimp 2.4 and later, more colorspaces are supported, but the plugin has not yet been adapted to work with general colorspaces.
>
> Once installed, the script is available from the menu item Filters/Colors/White Balance.
>
> ### Download
>
> -   Download **whitebalance.scm** for Gimp 2.2, 2.4, and 2.6 from the attachments section at the bottom of this page.
> -   To install, put the script in the appropriate directory, then click on the menu Filters / Script-Fu / Refresh Filters.  On the Mac, the appropriate directory is Library/Application Support/Gimp/scripts/
>
> ### Usage
>
> You can specify the color temperature of the original image, and the desired color temperature of the result, as well as a light intensity correction factor. There are two ways of specifying the color temperature of the original image:
>
> 1.  (Option: 'From slider below') You can use a slider to specify the color temperature of the original.
> 2.  (Option: 'From foreground color')  Point the color picker tool at something that was white in the photo (example: snow, clouds, a white T-shirt, white paper), and select its color as foreground color.  Colortemp will compute the color temperature of the light when the photo was taken, and it will use that color temperature as the source temperature.  (Details: the script will use as the original temperature the temperature at which a black body is of color closest to the foreground color.)
>
> The first method can be used when you know the color temperature of the source, and does not require the image to contain a white or grey object. For example, to convert from from incandescent to daylight, select 'From slider below', choose 2800K as temperature of the original, and 6500K as the target color temperature.
>
> To use the second method, use the color picker tool to pick the color from a gray or white object in the scene.
>
> The Intensity slider is used to modify the intensity of the image; this can be useful to avoid clipping of channels. The saturation slider can be used to modify the saturation of the image. Sometimes, when performing a large change in color temperature, the effect is more natural if the image is desaturated a little bit.
>
> If you wish to make the foreground color white, you should consider using the [whitebalance](https://web.archive.org/web/20120307072519/http://luca.dealfaro.org/Whitebalance) or grey-point script-fu's.
>
> The color transformation of this color script is performed in the linear, rather than gamma-corrected, color space (as it should, for modifying color temperature). The gamma-corrected color space is the usual one, where a color pixel can have a value from 0 to 255. If x is the value of a pixel in this gamma-corrected space, the value of the pixel in the linear space is approximately (x / 255)^2.2 (the actual conversion is slightly more involved).
>
> The color conversion performed by this script is based on the color of a black body, in the sRGB color space, as a function of temperature. The calculations are correct only for the official sRGB color space, with D65 (6500 K) as white point, and with the sRGB gamma, which is approximately equal to 2.2. As the conversion is based on black-body temperature, it does not necessarily work well for non-black-body light sources, such as mercury lamps, fluorescent lamps, and so forth.

-<https://web.archive.org/web/20120610110646/https://luca.dealfaro.org/Whitebalance>


## Related Projects
- [gimp-colortemp](https://github.com/Hierosoft/gimp-colortemp)
  - based on script by same author: https://web.archive.org/web/20120307072519/http://luca.dealfaro.org/Colortemp
- WhiteBalanceStretch by dinasset
  "Even if [whitebalance.scm] -as Ofnuts pointed out- is less useful in Gimp 2.10, I updated also my personal filter." -<http://gimpchat.com/viewtopic.php?f=9&t=16699#p229884>
- [GIMP Plugin Registry Revived](https://dodoledev.github.io/registry.gimp.org_revived)
  - [whitebalance](https://dodoledev.github.io/registry.gimp.org_revived/node/72.html) (original GIMP 2.2-2.6 version, available as GIMP 2.6.0.0 release here)
- GIMP itself has black, gray, and white color choosers now. In GIMP 3.0 it is under Colors, Levels.
  - Whether this is technically valid (operates in correct colorspace to consistently change Kelvin-based color temperature across all colors and brightness levels in the image, or whatever else) is unknown
- (original version) https://web.archive.org/web/20120224005511/http://luca.dealfaro.org/Whitebalance
- [eAWB](https://github.com/doyousketch2/eAWB): Enhanced Auto White Balance for GIMP


## Contributors
- lucadealfaro (original author)
- dinasset 2018-07-23 (updated whitebalance_upd.7z for GIMP 2.10) <http://gimpchat.com/viewtopic.php?f=9&t=16699#p229884>
- Poikilos (committed versions to git and made releases)


## Discussions Leading up to this repo
- 2016-06-14 <https://stackoverflow.com/questions/37819144/matching-colour-lighting-between-images-using-a-colour-standard-in-gimp>
- 2018-07-23 <http://gimpchat.com/viewtopic.php?f=9&t=16699#p229884>
  - Has GIMP 2.9.5 update (included as release 2.9.5.0 in this repo) edited by dinasset.
  - Discusses dinasset's filter mentioned under "Related Projects" (which may be more technically valid than the colortemp script) and shows examples.
- 2023-10-11 [How to make my images have the same temperature/black point/white point? How to align ruler between photos?](https://www.reddit.com/r/GIMP/comments/175bljy/how_to_make_my_images_have_the_same/)
  - A comment mentions the whitebalance script, but not the colortemp script
