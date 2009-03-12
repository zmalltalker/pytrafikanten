# coding=utf-8

# fixme : test for unicode everywhere!


import os
import types
import trafikanten
import trafikanten.util
import time

def smoke_test_realtime_parser():
    folder = "tests/sample_realtime"
    files = os.listdir(folder)

    # make sure that all the realtime data files in the sample folder is
    # parsed without excepting and returns one or more results
    for path in [os.path.join(folder, f) for f in files]:
        s = open(path).read()
        assert trafikanten.api._parse_realtime_data(s) != None, "Oh noes! %s" % path


def smoke_test_search_parser():
    folder = "tests/sample_search"

    files = os.listdir(folder)

    # make sure that all the realtime data files in the sample folder is
    # parsed without excepting and returns one or more results
    for path in [os.path.join(folder, f) for f in files]:
        s = open(path).read()
        assert trafikanten.api._parse_station_data(s) != None, "Oh noes! %s" % path

def test_search_parser_all_strings_unicode():
    folder = "tests/sample_search"
    files = os.listdir(folder)

    # make sure that all the realtime data files in the sample folder is
    # parsed without excepting and returns one or more results
    for path in [os.path.join(folder, f) for f in files]:
        s = open(path).read()
        parsed = trafikanten.api._parse_station_data(s)
        for entry in parsed:
            for key, value in entry.items():
                if isinstance(value, types.StringType):
                    assert isinstance(value, types.UnicodeType), "Wanted unicode, got %s for key %s" % (type(value), key)

def test_realtime_parser_all_strings_unicode():
    folder = "tests/sample_realtime"
    files = os.listdir(folder)

    # make sure that all the realtime data files in the sample folder is
    # parsed without excepting and returns one or more results
    for path in [os.path.join(folder, f) for f in files]:
        s = open(path).read()
        parsed = trafikanten.api._parse_station_data(s)
        for entry in parsed:
            for key, value in entry.items():
                if isinstance(value, types.StringType):
                    assert isinstance(value, types.UnicodeType), "Wanted unicode, got %s for key %s" % (type(value), key)


def test_util_unicode_search():
    res = [
        {'xcoord': '599475', 'ycoord': '6642907', 'id': '03010661',
         'district': 'Oslo', 'name': u'ÅØÆåøæëêã'}
    ]

    data = trafikanten.util.make_human_readable_stations(res)
    assert isinstance(data, types.UnicodeType)

    data = trafikanten.util.make_delimited_stations(res)
    assert isinstance(data, types.UnicodeType)

    data = trafikanten.util.make_delimited_stations(res, header=True)
    assert isinstance(data, types.UnicodeType)

    data = trafikanten.util.make_xml_stations(res)
    assert isinstance(data, types.UnicodeType)

def test_util_unicode_realtime():
    res = [
        {'direction': u'1', 'destination': u'Kjelsås', 'wait_time': 3271,
         'time': (2008, 12, 26, 14, 47, 0, 4, 361, -1), 'id': u'12',
            'is_realtime': True
        }
    ]

    data = trafikanten.util.make_human_readable_realtime(res)
    assert isinstance(data, types.UnicodeType)

    data = trafikanten.util.make_delimited_realtime(res)
    assert isinstance(data, types.UnicodeType)

    data = trafikanten.util.make_delimited_realtime(res, header=True)
    assert isinstance(data, types.UnicodeType)

    data = trafikanten.util.make_xml_realtime(res)
    assert isinstance(data, types.UnicodeType)


def test_fuzzy_departure_unicode():
    t, d = trafikanten.util.fuzzy_departure({"wait_time": 3})
    assert t == trafikanten.util.FUZZY_NOW
    assert d == None

    t, d = trafikanten.util.fuzzy_departure({"wait_time": 120})
    assert t == trafikanten.util.FUZZY_MINS
    assert d == 2

    now = time.localtime()

    t, d = trafikanten.util.fuzzy_departure({"wait_time": 700, "time": now})
    assert t == trafikanten.util.FUZZY_TIME
    assert d != None

def test_invalid_station_id():
    assert trafikanten.get_realtime("does_not_exist") == None

def test_unicode_term_handling():
    term = u"østerås"
    assert trafikanten.find_station(term)
