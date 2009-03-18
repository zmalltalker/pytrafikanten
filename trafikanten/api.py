# coding=utf-8

import urllib
import time
import math
import xml.dom.minidom as minidom
from trafikanten import __version__ as version
from util import utm_to_lat_lng

# url for station search api
_station_url = "http://www5.trafikanten.no/txml/?type=1&stopname=%s"

# url for non-subway realtime data
_non_subway_rt_url = \
    "http://www.sis.trafikanten.no/xmlrtpi/dis/request?DISID=SN$%s"

# url for subway realtime data
_subway_rt_url = \
    "http://www.sis.trafikanten.no:8088/xmlrtpi/dis/request?DISID=SN$%s"

# known subways station ids. Required because subway stations use a different
# realtime data source than other stations.
_subway_stations = [
    "03011930", "03012220", "03011030", "03012365", "02190070", "02190080",
    "02190090", "03010011", "03010020", "03010031", "03010200", "03010360",
    "03010370", "03010600", "03010610", "03010770", "03010780", "03010950",
    "03011010", "03011020", "03011110", "03011120", "03011130", "03011140",
    "03011200", "03011210", "03011220", "03011310", "03011320", "03011330",
    "03011400", "03011410", "03011430", "03011440", "03011450", "03011510",
    "03011520", "03011530", "03011540", "03011610", "03011620", "03011630",
    "03011710", "03011720", "03011730", "03011810", "03011910", "03011920",
    "03011940", "03012000", "03012010", "03012020", "03012030", "03012040",
    "03012100", "03012120", "03012130", "03012210", "03012230", "03012240",
    "03012260", "03012270", "03012280", "03012305", "03012310", "03012315",
    "03012320", "03012325", "03012330", "03012340", "03012345", "03012350",
    "03012355", "03012360", "03012370", "03012375", "03012380", "03012385",
    "03012390", "03012410", "03012420", "03012430", "03012450", "03012460",
    "03012560", "03012565", "03012572", "03012630"
]

class TrafikantentURLopener(urllib.FancyURLopener):
    version = "pytrafikanten/%s" % version

urllib._urlopener = TrafikantentURLopener()

def find_station(term):
    """Search for stations matching term.
    Returns a list of dicts of the form:
    match = {
        "id": "03232323",
        "name": "some station name",
        "district": "district for station",
        "xcoord": "0",
        "ycoord"; "0"
    }
    If no matches where found, the list has length 0. If the search did not
    complete successfully, return None.
    """
    if not term:
        return None

    url = _station_url % urllib.quote(term.encode("utf-8"))
    data = urllib.urlopen(url).read()
    return _parse_station_data(data)

def _get_text(nodelist):
    """Stupid helper for dom. give me .textContent plx
    Returns the contcatentated contents of all text nodes in nodelist"""
    text = u""
    for node in nodelist:
        if node.nodeType == node.TEXT_NODE:
            text = text + unicode(node.data)
    return text

def _single_element(node, name):
    """If node contains one or more children with nodename "name", return the
    first one. If not, return None"""
    elems = node.getElementsByTagName(name)
    if elems: return elems[0]
    else: return None

def _parse_station_data(xmlstr):
    """
    Takes xml a string and returns a list of dicts containing station data.
    """
    doc = minidom.parseString(xmlstr)
    ret = []
    elem_map = {"fromid": "id", "StopName": "name", "District": "district",
                "XCoordinate": "xcoord", "YCoordinate": "ycoord"}
    for elem in doc.getElementsByTagName("StopMatch"):
        entry = {"district": u""}
        for name, value in [ (e.nodeName, _get_text(e.childNodes)) \
                              for e in elem.childNodes \
                              if e.nodeType == e.ELEMENT_NODE  ]:
            if name in elem_map:
                entry[elem_map[name]] = unicode(value)

        if "id" in entry and "name" in entry:
            add_lat_lng_to_entry(entry)
            ret.append(entry)

    return ret

def add_lat_lng_to_entry(entry):
    """Adds a lat and lng for x and y (which is another coordinate system)"""
    entry["lat"], entry["lng"] = utm_to_lat_lng(int(entry['xcoord']), int(entry['ycoord']))

def get_realtime(sid):
    """Get realtime data for station with id "sid". Returns a list of
    dictionaries. If no realtime data is found, the returned list will be
    empty. If the station doesn't exist, or any other error occurs, returns
    None.
    """
    if not sid:
        return None

    if sid in _subway_stations:
        url = _subway_rt_url % sid
    else:
        url = _non_subway_rt_url % sid

    data = urllib.urlopen(url).read()
    result = _parse_realtime_data(data)

    if result:
        result.sort(key=lambda e: int(e["wait_time"]))

    return result

def _parse_realtime_data(xmlstr):
    """
    Takes xml a string and returns a list of dicts containing realtime data.
    """
    doc = minidom.parseString(xmlstr)
    ret = []
    elem_map = {"LineID": "id", "DirectionID": "direction",
                "DestinationStop": "destination" }

    ack = _single_element(doc, "Acknowledge")
    if ack == None or ack.attributes["Result"].nodeValue != "ok":
        return None

    curtime = time.mktime(time.strptime(
        ack.attributes["TimeStamp"].nodeValue[:-10], "%Y-%m-%dT%H:%M:%S"))

    for elem in doc.getElementsByTagName("DISDeviation"):
        entry = {"is_realtime": False}

        for name, value in [ (e.nodeName, _get_text(e.childNodes)) \
                              for e in elem.childNodes \
                              if e.nodeType == e.ELEMENT_NODE ]:
            if name in elem_map:
                entry[elem_map[name]] = unicode(value)
            elif name == "TripStatus":
                entry["is_realtime"] = value == "Real"

        if entry["is_realtime"]:
            timeele = _single_element(elem, "ExpectedDISDepartureTime")
        else:
            timeele = _single_element(elem, "ScheduledDISDepartureTime")

        parsed_time = time.strptime(
            _get_text(timeele.childNodes)[:-10], "%Y-%m-%dT%H:%M:%S")
        entry["time"] = parsed_time
        entry["wait_time"] = int(time.mktime(parsed_time) - curtime)
        ret.append(entry)

    return ret
