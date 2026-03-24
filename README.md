# Tree Solver

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

## Demo Videos

### Breadth-First Search (BFS)

Put the video here

### Depth-First Search (DFS)

Put the video here

## Requirements

- Python 3.x
- PyQt6
