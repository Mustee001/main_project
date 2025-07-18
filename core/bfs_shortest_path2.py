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