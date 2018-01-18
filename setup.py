from setuptools import setup, find_packages

setup(
    name='Amby',
    version='1.0',
    packages=find_packages(),
    url='https://github.com/cryzed/Amby',
    license='MIT',
    author='Chris Braun',
    author_email='cryzed@googlemail.com',
    description='Ambient Lighting for the Philips Hue Bridge on Linux',
    # Currently PyQt5 is a hard dependency, since it is the only implemented color provider
    install_requires=['qhue', 'numpy', 'appdirs', 'rgbxy', 'PyQt5'],
    entry_points={
        'console_scripts': [
            'amby = amby.cli:main'
        ]
    }
)
