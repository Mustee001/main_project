import geopandas as gpd
import networkx as nx
from shapely.geometry import LineString, MultiLineString, Point
from collections import deque
import pandas as pd

# --- Configuration: SET YOUR FILE PATHS AND COLUMN NAMES HERE ---
ROAD_LINES_FILE = "ROAD_NETWORK_finale.geojson"
ROAD_INTERSECTIONS_FILE = "all_intersections_pro.geojson"
MAIN_BUILDINGS_FILE = "all_school_buildings_pro.geojson"

QGIS_NAME_COLUMN = 'Name'
QGIS_UNIQUE_ID_COLUMN = 'id' # IMPORTANT: Set to 'id' (lowercase) to match QGIS export

COORD_PRECISION = 6

# --- Helper Function: Breadth-First Search (BFS) Algorithm ---
def bfs_shortest_path(graph, start_node, end_node):
    """
    Finds the shortest path in an unweighted graph using BFS.
    Returns a list of NetworkX node IDs forming the path, or None if no path.
    """
    if start_node == end_node:
        return [start_node]
    if start_node not in graph or end_node not in graph:
        return None

    queue = deque([(start_node, [start_node])])
    visited = {start_node}

    while queue:
        current_node, path = queue.popleft()

        if current_node == end_node:
            return path

        for neighbor in graph.neighbors(current_node):
            if neighbor not in visited:
                visited.add(neighbor)
                queue.append((neighbor, path + [neighbor]))
    return None

# --- Helper Function: Find NetworkX ID from QGIS ID or Name ---
# MODIFICATION: Changed how search_by is handled within this function
def find_networkx_id(identifier, details_dict, search_by='id'): # Default search_by to 'id'
    """
    Finds the NetworkX node ID given a QGIS ID (from 'id' column) or Name.
    Args:
        identifier (str): The QGIS 'id' or 'Name' to search for.
        details_dict (dict): The networkx_id_to_details dictionary.
        search_by (str): 'id' or 'name' to specify which attribute to search.
                         'id' directly corresponds to the 'qgis_id' key in details_dict,
                         which stores values from QGIS_UNIQUE_ID_COLUMN.
    Returns:
        int: The corresponding NetworkX node ID, or None if not found.
    """
    stripped_identifier = str(identifier).strip()
    for networkx_id, details in details_dict.items():
        # The 'qgis_id' key in details_dict stores values from QGIS_UNIQUE_ID_COLUMN ('id')
        if search_by == 'id': # Directly check for 'id' from user input
            # Case-sensitive matching for QGIS_ID (from the 'id' column)
            if details['qgis_id'] == stripped_identifier:
                return networkx_id
        elif search_by == 'name':
            # Name matching remains case-insensitive
            if details['name'].lower() == stripped_identifier.lower():
                return networkx_id
    return None

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
