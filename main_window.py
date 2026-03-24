"""
Main window for the Tree Solver application.
Handles UI, interactions, and animation orchestration.
"""

from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QToolBar,
    QGraphicsView, QGraphicsScene, QGraphicsItem, QMessageBox,
    QLabel, QPushButton, QButtonGroup, QGraphicsLineItem
)
from PyQt6.QtCore import Qt, QTimer, QPointF, pyqtSignal, QRectF
from PyQt6.QtGui import QAction, QPen, QColor, QPainter, QKeyEvent

from node_item import NodeItem
from edge_item import EdgeItem
from algorithms import bfs_generator, dfs_generator
from validator import validate_tree, build_graph_from_scene, ValidationError


class GraphicsView(QGraphicsView):
    """Custom graphics view for handling mouse events."""
    
    connection_requested = pyqtSignal(QPointF)
    
    def __init__(self, scene, parent=None):
        super().__init__(scene, parent)
        self.setRenderHint(QPainter.RenderHint.Antialiasing)
        self.setDragMode(QGraphicsView.DragMode.ScrollHandDrag)
        self.setTransformationAnchor(QGraphicsView.ViewportAnchor.AnchorUnderMouse)
        self.setResizeAnchor(QGraphicsView.ViewportAnchor.AnchorUnderMouse)


