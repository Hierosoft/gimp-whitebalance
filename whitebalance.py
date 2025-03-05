#!/usr/bin/env python3

import logging
import os
import sys

import gi

# Must use require before import:
gi.require_version('Gimp', '3.0')
# gi.require_version('GimpUi', '3.0')
# gi.require_version('Gegl', '0.4')  # See https://github.com/GNOME/gimp/blob/095727b0746262bc1cf30e1f1994f81288280edc/plug-ins/python/foggify.py#L22C1-L23C1


from gi.repository import (  # noqa: E402  (must require version before import)
    Gimp,
    Gegl,
    # GimpUi,
    # GLib,
    # GObject,
)

logging.basicConfig(level=logging.INFO)

MY_NAME = os.path.split(__file__)[1]

logger = logging.getLogger(MY_NAME)  # Don't use __name__ since "__main__" run by GIMP


def adjust_white_balance(image, drawable, add_undo=False, stretch_mode='add',
                         progress_portion=None, progress_offset=None):
    """Adjust white balance relative to the currently selected foreground color."""
    logger.info("adjust_white_balance...")
    pdb = Gimp.get_pdb()

    logger.info("context_get_foreground...")
    # Get the current foreground color
    fg_color = Gimp.context_get_foreground()
    logger.info("get_rgba...")
    brush_rgba = fg_color.get_rgba()
    r, g, b, _ = brush_rgba

    logger.info("fg_color.get_rgba()={}".format(fg_color.get_rgba()))

    # baseline = (r + g + b) / 3.0  # add diff of average loses light detail
    # prefer losing dark details (add a negative if target higher than channel)
    # - detail loss can be avoided using only input in gimp-drawable-levels
    target_gray = min(r, g, b)

    # Compute the adjustments. Subtracting a potentially bigger num is
    #   negative (prefer losing detail in dark areas instead of light
    #   areas)
    adjust_r = target_gray - r
    adjust_g = target_gray - g
    adjust_b = target_gray - b

    # proc_name = "gimp_drawable_levels"  # for GIMP 2.x?
    #   2.x used "gimp-levels" it seems in
    #   https://github.com/bootchk/GimpFu-v3/blob/7e6e08a2acb34fe2dce6631f9f255dae5ab34a6b/gimpfu/adaption/compatibility.py#L107
    proc_name = "gimp-drawable-levels"

    # Query available procedures for the plugin type

    # print("pdb.query_procedures.__doc__=%s" % pdb.query_procedures.__doc__):
    #   self, name:str, blurb:str, help:str, help_id:str, authors:str,
    #   copyright:str, date:str, proc_type:str
    logger.info("query_procedures...")
    available_procedures = pdb.query_procedures(
        "",        # name
        "",        # blurb
        "",        # help
        "",        # help_id
        "",        # authors
        "",        # copyright
        "",        # date
        "",  # proc_type (NOTE: "PLUGIN" returns nothing)
    )
    logger.info("{} in available_procedures ?...".format(proc_name))
    if proc_name not in available_procedures:
        Gimp.message(
            "Error: '{}' not found in PDB! Got:"
            .format(proc_name))
        # print("available_procedures={}".format(dir(available_procedures)))
        for this_p in available_procedures:
            print("  - {}".format(this_p))
            # break
        print()
        return
    logger.info("pdb.lookup_procedure({})...".format(proc_name))
    procedure = pdb.lookup_procedure(proc_name)
    try:
        # Apply levels adjustment to shift colors
        # Example from
        #   <https://github.com/oliva/dotfiles/blob/5d4475ae3af8fb4b762f486cfec9f5a0e0b5eac7/gimp/.config/GIMP/2.99/plug-ins/text-halo/text-halo.py#L99>
        #   [mask, Gimp.HistogramChannel.VALUE,  #drawable, channel
        #    level_min, level_max, True, 1.0,  #input min, max, clamp, gamma
		#    0.0, 1.0, False]

        # result = procedure.run([
        #     drawable,
        #     0,  # Channel (RGB)
        #     0.0, 1.0, True, 1.0, # input: min, max, clamp, gamma
        #     # Output levels:
        #     0 + adjust_r, 255 + adjust_r,
        #     0 + adjust_g, 255 + adjust_g,
        #     0 + adjust_b, 255 + adjust_b,
        # ])
        # ^ (whitebalance.py:114766): LibGimp-WARNING **: 14:33:40.324: _gimp_procedure_run_array: no return values, shouldn't happen
        # /home/owner/.config/GIMP/3.0/plug-ins/whitebalance/whitebalance.py:171: Warning: g_error_new: assertion 'domain != 0' failed
        #   Gimp.main(WhiteBalanceBrush.__gtype__, sys.argv)
        # so as per
        # <https://github.com/cam92473/diffuse-dwarf-detection/blob/cc5b4a9c2f45a50064087c3d800398d18aa52607/ALGORITHM/IMAGE_PROCESS/gimp_procedure/gimp_procedure.py#L199>:
        logger.info("procedure.create_config()...")
        config = procedure.create_config()
        adjustments = (adjust_r, adjust_g, adjust_b)

        logger.info("adjustments={}".format(adjustments))
        # print("dir(Gimp.HistogramChannel)=%s" % (dir(Gimp.HistogramChannel)))
        # ^ 'ALPHA', 'BLUE', 'GREEN', 'LUMINANCE', 'RED', 'VALUE'
        channels = (
            Gimp.HistogramChannel.RED,
            Gimp.HistogramChannel.GREEN,
            Gimp.HistogramChannel.BLUE,
        )

        scales = []
        for i in range(len(channels)):
            scales.append(target_gray / brush_rgba[i])

        ok_count = 0
        # Doesn't work (does opposite)--reason unknown:
        # for i in range(len(channels)):
        #     adjust = adjustments[i]
        #     channel = channels[i]
        #     config.set_property('drawable', drawable)
        #     config.set_property('channel', channel)
        #     config.set_property('low-input', 0.0)
        #     config.set_property('high-input', 1.0)
        #     config.set_property('clamp-input', False)
        #     config.set_property('gamma', 1.0)
        #     config.set_property('low-output', 0.0)
        #     config.set_property('high-output', 1.0 + adjust)
        #     config.set_property('clamp-output', False)
        #     logger.info("procedure.run(config)...")
        #     result = procedure.run(config)

        #     if result is None:
        #         Gimp.message("Levels adjustment failed, no result returned.")
        #         break
        #     ok_count += 1
        new_color = Gegl.Color.new("#FFFF")
        size = drawable.get_width(), drawable.get_height()
        w, h = size
        print("size={}".format(size))
        for y in range(h):
            ratio = y / h
            if progress_portion is not None:
                ratio *= progress_portion
            if progress_offset is not None:
                ratio += progress_offset
            Gimp.progress_update(ratio)
            for x in range(w):
                color = drawable.get_pixel(x, y)
                rgba = color.get_rgba()  # returns _ResultTuple
                new_rgba = []
                lightness = (rgba[0] + rgba[1] + rgba[2]) / 3
                for i in range(len(rgba)):
                    if i < len(channels):
                        if stretch_mode == "proportional":
                            new_rgba.append(
                                rgba[i]
                                + adjustments[i] * lightness
                            )
                            if new_rgba[i] < 0:
                                new_rgba[i] = 0
                        elif stretch_mode == "multiply":
                            new_rgba.append(rgba[i] * scales[i])
                            if new_rgba[i] < 0:
                                new_rgba[i] = 0
                            elif new_rgba[i] > 1.0:
                                new_rgba[i] = 1.0
                        elif stretch_mode == "add":
                            new_rgba.append(rgba[i] + adjustments[i])
                            if new_rgba[i] < 0:
                                new_rgba[i] = 0
                        else:
                            raise ValueError(
                                "unknown stretch_mode={}".format(stretch_mode))
                    else:  # keep existing alpha
                        new_rgba.append(rgba[i])
                new_color.set_rgba(new_rgba[0], new_rgba[1], new_rgba[2], new_rgba[3])
                drawable.set_pixel(x, y, new_color)
                # logger.debug("{} became {}".format(rgba, new_rgba))

        logger.info("Adjusted {} channel(s)".format(ok_count))
        if ok_count == len(channels):
            Gimp.message("Levels adjustment completed.")
        # else exception should have been shown.
        Gimp.message("White balance adjusted relative to the foreground color.")
    except Exception as e:
        Gimp.message(f"Error running procedure: {str(e)}")
        raise

    # Ensure the layer is updated
    drawable.update(0, 0, drawable.get_width(), drawable.get_height())



