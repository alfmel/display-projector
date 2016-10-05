# display-projector

A simple Python 3 script to find the optimal resolution for an external projector that
will mirror your laptop screen, with the option to set a particular aspect ratio. When
run, the script will:

- Make sure an external display is plugged in
- Grab the resolutions supported by the external display
- Determine the highest resolution for the external display
- Calculate the appropriate scaling factor
- Run xrandr to set all parameters

## Usage

```bash
display_projector.py [ 16:9 | 4:3 ]
```

If the aspect ratio is not specified, it will default to 16:9.
