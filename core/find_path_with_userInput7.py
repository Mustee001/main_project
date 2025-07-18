def find_and_print_path(graph, start_id_str, end_id_str, search_type, networkx_id_to_details):
    """
    Finds and prints the shortest path between two identifiers,
    with a summary header and detailed output.
    """
    print("\n--- Calculating Shortest Path ---")

    # Pass search_type directly to find_networkx_id
    start_networkx_id = find_networkx_id(start_id_str, networkx_id_to_details, search_by=search_type)
    end_networkx_id = find_networkx_id(end_id_str, networkx_id_to_details, search_by=search_type)

    # These checks are now handled by the calling interactive loop, but kept for standalone function clarity
    if start_networkx_id is None:
        print(f"Error: Start node '{start_id_str}' not found in graph using '{search_type}'. Please check your data for exact ID/Name.")
        return
    if end_networkx_id is None:
        print(f"Error: End node '{end_id_str}' not found in graph using '{search_type}'. Please check your data for exact ID/Name.")
        return

    # Get names for summary output
    start_node_name = networkx_id_to_details[start_networkx_id]['name']
    start_node_qgis_id = networkx_id_to_details[start_networkx_id]['qgis_id']
    end_node_name = networkx_id_to_details[end_networkx_id]['name']
    end_node_qgis_id = networkx_id_to_details[end_networkx_id]['qgis_id']


    if start_networkx_id == end_networkx_id:
        print(f"Your start and end locations are the same: '{start_node_name}' (Unique ID: {start_node_qgis_id}).")
        print("\n--- Journey Details ---")
        print(f"Step 1: You are already at: '{start_node_name}' (Unique ID: {start_node_qgis_id}) at coordinates ({networkx_id_to_details[start_networkx_id]['geometry'].x:.{COORD_PRECISION}f}, {networkx_id_to_details[start_networkx_id]['geometry'].y:.{COORD_PRECISION}f}).")
        print("Journey complete!")
        return
    else:
        print(f"\nSearching for path from '{start_node_name}' (Unique ID: {start_node_qgis_id}) to '{end_node_name}' (Unique ID: {end_node_qgis_id}).")
        path_networkx_ids = bfs_shortest_path(graph, start_networkx_id, end_networkx_id)

        if path_networkx_ids:
            # --- Summary Output ---
            path_qgis_ids = [networkx_id_to_details[nx_id]['qgis_id'] for nx_id in path_networkx_ids]
            print(f"\nPath found:")
            print(f"Start location identifier: {start_node_qgis_id}; Name: \"{start_node_name}\"")
            print(f"Destination identifier: {end_node_qgis_id}; Name: \"{end_node_name}\"")
            print(f"BFS shortest path (sequence of Node IDs): {path_qgis_ids}")
            # --- End Summary Output ---

            print("\n--- Step-by-Step Directions ---")
            print(f"This journey will take {len(path_networkx_ids) - 1} steps (road segments).")

            for i in range(len(path_networkx_ids)):
                current_node_id = path_networkx_ids[i]
                node_info = networkx_id_to_details[current_node_id]

                print(f"Step {i+1}: Arrive at '{node_info['name']}' (Node ID: {node_info['qgis_id']}) at coordinates ({node_info['geometry'].x:.{COORD_PRECISION}f}, {node_info['geometry'].y:.{COORD_PRECISION}f}).")


                if i < len(path_networkx_ids) - 1:
                    next_node_id = path_networkx_ids[i+1]
                    if graph.has_edge(current_node_id, next_node_id):
                        edge_data = graph.get_edge_data(current_node_id, next_node_id)
                        line_description = edge_data.get('description', 'an unnamed path')
                        print(f"    - From here, proceed along '{line_description}' towards the next location.")
                    else:
                        print(f"    - WARNING: No direct road description found between '{node_info['name']}' and '{networkx_id_to_details[next_node_id]['name']}'.")
            print("\nJourney complete!")

        else:
            print(f"\nNo continuous path found between '{start_node_name}' and '{end_node_name}'.")
            print("This means there's no continuous route through the network from your starting point to your destination.")
            print("This could happen if:")
            print("  - Your start or end locations are isolated from the main road network.")
            print("  - There are gaps or missing connections in the road data.")
            print("Please verify the entered unique identifiers or names.")