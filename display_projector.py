#!/usr/bin/python

# A cool Python script to set the optimal resolution on the laptop screen and on the external projector.

import os
import sys

from Xlib import X, display
from Xlib.ext import randr


# A very important value
laptop_display = "eDP1"

class XlibWrapper():
    __laptop_16_9_resolution = {"width": 1920, "height": 1080}
    __laptop_4_3_resolution = {"width": 1400, "height": 1050}  # This prevents KDE's panel from disappearing
    __no_limit = {"width": 100000, "height": 100000}
    
    def __init__(self):
        d = display.Display()
        s = d.screen()
        self.__window = s.root.create_window(0, 0, 1, 1, 1, s.root_depth)
        
        
    def get_all_displays(self):
        """
        Returns a dictionary with a list of displays indexed by the display
        """
        displays = {}
        
        # Get all the outputs; we will get their properties later
        outputs = randr.get_screen_resources(self.__window).outputs
        
        for output in outputs:
            properties = self._get_display_properties(output)
            displays[properties["name"]] = output
        
        return displays
        
        
    def get_connected_displays(self):
        """
        Returns a dictionary with a list of displays indexed by the display
        """
        displays = {}
        
        # Get all the outputs; we will get their properties later
        outputs = randr.get_screen_resources(self.__window).outputs
        
        for output in outputs:
            properties = self._get_display_properties(output)
            if properties["connection"] == 0:
                displays[properties["name"]] = output
        
        return displays
        
        
    def _get_display_properties(self, output_id):
        return randr.get_output_info(self.__window, output_id, 0)._data
    
    
    def get_modes(self, output_id):
        """
        Returns the modes associated with the given output
        """
        mode_dict = {}
        
        # Get the modes for this monitor
        modes = self._get_display_properties(output_id)["modes"]
        
        all_modes = randr.get_screen_resources(self.__window)._data["modes"]
            
        for mode_id in modes:
            for mode in all_modes:
                if mode["id"] == mode_id:
                    width = mode["width"]
                    height = mode["height"]
                    
                    mode_name = "{}x{}".format(width, height)
                    mode_dict[mode_name] = mode
        
        return mode_dict

    
    def get_highest_resolution(self, modes, aspect_ratio=None):
        """
        Returns the highest resolution mode that does not exceed the preferred resoltion of the laptop display
        """
        preferred_mode = None
        
        if aspect_ratio == "16:9":
            limits = self.__laptop_16_9_resolution
        elif aspect_ratio == "4:3":
            limits = self.__laptop_4_3_resolution
        else:
            limits = self.__no_limit
        
        # Go through the modes
        for key, mode in modes.items():
            mode_aspect_ratio = self._get_aspect_ratio(mode)
            
            tmp_mode = None
            if aspect_ratio == mode_aspect_ratio:
                tmp_mode = mode
            elif aspect_ratio is None:
                tmp_mode = mode
            
            if tmp_mode is not None:
                if preferred_mode is None:
                    if mode["width"] <= limits["width"] and mode["height"] <= limits["height"]:
                        preferred_mode = mode
                else:
                    if (mode["width"] > preferred_mode["width"] or mode["height"] > preferred_mode["height"]) and \
                            (mode["width"] <= limits["width"] and mode["height"] <= limits["height"]):
                        preferred_mode = mode
    
        return preferred_mode
    

    def _get_aspect_ratio(self, mode):
        if mode["width"] / mode["height"] == 4 / 3:
            return "4:3"
        elif mode["width"] / mode["height"] == 16 / 9:
            return "16:9"
        else:
            return "other"


    def get_scaling_factor(self, mode, aspect_ratio=None):
        base = self.get_laptop_resolution(aspect_ratio)
        
        horiz_factor = base["width"] / mode["width"]
        vert_factor = base["width"] / mode["width"]
        
        if horiz_factor > vert_factor:
            return horiz_factor
        else:
            return vert_factor
        
    
    def get_laptop_resolution(self, aspect_ratio):
        if aspect_ratio == "4:3":
            return self.__laptop_4_3_resolution
        else:
            return self.__laptop_16_9_resolution


# Do real work
xlib_wrapper = XlibWrapper()

# Get the connected displays
displays = xlib_wrapper.get_connected_displays()
if len(displays) < 2:
    print("External display is not connected", file=sys.stderr)
    sys.exit(1)
elif len(displays) > 2:
    print("Too many displays connected", file=sys.stderr)
    sys.exit(1)

if len(sys.argv) > 1:
    aspect_ratio = sys.argv[1]
else:
    aspect_ratio = None
    
if aspect_ratio != "4:3":
    aspect_ratio = "16:9"

# Get the external display
display = None
display_name = None
for output_name, output_id in displays.items():
    if output_name != laptop_display:
        display = output_id
        display_name = output_name
        print("Using output {} for projector display".format(display_name))

if display is None:
    print("Could not get external display", file=sys.stderr)
    sys.exit(1)

# Get the modes for this display
modes = xlib_wrapper.get_modes(display)
best_mode = xlib_wrapper.get_highest_resolution(modes, aspect_ratio=aspect_ratio)

if best_mode is None:
    print("Could not get appropritate mode", file=sys.stderr)
    sys.exit(1)

# Get the scaling factor
scaling_factor = xlib_wrapper.get_scaling_factor(best_mode, aspect_ratio)

# Get the mode for the laptop
laptop_mode = xlib_wrapper.get_laptop_resolution(aspect_ratio)

# Run the command
base_command = "xrandr --output {} --mode {}x{} --output {} --mode {}x{} --scale {}x{} --same-as {}"
command = base_command.format(laptop_display, laptop_mode["width"], laptop_mode["height"], display_name,
                              best_mode["width"], best_mode["height"], scaling_factor, scaling_factor, laptop_display)

print(command)
os.system(command)
