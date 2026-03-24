# Tree Solver - Design Specification

## 1. Project Overview

**Project Name:** Tree Solver  
**Project Type:** Desktop Application (Python + PyQt6)  
**Core Functionality:** Interactive graphical tool for creating, visualizing, and solving tree structures using uninformed search algorithms (BFS/DFS).  
**Target Users:** Students learning graph theory, educators teaching search algorithms.

---

## 2. UI/UX Specification

### 2.1 Window Layout

*   **Main Window:** Single window application (800x600 minimum, resizable)
*   **Toolbar:** Horizontal toolbar at top with action buttons
*   **Canvas:** Central `QGraphicsView` area for node/edge manipulation
*   **Status Bar:** Bottom bar showing current state/instructions

### 2.2 Visual Design

*   **Background:** Light gray (#f0f0f0)
*   **Node Default:** White circle with black border
*   **Node Goal:** Green border (#27ae60)
*   **Node Selected:** Blue border (#3498db)
*   **Edge Color:** Black arrows
*   **BFS/DFS Animation Colors:**
    *   Unvisited: White (#ffffff)
    *   Visiting (frontier): Yellow (#f1c40f)
    *   Visited: Gray (#bdc3c7)
    *   Final Path: Green (#27ae60)

### 2.3 Components

*   **Toolbar Buttons:**
    *   "Add Node" - Creates new node at click position
    *   "Connect" - Enter connection mode to draw edges
    *   "Solve BFS" - Run Breadth-First Search
    *   "Solve DFS" - Run Depth-First Search
    *   "Clear" - Reset canvas

*   **Node Interaction:**
    *   Left-click + drag: Move node
    *   Double-click: Edit node name
    *   Right-click: Context menu (Mark as Goal, Delete)

*   **Edge Interaction:**
    *   Shift + drag from node to node: Create directed connection

---

## 3. Functionality Specification

### 3.1 Core Features

1.  **Node Management**
    *   Add nodes to canvas via toolbar button
    *   Default name: "Node N" (incrementing counter)
    *   Edit name via double-click dialog
    *   Delete via right-click menu
    *   Drag-and-drop positioning

2.  **Edge Management**
    *   Create directed edges (Parent → Child)
    *   Shift + drag from source to target
    *   Visual arrow showing direction

3.  **Tree Validation (Pre-solve)**
    *   Check: Exactly one start node (0 incoming edges)
    *   Check: Exactly one goal node marked
    *   Check: No cycles present
    *   Check: All nodes reachable from start

4.  **Search Algorithms (Generators)**
    *   BFS: Explores level by level
    *   DFS: Explores depth-first
    *   Yield states: visiting, visited, found_goal
    *   Track path for reconstruction

5.  **Animation System**
    *   QTimer fires every 500ms
    *   Reads next step from generator
    *   Updates node/edge colors accordingly
    *   Stops when goal found or frontier empty

6.  **Results Display**
    *   Highlight final path in green
    *   Show popup with path string: "Start → A → B → Goal"

### 3.2 Data Flow

```
User draws on canvas → Build Graph Dict → Validate → Run Generator → QTimer consumes steps → Update UI colors → Show Result
```

### 3.3 Architecture (Approach 1)

*   **Model Layer:** Pure Python graph representation (`dict`)
*   **View Layer:** PyQt6 QGraphicsScene/QGraphicsView
*   **Controller:** MainWindow orchestrating interactions
*   **Algorithm Layer:** Generator functions for BFS/DFS

---

## 4. Acceptance Criteria

1.  User can add, rename, move, and delete nodes
2.  User can create directed edges between nodes
3.  User can mark exactly one node as Goal
4.  Solve button validates tree before running
5.  Animation visibly shows BFS/DFS exploration order
6.  Final path highlighted in green
7.  Popup displays the found path
8.  Error popups for invalid trees (no start, no goal, cycles, disconnected)

---

## 5. File Structure

```
tree-solver/
├── main.py              # Application entry point
├── node_item.py         # Node graphics item class
├── edge_item.py         # Edge graphics item class
├── algorithms.py        # BFS/DFS generator functions
├── validator.py         # Tree validation logic
└── main_window.py       # Main window and UI logic
```