# (procedure, run_mode, image, drawables, config, run_data):  # See https://gitlab.gnome.org/GNOME/gimp/-/blame/master/extensions/goat-exercises/goat-exercise-py3.py#L57
def plugin_main(procedure, run_mode, image, drawables, config, run_data):
    # print([type(arg) for arg in args]):
    # [
    #   <class 'gi.repository.Gimp.ImageProcedure'>,
    #   <class 'gi.repository.Gimp.RunMode'>,
    #   <class 'gi.repository.Gimp.Image'>,
    #   <class 'list'>,
    #   <class '__gi__.GimpProcedureConfigRun-python-fu-white-balance-brush'>,
    #   <class 'NoneType'>
    # ]
    # print(type(drawables[0]))  # : <class 'gi.repository.Gimp.Layer'>
    image.undo_group_start()
    Gimp.context_push()
    progress_offset = 0
    progress_portion = 1 / len(drawables)
    layer_n = 0
    for drawable in drawables:
        layer_n += 1
        Gimp.progress_init(
            "This may take a while (layer {} of {})..."
            .format(layer_n, len(drawables)))
        adjust_white_balance(
            image,
            drawable,
            progress_offset=progress_offset,
            progress_portion=progress_portion,
        )
        progress_offset += progress_portion

    Gimp.displays_flush()

    Gimp.progress_update(1.0)
    Gimp.context_pop()
    image.undo_group_end()


class WhiteBalanceBrush(Gimp.PlugIn):
    __gtype_name__ = "WhiteBalanceBrush"
    # See https://github.com/UserUnknownFactor/GIMP3-ML/blob/f53dee1f92052b57de78b03ba3ffd0ad5ff4309c/gimpml/plugins/filterfolder/filterfolder.py#L206
    # @GObject.Property(type=Gimp.RunMode,
    #                   default=Gimp.RunMode.NONINTERACTIVE,
    #                   nick="Run mode", blurb="The run mode")

    def do_query_procedures(self):
        return ["python-fu-white-balance-brush"]

    def do_create_procedure(self, name):
        Gegl.init(None)
        # if name == "python-fu-white-balance-brush":
        procedure = Gimp.ImageProcedure.new(
            self,
            name,
            Gimp.PDBProcType.PLUGIN,
            plugin_main,
            None,
            # None
        )
        procedure.set_image_types("*")
        procedure.set_menu_label("White Balance from Brush")  # required or won't appear
        procedure.set_documentation(
            "Adjust white balance based on the foreground color",
            "Modifies image balance relative to the currently selected foreground color",
            "Jake Gustafson"
        )
        procedure.set_attribution("Jake Gustafson", "Jake Gustafson", "2025")
        procedure.add_menu_path("<Image>/Colors")  # Set parent
        return procedure

Gimp.main(WhiteBalanceBrush.__gtype__, sys.argv)
