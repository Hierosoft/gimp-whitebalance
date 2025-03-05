#!/usr/bin/env python3

import gi

gi.require_version('Gimp', '3.0')
# gi.require_version('GimpUi', '3.0')
# gi.require_version('Gegl', '0.4')  # See https://github.com/GNOME/gimp/blob/095727b0746262bc1cf30e1f1994f81288280edc/plug-ins/python/foggify.py#L22C1-L23C1

from gi.repository import (
    Gimp,
    # Gegl,
    # GimpUi,
    # GLib,
    # GObject,
)




import sys

def adjust_white_balance(image, drawable):
    """Adjust white balance relative to the currently selected foreground color."""
    pdb = Gimp.get_pdb()

    # Get the current foreground color
    fg_color = Gimp.context_get_foreground()
    r, g, b, _ = fg_color.get_rgba()

    # Compute the average of the RGB components
    avg = (r + g + b) / 3.0

    # Compute the adjustments
    adjust_r = avg - r
    adjust_g = avg - g
    adjust_b = avg - b
    # proc_name = gimp_drawable_levels  # apparently for GIMP 2.x only
    # available_procedures = pdb.query_procedures()
    # ^ expects 9 arguments, 1 given
    #!/usr/bin/env python3

import gi
gi.require_version('Gimp', '3.0')

from gi.repository import Gimp
import sys

def adjust_white_balance(image, drawable):
    """Adjust white balance relative to the currently selected foreground color."""
    pdb = Gimp.get_pdb()

    # Get the current foreground color
    fg_color = Gimp.context_get_foreground()
    r, g, b, _ = fg_color.get_rgba()

    # Compute the average of the RGB components
    avg = (r + g + b) / 3.0

    # Compute the adjustments
    adjust_r = avg - r
    adjust_g = avg - g
    adjust_b = avg - b

    # proc_name = "gimp_drawable_levels"  # for GIMP 2.x?
    #   2.x used "gimp-levels" it seems in
    #   https://github.com/bootchk/GimpFu-v3/blob/7e6e08a2acb34fe2dce6631f9f255dae5ab34a6b/gimpfu/adaption/compatibility.py#L107
    proc_name = "gimp-drawable-levels"

    # Query available procedures for the plugin type

    # print("pdb.query_procedures.__doc__=%s" % pdb.query_procedures.__doc__):
    #   self, name:str, blurb:str, help:str, help_id:str, authors:str,
    #   copyright:str, date:str, proc_type:str
    available_procedures = pdb.query_procedures(
        "",        # name
        "",        # blurb
        "",        # help
        "",        # help_id
        "",        # authors
        "",        # copyright
        "",        # date
        "PLUGIN",  # proc_type
    )
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
    levels_proc = pdb.lookup_procedure(proc_name)
    try:
        # Apply levels adjustment to shift colors
        # Example from
        #   <https://github.com/oliva/dotfiles/blob/5d4475ae3af8fb4b762f486cfec9f5a0e0b5eac7/gimp/.config/GIMP/2.99/plug-ins/text-halo/text-halo.py#L99>
        #   [mask, Gimp.HistogramChannel.VALUE,  #drawable, channel
        #    level_min, level_max, True, 1.0,  #input min, max, clamp, gamma
		#    0.0, 1.0, False]
        result = levels_proc.run([
            drawable,
            0,  # Channel (RGB)
            0.0, 1.0, True, 1.0, # input: min, max, clamp, gamma
            # Output levels:
            0 + adjust_r, 255 + adjust_r,
            0 + adjust_g, 255 + adjust_g,
            0 + adjust_b, 255 + adjust_b,
        ])
        if result is not None:
            Gimp.message("Levels adjustment completed.")
        else:
            Gimp.message("Levels adjustment failed, no result returned.")
    except Exception as e:
        Gimp.message(f"Error running procedure: {str(e)}")

    # Ensure the layer is updated
    drawable.update(0, 0, drawable.width, drawable.height)

    Gimp.message("White balance adjusted relative to the foreground color.")


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
    adjust_white_balance(image, drawables)


class WhiteBalanceBrush(Gimp.PlugIn):
    __gtype_name__ = "WhiteBalanceBrush"
    # See https://github.com/UserUnknownFactor/GIMP3-ML/blob/f53dee1f92052b57de78b03ba3ffd0ad5ff4309c/gimpml/plugins/filterfolder/filterfolder.py#L206
    # @GObject.Property(type=Gimp.RunMode,
    #                   default=Gimp.RunMode.NONINTERACTIVE,
    #                   nick="Run mode", blurb="The run mode")

    def do_query_procedures(self):
        return ["python-fu-white-balance-brush"]

    def do_create_procedure(self, name):
        # Gegl.init(None)
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
