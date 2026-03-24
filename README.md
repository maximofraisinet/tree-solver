# Tree Solver

Artificial Intelligence Project - UTN-FRCU Universidad Tecnológica Nacional - Facultad Regional Concepción del Uruguay

An interactive desktop application for visualizing and solving tree search algorithms.

## Installation

```bash
pip install PyQt6
```

## Usage

```bash
python main.py
```

### Controls

- **Add Node**: Creates a new node on the canvas
- **Connect Nodes**: Links a parent node to a child node
- **Set Start**: Marks the starting node (blue border)
- **Set Goal**: Marks the target node (green border)
- **Solve BFS**: Runs Breadth-First Search
- **Solve DFS**: Runs Depth-First Search
- **Clear**: Removes all nodes and edges
- **Drag**: Move nodes around the canvas
- **Right-click**: Context menu (Mark Goal/Start, Delete)

### Visual Design

- **Background**: Light gray (#f0f0f0)
- **Node Default**: White circle with black border
- **Node Goal**: Green border (#27ae60)
- **Node Selected**: Blue border (#3498db)
- **Edge Color**: Black arrows

### Algorithm Visualization Colors

- **Unvisited**: White (#ffffff)
- **Visiting (frontier)**: Yellow (#f1c40f)
- **Visited**: Gray (#bdc3c7)
- **Final Path**: Green (#27ae60)

## Algorithms

### Breadth-First Search (BFS)

Explores the tree level by level. Always expands the shallowest unexpanded node.

**Workflow:**
1. Start at the root node
2. Add all children to a queue
3. Process first node in queue
4. Add its children to the end of queue
5. Repeat until goal is found

BFS always finds the shortest path in an unweighted tree.

### Depth-First Search (DFS)

Explores as far as possible along each branch before backtracking.

**Workflow:**
1. Start at the root node
2. Add all children to a stack
3. Process first node in stack
4. Add its children to the beginning of stack
5. Repeat until goal is found

## Architecture

- **Model Layer**: Pure Python graph representation (dict)
- **View Layer**: PyQt6 QGraphicsScene/QGraphicsView
- **Controller**: MainWindow orchestrating interactions
- **Algorithm Layer**: Generator functions for BFS/DFS

## Validation

Before solving, the app validates:
- Exactly one start node (0 incoming edges)
- Exactly one goal node marked
- No cycles present
- All nodes reachable from start

## Demo Videos

### Breadth-First Search (BFS)

https://github.com/user-attachments/assets/c0efc27a-13da-4041-9433-8636646a2e44

<img width="1195" height="429" alt="BFS" src="https://github.com/user-attachments/assets/1f61af21-5ff0-4798-a9e8-4e028e32bb74" />

### Depth-First Search (DFS)

https://github.com/user-attachments/assets/48e558f8-8a3a-45b7-ac66-22c0018e4c75

<img width="1201" height="426" alt="DFS" src="https://github.com/user-attachments/assets/38d65931-a29e-4429-ba57-ba8703843563" />

## Requirements

- Python 3.x
- PyQt6