from ...Packages import *

# QGraphicsLineItem: Qt图形框架中的线条类，用于绘制直线
# 继承自QGraphicsItem，可以在QGraphicsScene中显示和管理
class ConnectionLine(QGraphicsLineItem):
    """连接线类"""
    def __init__(self, start_pin, end_pin, color,parent=None):
        super().__init__(parent)
        self.start_pin = start_pin
        self.end_pin = end_pin
        self.color=color
        # 设置连接线样式
        # 使用 QPen 设置连接线的颜色和宽度，此处颜色为 RGB(52, 73, 94)，宽度为 8 像素
        self.setPen(QPen(QColor(color), 8))
        # 设置该图形项为可选择状态，允许用户选中此连接线
        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsSelectable, True)
        # 设置该图形项的 Z 轴值为 -1
        self.setZValue(-1)
        
        # 更新连接线位置
        self.update_position()
    
    def update_position(self):
        """更新连接线位置"""
        if self.start_pin and self.end_pin:
            try:
                start_pos = self.start_pin.scenePos()
                end_pos = self.end_pin.scenePos()
                self.setLine(
                    start_pos.x()+self.start_pin.rect().width()/2, 
                    start_pos.y(), 
                    end_pos.x()-self.end_pin.rect().width()/2, 
                    end_pos.y()
                )
            except RuntimeError:
                # 如果引脚已被删除，移除连接线
                if self.scene():
                    self.scene().removeItem(self)
    
    def cleanup_connections(self):
        """清理连接关系，恢复引脚到未连接状态"""
        if self.start_pin and self in self.start_pin.connections:
            self.start_pin.connections.remove(self)
            self.start_pin.connected = len(self.start_pin.connections) > 0
            self.start_pin.update_appearance()
        
        if self.end_pin and self in self.end_pin.connections:
            self.end_pin.connections.remove(self)
            self.end_pin.connected = len(self.end_pin.connections) > 0
            self.end_pin.update_appearance()
    
    def paint(self, painter, option, widget):
        """绘制连接线"""
        # 清除选中状态标志，防止显示默认虚线框
        option.state &= ~QStyle.StateFlag.State_Selected

        if self.isSelected():
            # 选中时使用高亮样式
            # 在外边包裹self.color取反的颜色的框
            color = QColor(self.color)
            color.setRed(255 - color.red())
            color.setGreen(255 - color.green())
            color.setBlue(255 - color.blue())
            
            # 绘制反色边框
            border_pen = QPen(color, 12)
            border_pen.setJoinStyle(Qt.PenJoinStyle.MiterJoin)
            painter.setPen(border_pen)
            painter.drawLine(self.line())
            
            # 绘制内部连接线
            pen = QPen(QColor(self.color), 8)
            painter.setPen(pen)
            painter.drawLine(self.line())
        else:
            # 普通样式
            pen = QPen(QColor(self.color), 8)
            self.setPen(pen)
            super().paint(painter, option, widget)