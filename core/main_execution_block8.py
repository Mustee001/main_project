# --- Main Execution Block ---
if __name__ == "__main__":
    # Load Data
    road_lines_gdf, road_intersections_gdf, main_buildings_gdf = load_geospatial_data(
        ROAD_LINES_FILE, ROAD_INTERSECTIONS_FILE, MAIN_BUILDINGS_FILE
    )

    if road_lines_gdf is None or road_intersections_gdf is None or main_buildings_gdf is None:
        print("Exiting due to data loading errors.")
    else:
        # Prepare Nodes
        node_coords_to_networkx_id, networkx_id_to_details = prepare_graph_nodes(
            road_intersections_gdf, main_buildings_gdf, QGIS_NAME_COLUMN, QGIS_UNIQUE_ID_COLUMN, COORD_PRECISION
        )

        if not node_coords_to_networkx_id: # Check if mappings are empty
            print("Exiting due to no nodes being prepared.")
        else:
            # Build Graph
            G = build_network_graph(road_lines_gdf, node_coords_to_networkx_id, COORD_PRECISION)
            
            # Store CRS in graph for later use
            G.graph['crs'] = road_lines_gdf.crs # Assume road_lines_gdf has the desired CRS now

            # --- Data Summary ---
            print("\n--- Processed Data Summary ---")
            print(f"Initial road intersections loaded: {len(road_intersections_gdf)}")
            print(f"Initial main buildings loaded: {len(main_buildings_gdf)}")
            print(f"Total unique potential nodes identified: {len(node_coords_to_networkx_id)}")
            print(f"NetworkX Graph created with {G.number_of_nodes()} nodes and {G.number_of_edges()} edges.")
            print("------------------------------")
            # --- End Data Summary ---

            # --- Interactive Pathfinding Loop ---
            while True:
                print("\n--- Find Shortest Path ---")
                
                # MODIFIED LINE: Changed "qgis_id" to "id" in the prompt
                user_input_for_search_type = input("Search by 'id' (case-sensitive) or 'name' (case-insensitive)? (default: id): ").strip().lower()
                
                # Internal mapping for search_by type
                if user_input_for_search_type == '' or user_input_for_search_type == 'id':
                    SEARCH_BY_TYPE = 'id' # User sees 'id', and this is passed directly
                elif user_input_for_search_type == 'name':
                    SEARCH_BY_TYPE = 'name'
                else:
                    print("Invalid input. Searching by ID by default.")
                    SEARCH_BY_TYPE = 'id' # Default to 'id' for user display and internal logic

                start_networkx_id = None
                end_networkx_id = None

                # Input loop for Start Node
                while start_networkx_id is None:
                    # The prompt now uses the user-friendly SEARCH_BY_TYPE
                    START_IDENTIFIER = input(f"Enter the {SEARCH_BY_TYPE.upper()} of the START node (or type 'exit' to quit): ").strip()
                    if START_IDENTIFIER.lower() == 'exit':
                        break # Exit the inner loop

                    # Pass SEARCH_BY_TYPE directly to find_networkx_id.
                    # find_networkx_id will now directly handle 'id' or 'name'.
                    start_networkx_id = find_networkx_id(START_IDENTIFIER, networkx_id_to_details, SEARCH_BY_TYPE)
                    if start_networkx_id is None:
                        print(f"Error: Start node '{START_IDENTIFIER}' not found. Please try again with a valid {SEARCH_BY_TYPE.upper()}.")
                
                if start_networkx_id is None: # If user typed 'exit' for start node
                    print("Exiting pathfinding session.")
                    break # Exit the main while True loop

                # Input loop for End Node
                while end_networkx_id is None:
                    # The prompt now uses the user-friendly SEARCH_BY_TYPE
                    END_IDENTIFIER = input(f"Enter the {SEARCH_BY_TYPE.upper()} of the END node (or type 'exit' to quit): ").strip()
                    if END_IDENTIFIER.lower() == 'exit':
                        break # Exit the inner loop

                    # Pass SEARCH_BY_TYPE directly to find_networkx_id
                    end_networkx_id = find_networkx_id(END_IDENTIFIER, networkx_id_to_details, SEARCH_BY_TYPE)
                    if end_networkx_id is None:
                        print(f"Error: End node '{END_IDENTIFIER}' not found. Please try again with a valid {SEARCH_BY_TYPE.upper()}.")

                if end_networkx_id is None: # If user typed 'exit' for end node
                    print("Exiting pathfinding session.")
                    break # Exit the main while True loop

                # Proceed to find and print path if both nodes are found
                # Pass SEARCH_BY_TYPE directly
                find_and_print_path(G, START_IDENTIFIER, END_IDENTIFIER, SEARCH_BY_TYPE, networkx_id_to_details)

                # Option to find another path or exit
                another_path = input("\nDo you want to find another path? (yes/no): ").strip().lower()
                if another_path != 'yes':
                    print("Exiting pathfinding session. Goodbye!")
                    break
