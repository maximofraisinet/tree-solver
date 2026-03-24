"""
Edge graphics item for the tree solver canvas.
Represents a directed edge from one node to another.
"""

from PyQt6.QtWidgets import QGraphicsItem
from PyQt6.QtCore import Qt, QPointF, QRectF
from PyQt6.QtGui import QPen, QColor, QPainter, QPolygonF
from math import atan2, cos, sin, pi


ARROW_SIZE = 10


class EdgeItem(QGraphicsItem):
    """
    A directed edge connecting two nodes.
    Drawn as a line with an arrow head.
    """
    
    def __init__(self, source_node, target_node):
        super().__init__()
        self.source_node = source_node
        self.target_node = target_node
        
        source_node.connected_edges.append(self)
        target_node.connected_edges.append(self)
        
        self.default_color = QColor("#8b2e2e")
        self.path_color = QColor("#2ecc71")
        self.current_pen = QPen(self.default_color, 2)
        
        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsSelectable)
        self.setZValue(-1)
    
    def update_position(self):
        self.update()
    
    def boundingRect(self):
        source_pos = self.source_node.pos()
        target_pos = self.target_node.pos()
        
        min_x = min(source_pos.x(), target_pos.x()) - ARROW_SIZE - 30
        min_y = min(source_pos.y(), target_pos.y()) - ARROW_SIZE - 30
        max_x = max(source_pos.x(), target_pos.x()) + ARROW_SIZE + 30
        max_y = max(source_pos.y(), target_pos.y()) + ARROW_SIZE + 30
        
        return QRectF(min_x, min_y, max_x - min_x, max_y - min_y)
    
    def paint(self, painter: QPainter, option, widget=None):
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        source_center = self.source_node.pos()
        target_center = self.target_node.pos()
        
        dx = target_center.x() - source_center.x()
        dy = target_center.y() - source_center.y()
        angle = atan2(dy, dx)
        
        node_radius = 30
        
        start_x = source_center.x() + node_radius * cos(angle)
        start_y = source_center.y() + node_radius * sin(angle)
        end_x = target_center.x() - node_radius * cos(angle)
        end_y = target_center.y() - node_radius * sin(angle)
        
        if self.isSelected():
            pen = QPen(QColor("#c0392b"), 2)
        else:
            pen = self.current_pen
        
        painter.setPen(pen)
        painter.drawLine(QPointF(start_x, start_y), QPointF(end_x, end_y))
        
        arrow_point = QPointF(end_x, end_y)
        arrow_angle1 = angle + pi - pi / 6
        arrow_angle2 = angle + pi + pi / 6
        
        arrow_p1 = QPointF(
            end_x - ARROW_SIZE * cos(arrow_angle1),
            end_y - ARROW_SIZE * sin(arrow_angle1)
        )
        arrow_p2 = QPointF(
            end_x - ARROW_SIZE * cos(arrow_angle2),
            end_y - ARROW_SIZE * sin(arrow_angle2)
        )
        
        arrow_polygon = QPolygonF([arrow_point, arrow_p1, arrow_p2])
        painter.drawPolygon(arrow_polygon)
    
    def get_source_name(self) -> str:
        return self.source_node.get_name()
    
    def get_target_name(self) -> str:
        return self.target_node.get_name()
    
    def get_nodes(self):
        return (self.source_node, self.target_node)
    
    def set_visual_state(self, state: str):
        if state == 'path':
            self.current_pen = QPen(self.path_color, 3)
        else:
            self.current_pen = QPen(self.default_color, 2)
        self.update()
    
    def reset_visual_state(self):
        self.current_pen = QPen(self.default_color, 2)
        self.update()
    
    def remove_from_nodes(self):
        if self in self.source_node.connected_edges:
            self.source_node.connected_edges.remove(self)
        if self in self.target_node.connected_edges:
            self.target_node.connected_edges.remove(self)
