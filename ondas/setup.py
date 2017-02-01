#!/usr/bin/env python
"""
setup.py file for Ondas
"""

from distutils.core import setup, Extension

ondas_module = Extension(
    '_ondas',
    sources=['ondas_wrap.c', 'ondas.c'], )

setup(
    name='ondas',
    version='0.1',
    author="Andres",
    description="""Gerador de ondas""",
    ext_modules=[ondas_module],
    py_modules=["ondas"], )
