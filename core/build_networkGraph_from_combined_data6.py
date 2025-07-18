def build_network_graph(road_lines_gdf, node_coords_to_networkx_id, precision):
    """
    Builds a NetworkX graph from road lines and node mappings.
    Returns:
        networkx.Graph: The constructed graph.
    """
    print("Building the NetworkX graph...")
    G = nx.Graph()

    # Add all nodes that were identified
    G.add_nodes_from(node_coords_to_networkx_id.values())

    for idx, row in road_lines_gdf.iterrows():
        line_geom = row.geometry
        line_description = row['description'] if 'description' in row and pd.notna(row['description']) else 'unnamed path'

        if isinstance(line_geom, LineString):
            lines_to_process = [line_geom]
        elif isinstance(line_geom, MultiLineString):
            lines_to_process = list(line_geom.geoms)
        else:
            continue

        for single_line in lines_to_process:
            start_point_coords = single_line.coords[0]
            end_point_coords = single_line.coords[-1]

            start_key = f"{start_point_coords[0]:.{precision}f},{start_point_coords[1]:.{precision}f}"
            end_key = f"{end_point_coords[0]:.{precision}f},{end_point_coords[1]:.{precision}f}"

            u = node_coords_to_networkx_id.get(start_key)
            v = node_coords_to_networkx_id.get(end_key)

            if u is not None and v is not None and u != v:
                G.add_edge(u, v, geometry=single_line, description=str(line_description).strip())

    print(f"NetworkX graph built: {G.number_of_nodes()} nodes, {G.number_of_edges()} edges.")
    return G