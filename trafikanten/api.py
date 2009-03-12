# coding=utf-8

import urllib
import time
import math
import xml.dom.minidom as minidom

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
  lat, lng = utm_to_lat_lng(32, int(entry['xcoord']), int(entry['ycoord']))
  entry["lat"] = lat
  entry["lng"] = lng

def utm_to_lat_lng(zone, easting, northing, northernHemisphere=True):
  """Converts from utm to lat_lng"""
  if not northernHemisphere:
      northing = 10000000 - northing

  a = 6378137
  e = 0.081819191
  e1sq = 0.006739497
  k0 = 0.9996

  arc = northing / k0
  mu = arc / (a * (1 - math.pow(e, 2) / 4.0 - 3 * math.pow(e, 4) / 64.0 - 5 * math.pow(e, 6) / 256.0))

  ei = (1 - math.pow((1 - e * e), (1 / 2.0))) / (1 + math.pow((1 - e * e), (1 / 2.0)))

  ca = 3 * ei / 2 - 27 * math.pow(ei, 3) / 32.0

  cb = 21 * math.pow(ei, 2) / 16 - 55 * math.pow(ei, 4) / 32
  cc = 151 * math.pow(ei, 3) / 96
  cd = 1097 * math.pow(ei, 4) / 512
  phi1 = mu + ca * math.sin(2 * mu) + cb * math.sin(4 * mu) + cc * math.sin(6 * mu) + cd * math.sin(8 * mu)

  n0 = a / math.pow((1 - math.pow((e * math.sin(phi1)), 2)), (1 / 2.0))

  r0 = a * (1 - e * e) / math.pow((1 - math.pow((e * math.sin(phi1)), 2)), (3 / 2.0))
  fact1 = n0 * math.tan(phi1) / r0

  _a1 = 500000 - easting
  dd0 = _a1 / (n0 * k0)
  fact2 = dd0 * dd0 / 2

  t0 = math.pow(math.tan(phi1), 2)
  Q0 = e1sq * math.pow(math.cos(phi1), 2)
  fact3 = (5 + 3 * t0 + 10 * Q0 - 4 * Q0 * Q0 - 9 * e1sq) * math.pow(dd0, 4) / 24

  fact4 = (61 + 90 * t0 + 298 * Q0 + 45 * t0 * t0 - 252 * e1sq - 3 * Q0 * Q0) * math.pow(dd0, 6) / 720

  lof1 = _a1 / (n0 * k0)
  lof2 = (1 + 2 * t0 + Q0) * math.pow(dd0, 3) / 6.0
  lof3 = (5 - 2 * Q0 + 28 * t0 - 3 * math.pow(Q0, 2) + 8 * e1sq + 24 * math.pow(t0, 2)) * math.pow(dd0, 5) / 120
  _a2 = (lof1 - lof2 + lof3) / math.cos(phi1)
  _a3 = _a2 * 180 / math.pi

  latitude = 180 * (phi1 - fact1 * (fact2 + fact3 + fact4)) / math.pi

  if not northernHemisphere:
      latitude = -latitude

  longitude = ((zone > 0) and (6 * zone - 183.0) or 3.0) - _a3

  return (latitude, longitude)

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
