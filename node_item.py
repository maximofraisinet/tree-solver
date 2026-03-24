"""
Node graphics item for the tree solver canvas.
"""

from PyQt6.QtWidgets import QGraphicsItem, QInputDialog, QGraphicsTextItem
from PyQt6.QtCore import Qt, QRectF, QPointF
from PyQt6.QtGui import QPen, QBrush, QColor, QFont, QPainter, QPainterPath


NODE_RADIUS = 30


class NodeItem(QGraphicsItem):
    """
    A graphical node represented as a circle with text inside.
    Supports drag-and-drop, renaming, and goal marking.
    """
    
    def __init__(self, name: str, x: float, y: float, scene_ref):
        super().__init__()
        self.name = name
        self.node_radius = NODE_RADIUS
        self.is_goal = False
        self.is_start = False
        self.scene_ref = scene_ref
        self.connected_edges = []
        self.current_brush = QBrush(QColor("#ffffff"))
        
        self.default_color = QColor("#ffffff")
        self.border_color = QColor("#2c3e50")
        self.goal_border_color = QColor("#27ae60")
        self.start_border_color = QColor("#3498db")
        self.visiting_color = QColor("#f1c40f")
        self.visited_color = QColor("#bdc3c7")
        self.path_color = QColor("#27ae60")
        
        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsMovable)
        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsSelectable)
        self.setPos(x, y)
        
        self.text_item = QGraphicsTextItem(self)
        self.text_item.setPlainText(name)
        self.text_item.setDefaultTextColor(QColor("#2c3e50"))
        font = QFont("Arial", 12, QFont.Weight.Bold)
        self.text_item.setFont(font)
        self.text_item.setPos(-self.text_item.boundingRect().width() / 2, -self.text_item.boundingRect().height() / 2)
    
    def boundingRect(self) -> QRectF:
        return QRectF(
            -self.node_radius,
            -self.node_radius,
            self.node_radius * 2,
            self.node_radius * 2
        )
    
    def paint(self, painter: QPainter, option, widget=None):
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        if self.isSelected():
            border = QPen(QColor("#3498db"), 3)
        elif self.is_goal:
            border = QPen(self.goal_border_color, 4)
        elif self.is_start:
            border = QPen(self.start_border_color, 4)
        else:
            border = QPen(self.border_color, 2)
        
        painter.setPen(border)
        
        if self.is_goal:
            brush = QBrush(QColor("#e8f8f5"))
        elif self.is_start:
            brush = QBrush(QColor("#ebf5fb"))
        else:
            brush = self.current_brush
        
        painter.setBrush(brush)
        painter.drawEllipse(self.boundingRect())
    
    def itemChange(self, change, value):
        """Handle item changes - update connected edges when moving."""
        if change == QGraphicsItem.GraphicsItemChange.ItemPositionHasChanged:
            for edge in self.connected_edges:
                edge.update_position()
        return super().itemChange(change, value)
    
    def get_name(self) -> str:
        return self.name
    
    def set_name(self, new_name: str):
        self.name = new_name
        self.text_item.setPlainText(new_name)
        self.text_item.setPos(-self.text_item.boundingRect().width() / 2, -self.text_item.boundingRect().height() / 2)
    
    def set_as_goal(self, goal: bool):
        self.is_goal = goal
        self.update()
    
    def is_goal_node(self) -> bool:
        return self.is_goal
    
    def set_is_start(self, start: bool):
        self.is_start = start
        self.update()
    
    def is_start_node(self) -> bool:
        return self.is_start
    
    def set_visual_state(self, state: str):
        if state == 'visiting':
            self.current_brush = QBrush(self.visiting_color)
        elif state == 'visited':
            self.current_brush = QBrush(self.visited_color)
        elif state == 'path':
            self.current_brush = QBrush(self.path_color)
        else:
            self.current_brush = QBrush(self.default_color)
        self.update()
    
    def reset_visual_state(self):
        self.current_brush = QBrush(self.default_color)
        self.update()
    
    def mouseDoubleClickEvent(self, event):
        new_name, ok = QInputDialog.getText(
            None,
            "Rename Node",
            "Enter new name:",
            text=self.name
        )
        if ok and new_name.strip():
            self.set_name(new_name.strip())
        super().mouseDoubleClickEvent(event)
