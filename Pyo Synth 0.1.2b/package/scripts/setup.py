"""
This is a setup.py script generated by py2applet

Usage:
    python setup.py py2app
"""

from setuptools import setup

APP = ['Pyo Synth.py']
OPTIONS = {'argv_emulation': True,
           'iconfile': 'logo.icns',
           'includes': ['pyo','wx','zlib'],
           'site_packages': True,
           'plist': "Info.plist"}

setup(
    name="Pyo Synth",
    version="0.1.2b",
    license="GPLv3",
    platforms="OSX",
    author='Alexandre Poirier',
    author_email='alexpoirier05@gmail.com',
    app=APP,
    options={'py2app': OPTIONS},
    setup_requires=['py2app'],
    packages=['resources'],
    requires=['pyo(>=0.8.3)','wxPython(==2.8.12)','python(==2.7.13)']
)
