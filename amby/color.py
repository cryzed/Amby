import numpy as np

try:
    import PyQt5
    from PyQt5.QtWidgets import QApplication
    from PyQt5.QtGui import QImage
except ImportError:
    PyQt5 = None


def _get_average_color_pyqt5(screen, region):
    application = QApplication([])

    screen = application.primaryScreen() if screen is None else application.screens()[screen - 1]
    screen_size = screen.size()
    region = region or (0, 0, screen_size.width(), screen_size.height())
    image = screen.grabWindow(0, *region).toImage()  # type: QImage

    # Data is stored as BGRA, despite image.format() claiming it is QImage.Format_RGB32
    pointer = image.constBits()
    data = pointer.asarray(image.byteCount())
    array = np.ndarray(shape=(image.byteCount() // 4, 4), dtype=np.ubyte, buffer=data)

    # Ignore alpha channel, round all values, convert to integers and reverse order BGR -> RGB
    average = np.average(array[:, :-1], axis=0).round().astype(int)[::-1]
    return tuple(average)


def get_average_color(screen=None, region=None):
    if PyQt5:
        return _get_average_color_pyqt5(screen, region)

    raise Exception('no screenshot provider available')
