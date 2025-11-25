import math
import requests
import xml.etree.ElementTree as ET

MTO_XML_BASE = "https://idfcurves.mto.gov.on.ca/data_xml/"

def to_grid_coordinate(coord: float) -> float:
    """
    Recreates the MTO JavaScript toGridCoordinate() rounding to 30-second grid.
    """
    negative = coord < 0
    if negative:
        coord = -coord

    d = int(coord)
    minutes_float = (coord - d) * 60
    m = int(minutes_float)
    seconds_float = (minutes_float - m) * 60
    s = int(seconds_float)

    # round seconds to either 30" or 60" bucket
    if s < 30:
        coord = d + m / 60 + 1 / 240   # 1/240 deg = 15 arcsec; they then floor at 6 decimals
    else:
        coord = d + m / 60 + 1 / 80    # 1/80 deg = 45 arcsec

    if negative:
        coord = -coord

    return float(f"{coord:.6f}")


def get_idf_depth(lat: float, lon: float, duration_hours: float = 12, return_period: int = 2) -> float:
    """
    Get rainfall depth (mm) from MTO IDF data for a given lat/lon, duration (hours),
    and return period (years).
    """
    # Snap to the same grid MTO uses
    grid_lat = to_grid_coordinate(lat)
    grid_lon = to_grid_coordinate(lon)

    # XML file is based only on the snapped latitude
    xml_url = f"{MTO_XML_BASE}{grid_lat:.6f}.xml"

    resp = requests.get(xml_url, timeout=20)
    resp.raise_for_status()

    root = ET.fromstring(resp.text)

    # coord id uses snapped lat and lon
    coord_id = f"{grid_lat:.6f},{grid_lon:.6f}"
    coord_elem = root.find(f".//coord[@id='{coord_id}']")
    if coord_elem is None:
        raise ValueError(f"No coord found for {coord_id} in {xml_url}")

    period_elem = coord_elem.find(f"./period[@id='{return_period}']")
    if period_elem is None:
        raise ValueError(f"No period {return_period}yr found for coord {coord_id}")

    a = float(period_elem.attrib["a"])
    b = float(period_elem.attrib["b"])

    # MTO formula (from their JS):
    # depth (mm) = a * t^(b + 1), where t is in hours
    t = float(duration_hours)
    depth_mm = a * (t ** (b + 1))

    return round(depth_mm, 2)
