# 🚦 PLP/BFS Software Engineering Path: Shortest Path in a Road Network

## 📌 Project Overview

This project implements a **Breadth-First Search (BFS)** algorithm to find the **shortest path in a real-world road network**—specifically, the road map of **Ibrahim Badamasi Babangida University, Lapai (IBBUL)**. It is part of the broader **PLP/BFS Software Engineering Path**, combining software engineering, data processing, and geospatial thinking.

The system reads raw road node data, builds a graph network, and allows users to interactively select start and end points to compute the shortest path.

## 🌍 Tools and Technologies

- **Python 3**
- **NetworkX**: For graph modeling and traversal
- **Matplotlib**: For visualizing the map and paths
- **CSV**: For storing and loading road nodes
- **OpenStreetMap (OSM)**: For raw road mapping and coordinates (data was collected from OSM)
- **Standard Python libraries**: `os`, `sys`, `csv`, etc.

## 📂 Project Structure

```
main_project/
│
├── core/
│   ├── data_loader.py              # Load CSV map node data
│   ├── map_plotter.py              # Plot the entire node map
│   ├── graph_constructor.py        # Construct graph using nodes and distances
│   ├── bfs_pathfinder.py           # Find shortest path using BFS
│   └── interactive_runner.py       # Handles input and output flow
│
└── main.py                         # Main script to run the entire process
```

## 🔧 How It Works

1. **Load Data**  
   Loads road network data from a CSV file into memory. Each line represents a node and its connected neighbors.

2. **Plot Map**  
   The node coordinates are used to draw a visual representation of the road network.

3. **Construct Graph**  
   Converts the nodes into a graph using **NetworkX**, where nodes are points on the map and edges represent roads.

4. **BFS Shortest Path**  
   Implements the **Breadth-First Search (BFS)** algorithm to find the shortest path between two nodes (by number of steps, not physical distance).

5. **Run Interactively**  
   Users can input a start and end node to see the shortest route plotted on the map.

## 🚀 How to Run

1. Clone this repository:
   ```bash
   git clone https://github.com/Mustee001/main_project.git
   cd main_project
   ```

2. Make sure all dependencies are installed:
   ```bash
   pip install networkx matplotlib
   ```

3. Run the project:
   ```bash
   python main.py
   ```

## 📸 Sample Output

- Full map with nodes plotted  
- Start and end points highlighted  
- Shortest path drawn in a different color  

*(Add sample screenshots later if needed)*

## 📎 Credits

- Map data from **OpenStreetMap**
- Project by **Mustapha Musa (Mustee)**

## 🧠 Notes

- BFS does not consider physical distance but steps. You can extend this with Dijkstra or A* later.
- Data must be cleaned before loading (ensure correct CSV structure).

## 🛠️ Future Improvements

- Switch to weighted graphs using physical distances
- Build a web or mobile frontend (maybe using Flutter)
- Add GPS-based node detection for real-time use

## 📄 License

This project is for learning and academic use under the MIT License.
