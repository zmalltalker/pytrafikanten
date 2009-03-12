# coding=utf-8

import math
import time
import xml.dom.minidom as minidom

FUZZY_NOW = 1
FUZZY_MINS = 2
FUZZY_TIME = 3

def fuzzy_departure(dep, mins_cutoff=10, time_format="%H.%M"):
    """Makes a fuzzy representation of the time to wait. Returns a tuple
    containing (result_type, result).

    If the wait time is less than one minute returns (FUZZY_NOW, "Now").
    If the wait time is less than mins_cutoff (in minutes), returns
    (FUZZY_MINS, number_of_minutes_to_wait)
    If the wait time is equal or greater than mins_cutoff returns 
    (FUZZY_TIME, time_for_departure). The time will be formated according
    to time_format, which is in the format of time.striftime."""
    wait = int(dep["wait_time"])
    if wait < 60:
        return (FUZZY_NOW, None)
    elif wait < mins_cutoff*60:
        return (FUZZY_MINS, int(math.floor(wait/60)))
    else:
        return (FUZZY_TIME, time.strftime(time_format, dep["time"]))

def make_human_readable_stations(res):
    """Makes  text representation of a search result that is suitable for 
    showing to a user. Returns a string"""
    ret = []
    if not res:
        ret.append( u"""No stations found""")
    else:
        format = u"%%(id)%ds %%(name)s (%%(district)s)" % \
                                max([ len(e["id"]) for e in res ])
        for dep in res:
            ret.append(format % dep)
    return "\n".join(ret)

def make_delimited_stations(res, header=False, separator=";"):
    """Emit station search result delimited by separator. If header is
    true, include field names as the first line, using same delimiter.
    """
    if not res:
        return ""
    
    separator = unicode(separator)

    format = separator.join(("%(id)s", "%(name)s", "%(district)s",
              "%(xcoord)s", "%(ycoord)s"))
    
    ret = []
    if header:
        ret.append(
            separator.join(("id", "name", "district", "xcoord", "ycoord")))

    for dep in res:
        ret.append(format % dep)
    
    return "\n".join(ret)

def make_xml_stations(res):
    """Serialize as search result in res to xml. Returns xml as a string.
    Format of xml is as follows:
    <stations>
        <station>
            <id>123123</id>
            <name>asdf</name
            <disctrict>Oslo</district>

            fixme: more

    """

    impl = minidom.getDOMImplementation()
    document = impl.createDocument(None, "stations", None)
    body = document.documentElement
    for hit in res:
        station = document.createElement("station")
        for key, val in hit.items():
            ele = document.createElement(key)
            ele.appendChild(document.createTextNode(val))
            station.appendChild(ele)
        body.appendChild(station)
    
    pretty = document.toprettyxml()
    # fixme: minidom docs says this is needed due to bugs with cyclic gc. 
    # Is this still the case though?
    document.unlink() 

    return pretty

def make_delimited_realtime(res, header=False, separator=";"):
    """Emit realtimeresult delimited by separator. If header is true, include
    field names as the first line, using same delimiter
    """
    if not res:
        return ""

    clean_res = [
        { "id": e["id"],
          "destination": e["destination"],
          "direction": e["direction"],
          "is_realtime": str(int(e["is_realtime"])),
          "wait_time": e["wait_time"],
          "time": time.asctime(e["time"])
        } for e in res
    ]

    format = separator.join(("%(id)s", "%(destination)s", "%(direction)s",
              "%(is_realtime)s", "%(wait_time)s", "%(time)s"))
    
    ret = []
    if header:
        ret.append(separator.join(("id", "destination", "direction",
                              "is_realtime", "wait_time", "time")))
    for dep in clean_res:
        ret.append(format % dep)

    return "\n".join(ret)

def make_human_readable_realtime(res):
    if not res:
        return """No departures found for station."""
    else:
        format = u"""%%(id)%ds %%(destination)-%ds %%(formatted_wait)-5s""" % \
                 (max([ len(e["id"]) for e in res ]),
                  max([ len(e["destination"]) for e in res ]))
        ret = []
        for dep in res:
            curdep = {"id": dep["id"], "destination": dep["destination"]}
            fuzz, val = fuzzy_departure(dep)

            if fuzz == FUZZY_NOW:
                curdep["formatted_wait"] = u"Now"
            elif fuzz == FUZZY_MINS and val == 1:
                curdep["formatted_wait"] = u"1 min"
            elif fuzz == FUZZY_MINS:
                curdep["formatted_wait"] = u"%d mins" % val
            else:
                curdep["formatted_wait"] = val
            
            ret.append(format % curdep)

    return "\n".join(ret)

def make_xml_realtime(res):
    """Serialize realtime data in res to xml. Returns xml as a string.
    Format of xml is as follows:
    <realtime>
        <departure>
            <id>123123</id>
            <name>asdf</name
            <time>result from time.asctime</time>
            <is_realtime>yes|no</is_realtime>
            <wait_time>234</wait_time>
            fixme: more

    """
    impl = minidom.getDOMImplementation()

    type_mapper = {
        "time": lambda t: time.asctime(t),
        "wait_time": unicode,
        "is_realtime": lambda b: u"yes" if b else u"no"
    }

    document = impl.createDocument(None, "realtime", None)
    body = document.documentElement
    for hit in res:
        departure = document.createElement("departure")
        for key, val in hit.items():
            ele = document.createElement(key)
            if key in type_mapper:
                ele.appendChild(document.createTextNode(type_mapper[key](val)))
            else:
                ele.appendChild(document.createTextNode(val))
            departure.appendChild(ele)
        body.appendChild(departure)
    
    pretty = document.toprettyxml()

    # fixme: minidom docs says this is needed due to bugs with cyclic gc. 
    # Is this still the case though?
    document.unlink()
    return pretty

