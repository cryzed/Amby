import numpy as np

from amby.constants import PHILIPS_MAX_BRIGHTNESS

try:
    import PyQt5
    from PyQt5.QtWidgets import QApplication
    from PyQt5.QtGui import QImage
except ImportError:
    PyQt5 = None

# https://en.wikipedia.org/wiki/Relative_luminance
_luminance_multipliers = np.array([0.2126, 0.7152, 0.0722])
_max_luminance = np.dot([255, 255, 255], _luminance_multipliers)
_last_image_reference = None


def _get_pixel_data_pyqt5(screen, region):
    application = QApplication([])
    screen = application.primaryScreen() if screen is None else application.screens()[screen - 1]
    screen_size = screen.size()
    region = region or (0, 0, screen_size.width(), screen_size.height())
    image = screen.grabWindow(0, *region).toImage()  # type: QImage

    # Data is stored as BGRA, despite image.format() claiming it is QImage.Format_RGB32
    pointer = image.constBits()
    data = pointer.asarray(image.byteCount())

    # Since the data is stored as BGRA there are 4 channels, with a single byte representing each one
    array = np.ndarray(shape=(image.byteCount() // 4, 4), dtype=np.ubyte, buffer=data)
    # Ugly hack so the QImage isn't cleaned up by Python's garbage collector prematurely
    global _last_image_reference
    _last_image_reference = image

    # Ignore alpha channel, and reverse order BGR -> RGB
    return np.fliplr(array[:, :-1])


def get_pixel_data(screen=None, region=None):
    if PyQt5:
        return _get_pixel_data_pyqt5(screen, region)
    else:
        raise Exception('no screenshot provider available')


def get_average_color(data):
    return tuple(np.average(data, axis=0).round().astype(int))


def get_relative_brightness(data, ignore_black):
    max_brightness = _max_luminance * data.shape[0]
    luminance = np.dot(data, _luminance_multipliers)
    absolute_brightness = np.sum(luminance, axis=0)

    if ignore_black:
        # Act like absolutely black pixels have a neutral effect on the absolute brightness by multiplying their amount
        # with half of the maximum brightness
        black_pixels = data.shape[0] - np.count_nonzero(luminance)
        absolute_brightness += PHILIPS_MAX_BRIGHTNESS / 2 * black_pixels

    return absolute_brightness / max_brightness
