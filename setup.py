import os
from setuptools import setup


setup(
    name = "push-notify-daemon",
    version = "0.0.1",
    author = "Ville Hakulinen",
    author_email = "ville.hakulinen@gmail.com",
    description = ("Notify daemon for push-tool-desktop."),
    license = "GPLv2",
    url = "https://github.com/vhakulinen/push-notify-daemon",
    scripts=["push-notify-daemon/push-notify-daemon.py"],
    classifiers = [
        "Development Status :: 3 - Alpha",
        "Environment :: Console",
        "Topic :: Desktop Environment",
    ]
)
