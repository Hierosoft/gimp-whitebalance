 Training Disclosure for gimp-whitebalance
This Training Disclosure, which may be more specifically titled above here (and in this document possibly referred to as "this disclosure"), is based on **Training Disclosure version 1.1.4** at https://github.com/Hierosoft/training-disclosure by Jake Gustafson. Jake Gustafson is probably *not* an author of the project unless listed as a project author, nor necessarily the disclosure editor(s) of this copy of the disclosure unless this copy is the original which among other places I, Jake Gustafson, state IANAL. The original disclosure is released under the [CC0](https://creativecommons.org/public-domain/cc0/) license, but regarding any text that differs from the original:

This disclosure also functions as a claim of copyright to the scope described in the paragraph below since potentially in some jurisdictions output not of direct human origin, by certain means of generation at least, may not be copyrightable (again, IANAL):

Various author(s) may make claims of authorship to content in the project not mentioned in this disclosure, which this disclosure by way of omission unless stated elsewhere implies is of direct human origin unless stated elsewhere. Such statements elsewhere are present and complete if applicable to the best of the disclosure editor(s) ability. Additionally, the project author(s) hereby claim copyright and claim direct human origin to any and all content in the subsections of this disclosure itself, where scope is defined to the best of the ability of the disclosure editor(s), including the subsection names themselves, unless where stated, and unless implied such as by context, being copyrighted or trademarked elsewhere, or other means of statement or implication according to law in applicable jurisdiction(s).

Disclosure editor(s): Hierosoft LLC

Project author: Hierosoft LLC

This disclosure is a voluntary of how and where content in or used by this project was produced by LLM(s) or any tools that are "trained" in any way.

The main section of this disclosure lists such tools. For each, the version, install location, and a scope of their training sources in a way that is specific as possible.

Subsections of this disclosure contain prompts used to generate content, in a way that is complete to the best ability of the disclosure editor(s).

tool(s) used:
- GPT-4-Turbo (Version 4o, chatgpt.com)

Scope of use: code described in subsections--typically modified by hand to improve logic, variable naming, integration, etc.

## whitebalance.py
- 2025-03-05

In GIMP 3.0 the GIMP scm script fails with:
scriptfu-Message: 11:52:43.438: Error while executing script-fu-colortemp:

gimp_plug_in_destroy_proxies: ERROR: GimpImage proxy with ID 3 was refed by plug-in, it MUST NOT do that!
gimp_plug_in_destroy_proxies: ERROR: GimpLayer proxy with ID 17 was refed by plug-in, it MUST NOT do that!
gimp_plug_in_destroy_proxies: ERROR: GimpGradient proxy with ID 2081 was refed by plug-in, it MUST NOT do that!
gimp_plug_in_destroy_proxies: ERROR: GimpFont proxy with ID 2956 was refed by plug-in, it MUST NOT do that!
gimp_plug_in_destroy_proxies: ERROR: GimpGradient proxy with ID 2055 was refed by plug-in, it MUST NOT do that!
gimp_plug_in_destroy_proxies: ERROR: GimpPalette proxy with ID 2014 was refed by plug-in, it MUST NOT do that!
. Try to fix it:

- paste scm version 2.10.4-1

Yes, the parts you mentioned.

Update the script to be fully compatible with GIMP 3.0.

Clearly you aren't listening. The undo lines are already in the script. Fix it for GIMP 3.0:

- paste scm version 2.10.4-1 again

You're missing most of the code. Try again:

- paste scm version 2.10.4-1 again

Convert this to GIMP 3.0:

- paste scm version 2.10.4-1 again except only keep 1st and last entry of list to prevent exceeding limits (ChatGPT had said it only got part of it, probably due to context window)

Wow, you're totally wrong. Just change the white balance relative to the selected brush's foreground color. First, get an average of R, G, and B from that color. Then, add to the redness of the entire image by (average - R), add to the greenness of the entire image by (average - G), add to the blueness of the entire image by (average - B).

