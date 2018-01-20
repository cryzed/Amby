import numpy as np
import rgbxy

try:
    import PyQt5
    from PyQt5.QtWidgets import QApplication
    from PyQt5.QtGui import QImage
except ImportError:
    PyQt5 = None

# https://en.wikipedia.org/wiki/Relative_luminance
_white_color = 255, 255, 255
_luminance_multipliers = 0.2126, 0.7152, 0.0722
_last_image_reference = None
_color_converter = rgbxy.Converter()


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


def _get_absolute_luminance(color):
    return sum(x * y for x, y in zip(color, _luminance_multipliers))


_max_luminance = _get_absolute_luminance(_white_color)


def get_relative_luminance(color):
    return _get_absolute_luminance(color) / _max_luminance


def get_average_color(data_matrix):
    return tuple(np.average(data_matrix, axis=0).round().astype(int))


def rgb_to_xy(color):
    # Prevent DivisionByZero exception in rgbxy library:
    # https://github.com/benknight/hue-python-rgb-converter/issues/6
    color = tuple(max(component, 10 ** -3) for component in color)
    return _color_converter.rgb_to_xy(*color)
