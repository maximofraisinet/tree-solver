"""
Node graphics item for the tree solver canvas.
"""

from PyQt6.QtWidgets import (
    QGraphicsItem, QGraphicsEllipseItem, QGraphicsTextItem,
    QGraphicsSceneContextMenuEvent, QInputDialog, QDialog, QVBoxLayout, QLineEdit, QPushButton
)
from PyQt6.QtCore import Qt, QRectF, QPointF, pyqtSignal
from PyQt6.QtGui import QPen, QBrush, QColor, QFont, QPainter


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
        self.scene_ref = scene_ref
        
        self.default_color = QColor("#ffffff")
        self.border_color = QColor("#2c3e50")
        self.goal_border_color = QColor("#27ae60")
        self.visited_color = QColor("#bdc3c7")
        self.visiting_color = QColor("#f1c40f")
        self.path_color = QColor("#27ae60")
        
        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsMovable)
        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsSelectable)
        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemSendsGeometryChanges)
        self.setAcceptHoverEvents(True)
        
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
            border = QPen(self.goal_border_color, 3)
        else:
            border = QPen(self.border_color, 2)
        
        painter.setPen(border)
        
        if self.is_goal:
            brush = QBrush(QColor("#e8f8f5"))
        else:
            brush = QBrush(self.default_color)
        
        painter.setBrush(brush)
        painter.drawEllipse(self.boundingRect())
    
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
    
    def set_visual_state(self, state: str):
        """
        Set the visual state of the node for animation.
        States: 'default', 'visiting', 'visited', 'path'
        """
        if state == 'visiting':
            brush = QBrush(self.visiting_color)
            self.setBrush(brush)
        elif state == 'visited':
            brush = QBrush(self.visited_color)
            self.setBrush(brush)
        elif state == 'path':
            brush = QBrush(self.path_color)
            self.setBrush(brush)
            pen = QPen(self.path_color, 3)
            self.setPen(pen)
        else:
            brush = QBrush(self.default_color)
            self.setBrush(brush)
            pen = QPen(self.border_color, 2)
            self.setPen(pen)
        self.update()
    
    def reset_visual_state(self):
        """Reset node to default appearance."""
        self.setBrush(QBrush(self.default_color))
        if self.is_goal:
            pen = QPen(self.goal_border_color, 3)
        else:
            pen = QPen(self.border_color, 2)
        self.setPen(pen)
        self.update()
    
    def mouseDoubleClickEvent(self, event):
        """Open dialog to rename the node on double-click."""
        new_name, ok = QInputDialog.getText(
            None,
            "Rename Node",
            "Enter new name:",
            text=self.name
        )
        if ok and new_name.strip():
            self.set_name(new_name.strip())
        super().mouseDoubleClickEvent(event)
    
    def contextMenuEvent(self, event):
        """Show context menu on right-click."""
        from PyQt6.QtWidgets import QMenu
        context_menu = QMenu()
        
        goal_action = context_menu.addAction("Mark as Goal" if not self.is_goal else "Unmark Goal")
        delete_action = context_menu.addAction("Delete Node")
        
        action = context_menu.exec(event.screenPos())
        
        if action == goal_action:
            self.set_as_goal(not self.is_goal)
            for node in self.scene_ref.items():
                if isinstance(node, NodeItem) and node != self:
                    if node.is_goal_node():
                        node.set_as_goal(False)
        elif action == delete_action:
            self.scene_ref.removeItem(self)
        
        event.accept()
    
    def center(self) -> QPointF:
        return self.pos()
