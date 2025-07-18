def prepare_graph_nodes(intersections_gdf, buildings_gdf, name_col, id_col, precision):
    """
    Combines intersection and building GDFs and prepares node mappings for NetworkX.
    Returns:
        tuple: (node_coords_to_networkx_id, networkx_id_to_details)
    """
    print("Combining all potential graph nodes (intersections + buildings)...")

    # Ensure CRSs match before concatenating
    if intersections_gdf.crs != buildings_gdf.crs:
        print(f"Warning: CRSs of road intersections ({intersections_gdf.crs}) and building layers ({buildings_gdf.crs}) differ. Reprojecting buildings to match intersections.")
        try:
            buildings_gdf = buildings_gdf.to_crs(intersections_gdf.crs)
        except Exception as e:
            print(f"Error reprojecting building layer: {e}")
            print("Continuing without reprojecting, but CRS mismatch might cause issues.")

    all_graph_nodes_gdf = gpd.pd.concat([
        intersections_gdf,
        buildings_gdf
    ]).drop_duplicates(subset=['geometry']).reset_index(drop=True)

    print(f"Total unique potential nodes identified in combined GeoDataFrame: {len(all_graph_nodes_gdf)}")

    if len(all_graph_nodes_gdf) == 0:
        print("Error: No nodes found to build the graph. Cannot proceed.")
        return {}, {} # Return empty mappings

    node_coords_to_networkx_id = {}
    networkx_id_to_details = {}
    current_networkx_id = 0

    for idx, row in all_graph_nodes_gdf.iterrows():
        point_geom = row.geometry
        coords_key = f"{point_geom.x:.{precision}f},{point_geom.y:.{precision}f}"

        # Get name and unique ID from columns specified in config
        qgis_name = row.get(name_col) # Use .get() for safer access
        qgis_unique_id = row.get(id_col) # Use .get() for safer access

        # Handle missing or empty values gracefully
        qgis_name = str(qgis_name).strip() if pd.notna(qgis_name) else f"Unnamed_Node_NX_{current_networkx_id}"
        qgis_unique_id = str(qgis_unique_id).strip() if pd.notna(qgis_unique_id) else f"QGIS_ID_NX_{current_networkx_id}"


        if coords_key not in node_coords_to_networkx_id:
            networkx_id = current_networkx_id
            node_coords_to_networkx_id[coords_key] = networkx_id
            networkx_id_to_details[networkx_id] = {
                'geometry': point_geom,
                'name': qgis_name,
                'qgis_id': qgis_unique_id # This 'qgis_id' key holds the value from your QGIS_UNIQUE_ID_COLUMN ('id')
            }
            current_networkx_id += 1

    print(f"Actual unique nodes after precision matching: {len(node_coords_to_networkx_id)}")
    return node_coords_to_networkx_id, networkx_id_to_details