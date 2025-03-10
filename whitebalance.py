#!/usr/bin/env python3

import logging
# import numpy as np  # not in GIMP 3.0 RC2 AppImage
import os
import sys

import gi

# Must use require before import:
gi.require_version('Gimp', '3.0')
gi.require_version('GimpUi', '3.0')
# gi.require_version('Gegl', '0.4')  # See https://github.com/GNOME/gimp/blob/095727b0746262bc1cf30e1f1994f81288280edc/plug-ins/python/foggify.py#L22C1-L23C1


from gi.repository import (  # noqa: E402  (must require version before import)
    Gimp,
    Gegl,
    GimpUi,
    GLib,
    GObject,
)

# logging.basicConfig(level=logging.INFO)

MY_NAME = os.path.split(__file__)[1]

logger = logging.getLogger(MY_NAME)  # Don't use __name__ since "__main__" run by GIMP


def adjust_white_balance(image, drawable, plugin_config, stretch_mode="levels",
                         progress_portion=None, progress_offset=None):
    """Adjust white balance relative to the currently selected foreground color.

    If called from the GIMP plugin, caller must:
    - start and end undo group if applicable
    - push and pop context if applicable
    - return procedure.new_return_values(Gimp.PDBStatusType.SUCCESS, GLib.Error())
    """
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

    amount = plugin_config.get_property("amount")  # (1.0 should be "correct")
    # Compute the adjustments. Subtracting a potentially bigger num is
    #   negative (prefer losing detail in dark areas instead of light
    #   areas)
    adjust_r = (target_gray - r) * amount
    adjust_g = (target_gray - g) * amount
    adjust_b = (target_gray - b) * amount

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

        # logger.info("config is {}".format(type(config))) #GimpProcedureConfig
        adjustments = (adjust_r, adjust_g, adjust_b)

        logger.info("adjustments={}".format(adjustments))
        # print("dir(Gimp.HistogramChannel)=%s" % (dir(Gimp.HistogramChannel)))
        # ^ 'ALPHA', 'BLUE', 'GREEN', 'LUMINANCE', 'RED', 'VALUE'
        channels = (
            Gimp.HistogramChannel.RED,
            Gimp.HistogramChannel.GREEN,
            Gimp.HistogramChannel.BLUE,
        )

        low_dist = target_gray
        high_dist = 1.0 - target_gray
        scales = []
        if stretch_mode == "multiply":
            for i in range(len(channels)):
                if brush_rgba[i] > 0:
                    scales.append(target_gray / brush_rgba[i])
                else:
                    Gimp.message(
                        "Error running procedure: Can't use 'multiply'"
                        " mode if R, G, or B is 0.")
                    # Ensure the layer is updated
                    drawable.update(0, 0, drawable.get_width(), drawable.get_height())
                    return
                    scales.append(target_gray)
            r_scale, g_scale, b_scale = scales
        ok_count = 0
        if stretch_mode == "levels":
            for i in range(len(channels)):
                config = procedure.create_config()
                adjust = adjustments[i]
                channel = channels[i]
                # TODO: report issue: no __doc__ for get_properties
                # All properties of gimp-drawable-levels: See
                #   gimp-3-procedures.md
                config.set_property('drawable', drawable)
                config.set_property('channel', channel)
                # config.set_property('low-input', 0.0)
                if plugin_config.get_property("enable_low"):
                    config.set_property('low-input', 0 - adjust)
                    # ^ subtracting negative, so positive--trim darkest
                    #   details
                else:
                    config.set_property('low-input', 0)
                config.set_property('high-input', 1.0)
                config.set_property('clamp-input', False)
                config.set_property('low-output', 0.0)
                if plugin_config.get_property("enable_gamma"):
                    config.set_property('gamma', 1.0 + adjust)
                    # Seems wrong with or without high-output change
                    # (Therefore user may adjust amount if using gamma).
                else:
                    config.set_property('gamma', 1.0)
                if plugin_config.get_property("enable_high"):
                    config.set_property('high-output', 1.0 + adjust)
                else:
                    # Defaults to 0, so:
                    config.set_property('high-output', 1.0)
                config.set_property('clamp-output', False)

                logger.info("procedure.run(config)...")
                result = procedure.run(config)

                if result is None:
                    Gimp.message("Levels adjustment failed, no result returned.")
                    break
                ok_count += 1
                Gimp.progress_update(ok_count / len(channels))
        new_color = Gegl.Color.new("#FFFF")
        size = drawable.get_width(), drawable.get_height()
        w, h = size
        logger.info("size={}".format(size))

        def wb_pyramid(color):
            r, g, b, a = color.get_rgba()
            lightness = (r + g + b) / 3
            proportion = lightness / low_dist if (lightness <= target_gray) else ((1 - lightness) / high_dist)
            new_color.set_rgba(
                max(r + adjust_r * proportion, 0),
                max(g + adjust_g * proportion, 0),
                max(b + adjust_b * proportion, 0),
                a,
            )
            return new_color

        def wb_proportional(color):
            r, g, b, a = color.get_rgba()
            lightness = (r + g + b) / 3
            new_color.set_rgba(
                max(r + adjust_r * lightness, 0),
                max(g + adjust_g * lightness, 0),
                max(b + adjust_b * lightness, 0),
                a,
            )
            return new_color

        def wb_multiply(color):
            r, g, b, a = color.get_rgba()
            new_color.set_rgba(
                min(r * r_scale, 1.0),
                min(g * g_scale, 1.0),
                min(b * b_scale, 1.0),
                a,
            )

        def wb_add(color):
            r, g, b, a = color.get_rgba()
            new_color.set_rgba(
                max(r + adjust_r, 0),
                max(g + adjust_g, 0),
                max(b + adjust_b, 0),
                a,
            )
            return new_color

        wb_fns = {
            "pyramid": wb_pyramid,
            "proportional": wb_proportional,
            "multiply": wb_multiply,
            "add": wb_add,
        }
        wb_fn = wb_fns.get(stretch_mode)
        for y in range(h):
            if stretch_mode == "levels":
                Gimp.progress_update(1.0)
                break  # already done using GIMP procedure above
            elif wb_fn is None:
                raise NotImplementedError(
                    "stretch_mode {} without whitebalance function"
                    " should skip drawing.".format(stretch_mode)
                )
            ratio = y / h
            if progress_portion is not None:
                ratio *= progress_portion
            if progress_offset is not None:
                ratio += progress_offset
            Gimp.progress_update(ratio)
            for x in range(w):
                color = drawable.get_pixel(x, y)
                wb_fn(color)  # sets outer scope's new_color
                drawable.set_pixel(x, y, new_color)
                # logger.debug("{} became {}".format(rgba, new_rgba))

        logger.info("Adjusted {} channel(s)".format(ok_count))
        if ok_count == len(channels):
            Gimp.message("Levels adjustment completed.")
        # else exception should have been shown.
        Gimp.message("White balance adjusted relative to the foreground color.")
    except Exception as e:
        Gimp.message(f"Error running procedure: {str(e)}")
        drawable.update(0, 0, drawable.get_width(), drawable.get_height())
        raise
    # Ensure the layer is updated
    drawable.update(0, 0, drawable.get_width(), drawable.get_height())



