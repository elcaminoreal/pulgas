# Copyright (c) Moshe Zadka
# See LICENSE for details.
import os
import sys

import pulgas

extensions = [
    'sphinx.ext.autodoc',
    'sphinx.ext.viewcode',
    'sphinx.ext.napoleon',
]
master_doc = 'index'
project = 'Pulgas'
copyright = '2018, Moshe Zadka'
author = 'Moshe Zadka'
version = release = pulgas.__version__
