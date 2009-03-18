# coding=utf-8
"""
Trafikanten
~~~~~~~~~~~

Trafikanten is a library for accessing realtime data about departures
from the Norwegian public transportation system. It covers mainly Oslo
and Akershus counties.

:copyright: Copyright 2009 by the authors. see AUTHORS.
:license: BSD, see LICENSE for details.
"""

__version__ = '0.2'
__author__ = 'Rune Halvorsen <runefh@gmail.com>'
__url__ = 'http://bitbucket.org/runeh/pytrafikanten/'
__license__ = 'BSD License'
__docformat__ = 'restructuredtext'

from .api import find_station, get_realtime
from .classes import CachingTrafikanten, FileCacheTrafikanten, MemoryCacheTrafikanten
