# coding=utf-8
"""
    Trafikanten
    ~~~~~~~~~~~

    Trafikanten is a library for accessing realtime data about departures
    fromthe Norwegian public transportation system. It covers mainly Oslo
    and Akershus counties.

    :copyright: Copyright 2009. see AUTHORS.
    :license: BSD, see LICENSE for details.
"""
from .api import find_station, get_realtime
from .classes import CachingTrafikanten, FileCacheTrafikanten, MemoryCacheTrafikanten

__version__ = '0.1'
__author__ = 'Rune Halvorsen <runefh@gmail.com>'
__url__ = 'http://bitbucket.org/runeh/pytrafikanten/'
__license__ = 'BSD License'
__docformat__ = 'restructuredtext'
