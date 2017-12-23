#!/usr/bin/python
# -*- coding: utf-8 -*-

# thumbor imaging service
# https://github.com/thumbor/thumbor/wiki

# Licensed under the MIT license:
# http://www.opensource.org/licenses/mit-license
# Copyright (c) 2011 globo.com thumbor@googlegroups.com
'''This is the main module in thumbor'''

__version__ = "6.3.3rc"
__release_date__ = "22-Jun-2017"

# Syntactic sugar imports
from thumbor.lifecycle.events import Events  # NOQA
from thumbor.blueprints.engines.engine import Engine  # NOQA
