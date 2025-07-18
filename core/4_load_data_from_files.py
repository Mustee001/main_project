# --- Main Functions for Geospatial Graph Processing ---

def load_geospatial_data(road_lines_path, intersections_path, buildings_path):
    """
    Loads geospatial data from specified GeoJSON files.
    Returns:
        tuple: (road_lines_gdf, road_intersections_gdf, main_buildings_gdf)
    """
    print("Loading geospatial data...")
    try:
        road_lines_gdf = gpd.read_file(road_lines_path)
        road_intersections_gdf = gpd.read_file(intersections_path)
        main_buildings_gdf = gpd.read_file(buildings_path)
        print("Geospatial data loaded successfully.")
        return road_lines_gdf, road_intersections_gdf, main_buildings_gdf
    except Exception as e:
        print(f"Error loading geospatial files. Please check paths and file integrity: {e}")
        return None, None, None