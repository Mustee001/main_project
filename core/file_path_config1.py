import geopandas as gpd
import networkx as nx
from shapely.geometry import LineString, MultiLineString, Point
from collections import deque
import pandas as pd

# --- Configuration: SET YOUR FILE PATHS AND COLUMN NAMES HERE ---
ROAD_LINES_FILE = "ROAD_NETWORK_finale.geojson"
ROAD_INTERSECTIONS_FILE = "all intersections pro.geojson"
MAIN_BUILDINGS_FILE = "all school buildings pro.geojson"

QGIS_NAME_COLUMN = 'Name'
QGIS_UNIQUE_ID_COLUMN = 'id' # IMPORTANT: Set to 'id' (lowercase) to match QGIS export

COORD_PRECISION = 6