#!/usr/bin/env python3
"""
Setup script for Logo Designer package
"""

from setuptools import setup, find_packages

setup(
    name="logo-designer",
    version="0.1.0",
    description="A GUI application for designing logos with text",
    author="Logo Designer Team",
    packages=find_packages(),
    install_requires=[
        "pillow",
        "numpy",
    ],
    entry_points={
        'console_scripts': [
            'logo-designer=main:main',
        ],
    },
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Designers",
        "Programming Language :: Python :: 3",
        "Topic :: Multimedia :: Graphics",
        "License :: OSI Approved :: MIT License",
    ],
    python_requires=">=3.6",
)
