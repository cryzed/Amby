import numpy as np

try:
    import PyQt5
    from PyQt5.QtWidgets import QApplication
    from PyQt5.QtGui import QImage
except ImportError:
    PyQt5 = None

# https://en.wikipedia.org/wiki/Relative_luminance
_luminance_multipliers = np.array([0.2126, 0.7152, 0.0722])
_last_image_reference = None


def _get_color_data_pyqt5(screen, region):
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


def _get_color_data(screen, region):
    if PyQt5:
        return _get_color_data_pyqt5(screen, region)
    else:
        raise Exception('no screenshot provider available')


def _calculate_average_color(data):
    return tuple(np.average(data, axis=0).round().astype(int))


def get_average_color(screen=None, region=None):
    data = _get_color_data(screen, region)
    return _calculate_average_color(data)


def get_average_brightest_color(screen=None, region=None, percentage=10):
    data = _get_color_data(screen, region)

    # Calculate luminance for each color and sort data accordingly
    luminance = np.argsort(np.dot(data, _luminance_multipliers))
    data = data[luminance]

    # TODO: Use percentile index instead?
    count = data.shape[0]
    percentage_index = max(1, int(round((percentage / 100 * count))))
    brightest_colors = data[count - percentage_index:]
    return _calculate_average_color(brightest_colors)
