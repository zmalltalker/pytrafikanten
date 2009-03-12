# coding=utf-8

import tempfile
import shutil
import os
import stat
import time
import pickle
import trafikanten
import inspect

class CachingTrafikanten(object):
    """Superclass for classes that want to wrap around trafikanten while
    providing caching. This class should not be instantiated directly, it
    will not work.
    Subclasses need to implement four methods:
    - _get_cached_search(search_term): returns the cached data, or None if not
        in cache (or cache has expired)
    - _cache_search(search_term, data): saves the data for search_term to the
        cache.
    - _get_cached_realtime: same as _get_cached_search for realtime data
    - _cache_realtime: same as _cache_search for realtime data
    The data returned from the _get_* methods should be the same as what is
    returned from trafikanten.find_station and trafikanten.get_realtime.
    """
    def __init__(self, search_expiry_time=3600, realtime_expiry_time=20):
        self.search_expiry_time = search_expiry_time
        self.realtime_expiry_time = realtime_expiry_time

    def find_station(self, term):
        """Identical arguments and return value as trafikanten.find_station.
        Will call _get_cached_search and _cache_search to handle caching
        properly. Subclasses probably do not need to override this method."""
        data = self._get_cached_search(term)
        if data == None:
            data = trafikanten.find_station(term)
            self._cache_search(term, data)

        return data

    def get_realtime(self, sid):
        """Identical arguments and return value as trafikanten.get_realtime.
        Will call _get_cached_realtime and _cache_realtime to handle caching
        properly. Subclasses probably do not need to override this method."""
        data = self._get_cached_realtime(sid)
        if data == None:
            data = trafikanten.get_realtime(sid)
            self._cache_realtime(sid, data)

        return data

    def _get_cached_realtime(self, sid):
        """Return cached realtime data for the station sid. If no cached
        data is available, return None"""
        raise NotImplementedError("%s must be overridden in a subclass." %
                                  inspect.currentframe().f_code.co_name)

    def _cache_realtime(self, sid, data):
        """Cache realtime data for station sid. Returns nothing. This call
        is assumed to always succeed. If implementing a caching backend
        that may fail, this method should probably throw an exception"""
        raise NotImplementedError("%s must be overridden in a subclass." %
                                  inspect.currentframe().f_code.co_name)

    def _get_cached_search(self, term):
        """Get a cached serch data for term. Of the term is not cached, 
        return None"""
        raise NotImplementedError("%s must be overridden in a subclass." %
                                  inspect.currentframe().f_code.co_name)

    def _cache_search(self, term, data):
        """Cache data for search term. Returns nothing. This call
        is assumed to always succeed. If implementing a caching backend
        that may fail, this method should probably throw an exception"""
        raise NotImplementedError("%s must be overridden in a subclass." %
                                  inspect.currentframe().f_code.co_name)

class FileCacheTrafikanten(CachingTrafikanten):
    """Caching version of the trafikanten API that uses the file system for
    caching. It's fairly naive and will not clean up after itself, unless it's
    using a temporary folder and the object gets GCed."""
    def __init__(self, cache_loc=None, **kwargs):
        if cache_loc:
            self.cache_location = cache_loc
            self.uses_temp = False
        else:
            self.cache_location = tempfile.mkdtemp(".temp", "tf_cache.")
            self.uses_temp = True

        CachingTrafikanten.__init__(self, **kwargs)

    def __del__(self):
        """The desctructor just makes sure that if we're using a temporary
        cache directory, it gets deleted on object gc"""
        if self.uses_temp:
            shutil.rmtree(self.cache_location)

    def _get_cached_search(self, term):
        cachepath = os.path.join(self.cache_location, "search_"+str(hash(term)))
        if os.path.isfile(cachepath):
            age = time.time() - os.stat(cachepath)[stat.ST_MTIME]
            if age < self.search_expiry_time:
                fp = open(cachepath, "rb")
                data = pickle.load(fp)
                fp.close()
                return data

        return None

    def _cache_search(self, term, data):
        cachepath = os.path.join(self.cache_location, "search_"+str(hash(term)))
        fp = open(cachepath, "wb")
        pickle.dump(data, fp)
        fp.close()

    def _get_cached_realtime(self, sid):
        cachepath = os.path.join(self.cache_location, "station_"+str(hash(sid)))
        if os.path.isfile(cachepath):
            age = time.time() - os.stat(cachepath)[stat.ST_MTIME]
            if age < self.search_expiry_time:
                fp = open(cachepath, "rb")
                data = pickle.load(fp)
                fp.close()
                return data

        return None

    def _cache_realtime(self, sid, data):
        cachepath = os.path.join(self.cache_location, "search_"+str(hash(sid)))
        fp = open(cachepath, "wb")
        pickle.dump(data, fp)
        fp.close()


class MemoryCacheTrafikanten(CachingTrafikanten):
    """Caching version of the trafikanten API that ram for caching. It's
    fairly naive. Expired data is never removed"""
    def __init__(self, **kwargs):
        self._search_cache = {}
        self._realtime_cache =  {}

        CachingTrafikanten.__init__(self, **kwargs)

    def _get_cached_search(self, term):
        if term in self._search_cache:
            age = time.time() - self._search_cache[term][0]
            if age < self.search_expiry_time:
                return self._search_cache[term][1]

        return None

    def _cache_search(self, term, data):
        self._search_cache[term] = (time.time(), data)

    def _get_cached_realtime(self, sid):
        if sid in self._realtime_cache:
            age = time.time() - self._search_cache[sid][0]
            if age < self.search_expiry_time:
                return self._search_cache[sid][1]

        return None

    def _cache_realtime(self, sid, data):
        self._realtime_cache[sid] = (time.time(), data)
