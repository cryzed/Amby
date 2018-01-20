# Amby
Ambient Lighting for the Philips Hue Bridge on Linux

## Description
There's [ScreenBloom] for Windows and MAC systems, but I wanted something similar for my Linux installation. The color
averaging for the ambient light probably works slightly differently (simply the average of each color channel).

This isn't supposed to be perfect, I just made it for myself. I decided to share it because some people asked around for
something like this (mostly on the ScreenBloom issue tracker). If the dependency on PyQt5 is acceptable, it could also
be used to easily add support for Linux to the ScreenBloom project.

PyQt5 is currently a hard dependency because its really fast and no other screenshot providers are implemented.

## Installation
Run `$ pip install https://github.com/cryzed/Amby/archive/master.zip`, preferably in a virtual environment or with
`--user` and _not_ as root (despite what you might have read).

## Usage
Run Amby like this: `$ amby <bridge_address> <lights>`

Where `bridge_address` is the domain or IP address of the bridge and `lights` a space-separated list of light indices
that should be controlled by Amby.

A sample invocation might look like this:

`$ amby 192.168.0.75 1 -b -m 50 -i 0`

Meaning: "Contact the bridge at 192.168.0.75, set the ambient color for light 1, change the brightness to equal or
greater than 50% of the maximum brightness (depending on the luminance of the calculated ambient color) and don't wait
at all between iterations of this process (higher CPU usage!)."

When initially starting, Amby will prompt you to create a username to authenticate with the Philips Hue Bridge. Use the
`-h/--help` option to see all available options and their descriptions.

## Requirements
* Python 3.6+
* Python modules: qhue, numpy, appdirs, rgbxy, PyQt5


[ScreenBloom]: https://github.com/kershner/screenBloom
