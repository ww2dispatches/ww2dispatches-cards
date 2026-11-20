"""Georeference of the HQ Twelfth Army Group situation map scans (LOC, 1:1,000,000), from the printed graticule.
Full scan pixel coordinates. Checked on 25 Dec 1944 (item 2004630297) against towns across the sheet, within about 2 km."""
import math
X6, Y50, PXKM = 3713.0, 3017.0, 12.09
def px(lon, lat):
    return (X6 + (lon - 6) * 111.32 * math.cos(math.radians(lat)) * PXKM, Y50 - (lat - 50) * 110.6 * PXKM)
def ll(x, y):
    lat = 50 + (Y50 - y) / (110.6 * PXKM)
    return (6 + (x - X6) / (111.32 * math.cos(math.radians(lat)) * PXKM), lat)
