#!/usr/bin/env python3

from setuptools import setup

setup(
    name = "p3drender",
    packages = ["p3drender"],
    scripts = ["scripts/p3drender"],
    version = "1.0.0",
    install_requires = ["docopt", "py3d"],
    author = 'Felix "KoffeinFlummi" Wiegand',
    author_email = "koffeinflummi@protonmail.com",
    description = "A script for rendering P3D files using py3d and Blender",
    license = "MIT",
    keywords = "arma 3d p3d mlod blender rendering render",
    url = "https://github.com/KoffeinFlummi/p3drender",
    classifiers = []
)