# (procedure, run_mode, image, drawables, config, run_data):  # See https://gitlab.gnome.org/GNOME/gimp/-/blame/master/extensions/goat-exercises/goat-exercise-py3.py#L57
def plugin_main(procedure, run_mode, image, drawables, config, run_data):
    if run_mode == Gimp.RunMode.INTERACTIVE:
        # See https://github.com/GNOME/gimp/blob/095727b0746262bc1cf30e1f1994f81288280edc/plug-ins/python/foggify.py#L33
        GimpUi.init(procedure.get_name())
        dialog = GimpUi.ProcedureDialog(procedure=procedure, config=config)
        dialog.fill(None)
        if not dialog.run():
            dialog.destroy()
            return procedure.new_return_values(Gimp.PDBStatusType.CANCEL, GLib.Error())
        else:
            dialog.destroy()

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
            config,
            progress_offset=progress_offset,
            progress_portion=progress_portion,
        )
        progress_offset += progress_portion

    Gimp.displays_flush()

    Gimp.progress_update(1.0)
    Gimp.context_pop()
    image.undo_group_end()
    return procedure.new_return_values(Gimp.PDBStatusType.SUCCESS, GLib.Error())

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

        procedure.add_boolean_argument("enable_high", "Affect brightest", "Affect brightest", True, GObject.ParamFlags.READWRITE)
        procedure.add_boolean_argument("enable_gamma", "Affect gamma (mid-level)", "Affect gamma (mid-level)", False, GObject.ParamFlags.READWRITE)
        procedure.add_boolean_argument("enable_low", "Affect darkest", "Affect darkest", False, GObject.ParamFlags.READWRITE)
        procedure.add_double_argument("amount", "Amount (1.0 to match brush value)", "Amount (1.0 to match brush value)", 0, 2.0, 1.0, GObject.ParamFlags.READWRITE)

        return procedure

Gimp.main(WhiteBalanceBrush.__gtype__, sys.argv)