It causes "AttributeError: 'Color' object has no attribute 'r'". Keep in mind Gegl.Color is used for Gimp 3.0, and the foreground color's only public attributes are 'bind_property', 'bind_property_full', 'chain', 'compat_control', 'connect', 'connect_after', 'connect_data', 'connect_object', 'connect_object_after', 'disconnect', 'disconnect_by_func', 'duplicate', 'emit', 'emit_stop_by_name', 'find_property', 'force_floating', 'freeze_notify', 'g_type_instance', 'get_bytes', 'get_cmyk', 'get_components', 'get_data', 'get_format', 'get_hsla', 'get_hsva', 'get_properties', 'get_property', 'get_qdata', 'get_rgba', 'get_rgba_with_space', 'getv', 'handler_block', 'handler_block_by_func', 'handler_disconnect', 'handler_is_connected', 'handler_unblock', 'handler_unblock_by_func', 'install_properties', 'install_property', 'interface_find_property', 'interface_install_property', 'interface_list_properties', 'is_floating', 'list_properties', 'new', 'newv', 'notify', 'notify_by_pspec', 'override_property', 'parent_instance', 'priv', 'props', 'qdata', 'ref', 'ref_count', 'ref_sink', 'replace_data', 'replace_qdata', 'run_dispose', 'set_bytes', 'set_cmyk', 'set_components', 'set_data', 'set_hsla', 'set_hsva', 'set_properties', 'set_property', 'set_rgba', 'set_rgba_with_space', 'steal_data', 'steal_qdata', 'stop_emission', 'stop_emission_by_name', 'thaw_notify', 'unref', 'watch_closure', 'weak_ref'

The script still causes "AttributeError: 'PDB' object has no attribute 'run_procedure'. Did you mean: 'lookup_procedure'?". The public attributes and methods of pdb are: 'bind_property', 'bind_property_full', 'chain', 'compat_control', 'connect', 'connect_after', 'connect_data', 'connect_object', 'connect_object_after', 'disconnect', 'disconnect_by_func', 'dump_to_file', 'emit', 'emit_stop_by_name', 'find_property', 'force_floating', 'freeze_notify', 'g_type_instance', 'get_data', 'get_last_error', 'get_last_status', 'get_properties', 'get_property', 'get_qdata', 'getv', 'handler_block', 'handler_block_by_func', 'handler_disconnect', 'handler_is_connected', 'handler_unblock', 'handler_unblock_by_func', 'install_properties', 'install_property', 'interface_find_property', 'interface_install_property', 'interface_list_properties', 'is_floating', 'list_properties', 'lookup_procedure', 'newv', 'notify', 'notify_by_pspec', 'override_property', 'procedure_exists', 'props', 'qdata', 'query_procedures', 'ref', 'ref_count', 'ref_sink', 'replace_data', 'replace_qdata', 'run_dispose', 'set_data', 'set_properties', 'set_property', 'steal_data', 'steal_qdata', 'stop_emission', 'stop_emission_by_name', 'temp_procedure_name', 'thaw_notify', 'unref', 'watch_closure', 'weak_ref'

(whitebalance.py:107550): LibGimp-CRITICAL **: 12:56:02.988: gimp_pdb_lookup_procedure: assertion 'gimp_is_canonical_identifier (procedure_name)' failed
Traceback (most recent call last):
  File "/home/owner/.config/GIMP/3.0/plug-ins/whitebalance/whitebalance.py", line 68, in plugin_main
    adjust_white_balance(image, drawables)
  File "/home/owner/.config/GIMP/3.0/plug-ins/whitebalance/whitebalance.py", line 39, in adjust_white_balance
    procedure.run([
    ^^^^^^^^^^^^^^^
AttributeError: 'NoneType' object has no attribute 'run'

- Chat expired, so start new

Try to fix "TypeError: Gimp.PDB.query_procedures() takes exactly 9 arguments (1 given)" using the latest GIMP 3.0 code to fix

- Paste Python version from previous conversation with minor manual fixes

TypeError: Gimp.PDB.query_procedures() takes exactly 9 arguments (5 given)

All arguments of query_procedures have to be strings, and you added an extra argument. pdb.query_procedures.__doc__ shows self and name:str, blurb:str, help:str, help_id:str, authors:str, copyright:str, date:str, proc_type:str

(whitebalance.py:110091): LibGimp-WARNING **: 13:25:02.867: _gimp_procedure_run_array: no return values, shouldn't happen
/home/owner/.config/GIMP/3.0/plug-ins/whitebalance/whitebalance.py:157: Warning: g_error_new: assertion 'domain != 0' failed
  Gimp.main(WhiteBalanceBrush.__gtype__, sys.argv)

Also you should have said gimp-drawable-levels, not gimp_drawable_levels, which I have fixed in my copy.

It still gives (whitebalance.py:110516): LibGimp-WARNING **: 13:31:21.164: _gimp_procedure_run_array: no return values, shouldn't happen
/home/owner/.config/GIMP/3.0/plug-ins/whitebalance/whitebalance.py:164: Warning: g_error_new: assertion 'domain != 0' failed
  Gimp.main(WhiteBalanceBrush.__gtype__, sys.argv)