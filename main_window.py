"""
Main window for the Tree Solver application.
Handles UI, interactions, and animation orchestration.
"""

from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QToolBar, QHBoxLayout,
    QGraphicsView, QGraphicsScene, QMessageBox, QDialog, QGridLayout,
    QLabel, QPushButton, QMenu, QButtonGroup, QDialogButtonBox
)
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QPen, QColor, QPainter, QAction

from node_item import NodeItem
from edge_item import EdgeItem
from algorithms import bfs_generator, dfs_generator
from validator import validate_tree, build_graph_from_scene, ValidationError


class ConnectDialog(QDialog):
    """Dialog for selecting parent and child nodes visually."""
    
    def __init__(self, nodes, parent=None):
        super().__init__(parent)
        self.nodes = nodes
        self.parent_node = None
        self.child_node = None
        self.setWindowTitle("Connect Nodes")
        self.setMinimumSize(400, 300)
        
        layout = QVBoxLayout(self)
        
        layout.addWidget(QLabel("Select PARENT node:"))
        self.parent_group = QButtonGroup(self)
        parent_layout = QGridLayout()
        
        cols = 4
        for i, node in enumerate(nodes):
            row = i // cols
            col = i % cols
            btn = QPushButton(node.get_name())
            btn.setCheckable(True)
            btn.clicked.connect(lambda checked, n=node: self.select_parent(n))
            self.parent_group.addButton(btn)
            parent_layout.addWidget(btn, row, col)
        
        layout.addLayout(parent_layout)
        
        layout.addWidget(QLabel("Select CHILD node:"))
        self.child_group = QButtonGroup(self)
        child_layout = QGridLayout()
        
        for i, node in enumerate(nodes):
            row = i // cols
            col = i % cols
            btn = QPushButton(node.get_name())
            btn.setCheckable(True)
            btn.setEnabled(False)
            btn.clicked.connect(lambda checked, n=node: self.select_child(n))
            self.child_group.addButton(btn)
            child_layout.addWidget(btn, row, col)
        
        self.child_buttons = child_layout
        layout.addLayout(child_layout)
        
        self.selected_label = QLabel("No connection selected")
        layout.addWidget(self.selected_label)
        
        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)
    
    def select_parent(self, node):
        for btn in self.parent_group.buttons():
            btn.setEnabled(False)
        
        for btn in self.child_group.buttons():
            if btn.text() != node.get_name():
                btn.setEnabled(True)
        
        self.parent_node = node
        self.update_label()
    
    def select_child(self, node):
        for btn in self.child_group.buttons():
            btn.setEnabled(False)
        
        self.child_node = node
        self.update_label()
    
    def update_label(self):
        if self.parent_node and self.child_node:
            self.selected_label.setText(f"Connect: {self.parent_node.get_name()} -> {self.child_node.get_name()}")
        elif self.parent_node:
            self.selected_label.setText(f"Parent: {self.parent_node.get_name()} (now select child)")
        else:
            self.selected_label.setText("No connection selected")


class SelectNodeDialog(QDialog):
    """Dialog for selecting a node visually."""
    
    def __init__(self, nodes, title, instruction, exclude_node=None, parent=None):
        super().__init__(parent)
        self.nodes = nodes
        self.selected_node = None
        self.exclude_node = exclude_node
        self.setWindowTitle(title)
        self.setMinimumSize(400, 300)
        
        layout = QVBoxLayout(self)
        
        layout.addWidget(QLabel(instruction))
        
        self.button_group = QButtonGroup(self)
        button_layout = QGridLayout()
        
        cols = 4
        filtered_nodes = [n for n in nodes if n != exclude_node]
        
        for i, node in enumerate(filtered_nodes):
            row = i // cols
            col = i % cols
            btn = QPushButton(node.get_name())
            btn.setCheckable(True)
            btn.clicked.connect(lambda checked, n=node: self.select_node(n))
            self.button_group.addButton(btn)
            button_layout.addWidget(btn, row, col)
        
        layout.addLayout(button_layout)
        
        self.selected_label = QLabel("No node selected")
        layout.addWidget(self.selected_label)
        
        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)
    
    def select_node(self, node):
        for btn in self.button_group.buttons():
            btn.setEnabled(False)
        
        self.selected_node = node
        self.selected_label.setText(f"Selected: {node.get_name()}")