class MainWindow(QMainWindow):
    """Main application window."""
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Tree Solver - Graph Search Visualizer")
        self.setGeometry(100, 100, 1000, 700)
        
        self.node_counter = 0
        self.connect_mode = False
        self.connect_source = None
        self.temp_line = None
        self.solving = False
        self.solver_generator = None
        self.animation_timer = None
        self.current_path = []
        
        self._setup_ui()
    
    def _setup_ui(self):
        """Setup the user interface."""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        layout = QVBoxLayout(central_widget)
        
        toolbar = QToolBar()
        toolbar.setMovable(False)
        self.addToolBar(toolbar)
        
        self.add_node_btn = QPushButton("Add Node")
        self.add_node_btn.clicked.connect(self.add_node_at_center)
        toolbar.addWidget(self.add_node_btn)
        
        self.connect_btn = QPushButton("Connect")
        self.connect_btn.setCheckable(True)
        self.connect_btn.clicked.connect(self.toggle_connect_mode)
        toolbar.addWidget(self.connect_btn)
        
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
        
        self.view = GraphicsView(self.scene, self)
        
        layout.addWidget(self.view)
        
        self.status_label = QLabel("Shift+Click two nodes to connect them, or use Connect mode")
        layout.addWidget(self.status_label)
        
        self.scene.mousePressEvent = self.handle_mouse_press
        self.scene.mouseMoveEvent = self.handle_mouse_move
        self.scene.mouseReleaseEvent = self.handle_mouse_release
    
    def add_node_at_center(self):
        """Add a new node at the center of the canvas."""
        self.node_counter += 1
        node_name = f"Node{self.node_counter}"
        
        view_center = self.view.mapToScene(self.view.viewport().rect().center())
        node = NodeItem(node_name, view_center.x(), view_center.y(), self.scene)
        
        self.scene.addItem(node)
        self.status_label.setText(f"Added {node_name}. Double-click to rename, Right-click for options.")
    
    def toggle_connect_mode(self):
        """Toggle connection mode for creating edges."""
        self.connect_mode = self.connect_btn.isChecked()
        
        if self.connect_mode:
            self.status_label.setText("Connect Mode: Click source node, then target node")
            self.view.setDragMode(QGraphicsView.DragMode.NoDrag)
        else:
            self.status_label.setText("Shift+Click two nodes to connect them, or use Connect mode")
            self.view.setDragMode(QGraphicsView.DragMode.ScrollHandDrag)
            self.connect_source = None
            if self.temp_line:
                self.scene.removeItem(self.temp_line)
                self.temp_line = None
    
    def handle_mouse_press(self, event):
        """Handle mouse press events on the scene."""
        if self.solving:
            return
        
        pos = event.scenePos()
        item = self.scene.itemAt(pos, self.view.transform())
        
        if event.button() == Qt.MouseButton.LeftButton:
            if self.connect_mode and isinstance(item, NodeItem):
                if self.connect_source is None:
                    self.connect_source = item
                    self.status_label.setText(f"Selected: {item.get_name()}. Click another node to connect.")
                else:
                    if item != self.connect_source:
                        self.create_edge(self.connect_source, item)
                    self.connect_source = None
                    if self.temp_line and self.temp_line.scene() == self.scene:
                        self.scene.removeItem(self.temp_line)
                        self.temp_line = None
                    self.status_label.setText("Click first node for next connection.")
                event.accept()
                return
            
            if event.modifiers() & Qt.KeyboardModifier.ShiftModifier:
                if isinstance(item, NodeItem):
                    if self.connect_source is None:
                        self.connect_source = item
                        self.status_label.setText(f"Selected: {item.get_name()}. Click another node.")
                    else:
                        if item != self.connect_source:
                            self.create_edge(self.connect_source, item)
                        self.connect_source = None
                        if self.temp_line and self.temp_line.scene() == self.scene:
                            self.scene.removeItem(self.temp_line)
                            self.temp_line = None
                        self.status_label.setText("Shift+Click two nodes to connect.")
                    event.accept()
                    return
        
        QGraphicsScene.mousePressEvent(self.scene, event)
    
    def handle_mouse_move(self, event):
        """Handle mouse move events for drawing temp connection line."""
        if self.connect_source:
            pos = event.scenePos()
            
            if self.temp_line and self.temp_line.scene() == self.scene:
                self.scene.removeItem(self.temp_line)
            
            self.temp_line = QGraphicsLineItem(
                self.connect_source.pos().x(),
                self.connect_source.pos().y(),
                pos.x(),
                pos.y()
            )
            pen = QPen(QColor("#7f8c8d"), 2, Qt.PenStyle.DashLine)
            self.temp_line.setPen(pen)
            self.scene.addItem(self.temp_line)
        
        QGraphicsScene.mouseMoveEvent(self.scene, event)
    
    def handle_mouse_release(self, event):
        """Handle mouse release events."""
        QGraphicsScene.mouseReleaseEvent(self.scene, event)
    
    def create_edge(self, node_a: NodeItem, node_b: NodeItem):
        """Create an edge between two nodes. Direction is auto-determined."""
        name_a = node_a.get_name()
        name_b = node_b.get_name()
        
        for item in self.scene.items():
            if isinstance(item, EdgeItem):
                names = {item.get_source_name(), item.get_target_name()}
                if names == {name_a, name_b}:
                    QMessageBox.warning(self, "Warning", "Connection already exists between these nodes!")
                    return
        
        edge = EdgeItem(node_a, node_b)
        self.scene.addItem(edge)
        self.status_label.setText(f"Connected: {name_a} <-> {name_b}")
    
    def clear_canvas(self):
        """Clear all nodes and edges from the canvas."""
        self.stop_animation()
        self.scene.clear()
        self.node_counter = 0
        self.status_label.setText("Canvas cleared. Add nodes to begin.")
    
    def solve_tree(self, algorithm: str):
        """Solve the tree using BFS or DFS."""
        if self.solving:
            return
        
        nodes = [item for item in self.scene.items() if isinstance(item, NodeItem)]
        edges = [item for item in self.scene.items() if isinstance(item, EdgeItem)]
        
        if not nodes:
            QMessageBox.warning(self, "Error", "Add some nodes first!")
            return
        
        try:
            graph, goal_node = build_graph_from_scene(nodes, edges)
            start_node, _ = validate_tree(graph, goal_node)
        except ValidationError as e:
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
        """Reset all nodes and edges to default visual state."""
        for item in self.scene.items():
            if isinstance(item, NodeItem):
                item.reset_visual_state()
            elif isinstance(item, EdgeItem):
                item.reset_visual_state()
    
    def _animation_step(self, goal_node: str):
        """Process the next step in the animation."""
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
        """Highlight the final path in green."""
        for item in self.scene.items():
            if isinstance(item, NodeItem):
                if item.get_name() in path:
                    item.set_visual_state('path')
            
            elif isinstance(item, EdgeItem):
                for i in range(len(path) - 1):
                    if item.get_source_name() == path[i] and item.get_target_name() == path[i+1]:
                        item.set_visual_state('path')
    
    def _show_result(self, path: list):
        """Show a popup with the found path."""
        path_str = " -> ".join(path)
        QMessageBox.information(self, "Path Found!", f"Path: {path_str}")
    
    def stop_animation(self):
        """Stop the animation timer."""
        self.solving = False
        if self.animation_timer:
            self.animation_timer.stop()
            self.animation_timer = None
        self.solver_generator = None
        self.status_label.setText("Ready. Add nodes or solve the tree.")
