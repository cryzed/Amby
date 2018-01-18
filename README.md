# Amby
Ambient Lighting for the Philips Hue Bridge on Linux

## Description
There's [ScreenBloom] for Windows and MAC systems, but I wanted
something similar for my Linux installation. The color averaging for the
ambient light probably works slightly differently, but I quite like it.

This isn't supposed to be perfect, I just made it for myself. I decided
to share it because some people asked around for something like this. If
the dependency on PyQt5 is acceptable, it could also easily be used to
add Linux support to the [ScreenBloom] project.

## Usage
Start the script like this:

`$ ./amby <bridge_address> <lights> --username <username>`

If initially no Philips Hue Bridge username is specified
(omit `-u/--username`), the script will prompt you to create one. You can
then use the generated username in subsequent invocations. Use the
`-h/--help` option for more options.

## Requirements
* Python 3.6+
* numpy
* qhue
* rgbxy
* PyQt5


[ScreenBloom]: https://github.com/kershner/screenBloom