class MainWindow(QMainWindow):
    """Main application window."""
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Tree Solver - Graph Search Visualizer")
        self.setGeometry(100, 100, 1000, 700)
        
        self.node_counter = 0
        self.solving = False
        self.solver_generator = None
        self.animation_timer = None
        self.start_node = None
        
        self._setup_ui()
    
    def _setup_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        layout = QVBoxLayout(central_widget)
        
        toolbar = QToolBar()
        toolbar.setMovable(False)
        self.addToolBar(toolbar)
        
        self.add_node_btn = QPushButton("Add Node")
        self.add_node_btn.clicked.connect(self.add_node_at_center)
        toolbar.addWidget(self.add_node_btn)
        
        self.connect_btn = QPushButton("Connect Nodes")
        self.connect_btn.clicked.connect(self.connect_nodes_dialog)
        toolbar.addWidget(self.connect_btn)
        
        toolbar.addSeparator()
        
        self.set_start_btn = QPushButton("Set Start")
        self.set_start_btn.clicked.connect(self.set_start_dialog)
        toolbar.addWidget(self.set_start_btn)
        
        self.set_goal_btn = QPushButton("Set Goal")
        self.set_goal_btn.clicked.connect(self.set_goal_dialog)
        toolbar.addWidget(self.set_goal_btn)
        
        toolbar.addSeparator()
        
        self.solve_bfs_btn = QPushButton("Solve BFS")
        self.solve_bfs_btn.clicked.connect(lambda: self.solve_tree("BFS"))
        toolbar.addWidget(self.solve_bfs_btn)
        
        self.solve_dfs_btn = QPushButton("Solve DFS")
        self.solve_dfs_btn.clicked.connect(lambda: self.solve_tree("DFS"))
        toolbar.addWidget(self.solve_dfs_btn)
        
        toolbar.addSeparator()
        
        self.clear_btn = QPushButton("Clear")
        self.clear_btn.clicked.connect(self.clear_canvas)
        toolbar.addWidget(self.clear_btn)
        
        self.scene = QGraphicsScene(self)
        self.scene.setSceneRect(-500, -350, 1000, 700)
        self.scene.setBackgroundBrush(QColor("#f0f0f0"))
        
        self.view = QGraphicsView(self.scene, self)
        self.view.setRenderHint(QPainter.RenderHint.Antialiasing)
        self.view.setDragMode(QGraphicsView.DragMode.ScrollHandDrag)
        self.view.setTransformationAnchor(QGraphicsView.ViewportAnchor.AnchorUnderMouse)
        self.view.setResizeAnchor(QGraphicsView.ViewportAnchor.AnchorUnderMouse)
        
        layout.addWidget(self.view)
        
        self.status_label = QLabel("Add nodes, then use Connect to link them. Set Start/Goal nodes.")
        layout.addWidget(self.status_label)
        
        self.view.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.view.customContextMenuRequested.connect(self.show_context_menu)
    
    def show_context_menu(self, pos):
        scene_pos = self.view.mapToScene(pos)
        item = self.scene.itemAt(scene_pos, self.view.transform())
        
        if isinstance(item, NodeItem):
            menu = QMenu()
            goal_action = menu.addAction("Mark as Goal" if not item.is_goal_node() else "Unmark Goal")
            start_action = menu.addAction("Mark as Start" if item != self.start_node else "Unmark Start")
            delete_action = menu.addAction("Delete Node")
            
            action = menu.exec(self.view.mapToGlobal(pos))
            
            if action == goal_action:
                item.set_as_goal(not item.is_goal_node())
                for node in self.scene.items():
                    if isinstance(node, NodeItem) and node != item:
                        if node.is_goal_node():
                            node.set_as_goal(False)
            elif action == start_action:
                if self.start_node == item:
                    self.start_node = None
                    item.set_is_start(False)
                else:
                    if self.start_node:
                        self.start_node.set_is_start(False)
                    self.start_node = item
                    item.set_is_start(True)
            elif action == delete_action:
                if item == self.start_node:
                    self.start_node = None
                edges_to_remove = [e for e in self.scene.items() if isinstance(e, EdgeItem) 
                                   if item in e.get_nodes()]
                for edge in edges_to_remove:
                    edge.remove_from_nodes()
                    self.scene.removeItem(edge)
                self.scene.removeItem(item)
    
    def add_node_at_center(self):
        self.node_counter += 1
        node_name = f"Node{self.node_counter}"
        
        view_center = self.view.mapToScene(self.view.viewport().rect().center())
        node = NodeItem(node_name, view_center.x(), view_center.y(), self.scene)
        
        self.scene.addItem(node)
        self.status_label.setText(f"Added {node_name}. Drag to move.")
    
    def connect_nodes_dialog(self):
        nodes = [item for item in self.scene.items() if isinstance(item, NodeItem)]
        
        if len(nodes) < 2:
            QMessageBox.warning(self, "Error", "You need at least 2 nodes to create a connection.")
            return
        
        dialog = ConnectDialog(nodes, self)
        
        if dialog.exec() == QDialog.DialogCode.Accepted:
            if dialog.parent_node and dialog.child_node:
                self.create_edge(dialog.parent_node, dialog.child_node)
    
    def set_start_dialog(self):
        nodes = [item for item in self.scene.items() if isinstance(item, NodeItem)]
        
        if not nodes:
            QMessageBox.warning(self, "Error", "Add some nodes first!")
            return
        
        dialog = SelectNodeDialog(nodes, "Set Start Node", "Select the START node:", parent=self)
        
        if dialog.exec() == QDialog.DialogCode.Accepted:
            if dialog.selected_node:
                if self.start_node:
                    self.start_node.set_is_start(False)
                self.start_node = dialog.selected_node
                dialog.selected_node.set_is_start(True)
                self.status_label.setText(f"Start node set to: {dialog.selected_node.get_name()}")
    
    def set_goal_dialog(self):
        nodes = [item for item in self.scene.items() if isinstance(item, NodeItem)]
        
        if not nodes:
            QMessageBox.warning(self, "Error", "Add some nodes first!")
            return
        
        dialog = SelectNodeDialog(nodes, "Set Goal Node", "Select the GOAL node:", parent=self)
        
        if dialog.exec() == QDialog.DialogCode.Accepted:
            if dialog.selected_node:
                for node in nodes:
                    node.set_as_goal(False)
                dialog.selected_node.set_as_goal(True)
                self.status_label.setText(f"Goal node set to: {dialog.selected_node.get_name()}")
    
    def create_edge(self, parent_node, child_node):
        name_a = parent_node.get_name()
        name_b = child_node.get_name()
        
        for item in self.scene.items():
            if isinstance(item, EdgeItem):
                nodes = item.get_nodes()
                if (nodes[0].get_name(), nodes[1].get_name()) == (name_a, name_b):
                    QMessageBox.warning(self, "Warning", "Connection already exists!")
                    return
        
        edge = EdgeItem(parent_node, child_node)
        self.scene.addItem(edge)
        self.status_label.setText(f"Connected: {name_a} -> {name_b}")
    
    def clear_canvas(self):
        self.stop_animation()
        self.scene.clear()
        self.node_counter = 0
        self.start_node = None
        self.status_label.setText("Canvas cleared.")
    
    def solve_tree(self, algorithm: str):
        if self.solving:
            return
        
        nodes = [item for item in self.scene.items() if isinstance(item, NodeItem)]
        edges = [item for item in self.scene.items() if isinstance(item, EdgeItem)]
        
        print(f"\n{'='*50}")
        print(f"SOLVE TREE - {algorithm}")
        print(f"{'='*50}")
        
        if not nodes:
            print("ERROR: No nodes in canvas")
            QMessageBox.warning(self, "Error", "Add some nodes first!")
            return
        
        if not self.start_node:
            print("ERROR: No start node set")
            QMessageBox.warning(self, "Error", "Set a start node first!")
            return
        
        goal_node = None
        for node in nodes:
            if node.is_goal_node():
                goal_node = node.get_name()
                break
        
        if not goal_node:
            print("ERROR: No goal node set")
            QMessageBox.warning(self, "Error", "Set a goal node first!")
            return
        
        print(f"Start node: {self.start_node.get_name()}")
        print(f"Goal node: {goal_node}")
        print(f"Total nodes: {len(nodes)}")
        print(f"Total edges: {len(edges)}")
        
        print(f"\nEdges in graph:")
        for edge in edges:
            print(f"  {edge.get_source_name()} -> {edge.get_target_name()}")
        
        try:
            graph, _ = build_graph_from_scene(nodes, edges)
            print(f"\nGraph adjacency list:")
            for node, neighbors in graph.items():
                if neighbors:
                    print(f"  {node} -> {neighbors}")
            
            user_start = self.start_node.get_name()
            start_node, _ = validate_tree(graph, goal_node, user_start)
            print(f"\n✓ VALIDATION PASSED!")
            print(f"  Start: {start_node}")
            print(f"  Goal: {goal_node}")
        except ValidationError as e:
            print(f"\n✗ VALIDATION FAILED: {e}")
            QMessageBox.warning(self, "Validation Error", str(e))
            return
        
        self.status_label.setText(f"Running {algorithm}...")
        
        if algorithm == "BFS":
            self.solver_generator = bfs_generator(graph, start_node, goal_node)
        else:
            self.solver_generator = dfs_generator(graph, start_node, goal_node)
        
        self.solving = True
        self._reset_visual_states()
        
        self.animation_timer = QTimer()
        self.animation_timer.timeout.connect(lambda: self._animation_step(goal_node))
        self.animation_timer.start(500)
    
    def _reset_visual_states(self):
        for item in self.scene.items():
            if isinstance(item, NodeItem):
                item.reset_visual_state()
            elif isinstance(item, EdgeItem):
                item.reset_visual_state()
    
    def _animation_step(self, goal_node: str):
        try:
            action, node_name, path = next(self.solver_generator)
            
            for item in self.scene.items():
                if isinstance(item, NodeItem):
                    if item.get_name() == node_name:
                        if action == 'visit' or action == 'exploring':
                            item.set_visual_state('visiting')
                        elif action == 'visited':
                            item.set_visual_state('visited')
                        elif action == 'goal_found':
                            self._highlight_path(path, goal_node)
                            self._show_result(path)
                            self.stop_animation()
                        break
                
                elif isinstance(item, EdgeItem):
                    if len(path) >= 2:
                        for i in range(len(path) - 1):
                            if item.get_source_name() == path[i] and item.get_target_name() == path[i+1]:
                                if action == 'goal_found':
                                    item.set_visual_state('path')
        
        except StopIteration:
            QMessageBox.information(self, "No Solution", "Goal node was not reached!")
            self.stop_animation()
    
    def _highlight_path(self, path: list, goal_node: str):
        for item in self.scene.items():
            if isinstance(item, NodeItem):
                if item.get_name() in path:
                    item.set_visual_state('path')
            
            elif isinstance(item, EdgeItem):
                for i in range(len(path) - 1):
                    if item.get_source_name() == path[i] and item.get_target_name() == path[i+1]:
                        item.set_visual_state('path')
    
    def _show_result(self, path: list):
        path_str = " -> ".join(path)
        QMessageBox.information(self, "Path Found!", f"Path: {path_str}")
    
    def stop_animation(self):
        self.solving = False
        if self.animation_timer:
            self.animation_timer.stop()
            self.animation_timer = None
        self.solver_generator = None
        self.status_label.setText("Ready.")
