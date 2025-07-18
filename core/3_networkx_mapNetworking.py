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