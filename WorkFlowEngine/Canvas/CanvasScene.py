from ..Packages import *
from .Node.Node import Node, NodePin
from .Node.ConnectionLine import ConnectionLine
# QGraphicsScene: Qt图形框架中的场景类，用于管理所有的图形项（QGraphicsItem）
# 场景是一个二维空间，可以包含各种图形项，如线条、矩形、文本等
# QGraphicsView用于显示场景的内容，提供缩放、平移等视图功能
class CanvasScene(QGraphicsScene):
    """画布场景类 - 管理所有图形项的容器"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.connections = []  # 存储所有连接线的列表
        self.temp_connection = None  # 临时连接线（拖拽时显示）
        self.dragging_pin = None  # 当前正在拖拽的引脚
        
        # setBackgroundBrush: 设置场景背景颜色
        # QBrush是画刷，用于填充区域，这里用RGB(240,240,240)的浅灰色
        self.setBackgroundBrush(QBrush(QColor(240, 240, 240)))
        
        # setSceneRect: 设置场景的边界矩形
        # 参数：x, y, width, height
        # 这里设置了一个很大的场景（100000x100000），以支持大型画布
        self.setSceneRect(-50000, -50000, 100000, 100000)
    
    def add_node(self, text, x=0, y=0):
        """添加节点到场景"""
        # 创建节点对象（Node是自定义的QGraphicsItem子类）
        node = Node(text, x, y)
        # addItem: 将图形项添加到场景中，使其可见和可交互
        self.addItem(node)
        return node
    
    def mousePressEvent(self, event):
        """鼠标按下事件 - QGraphicsScene的鼠标事件处理"""
        if event.button() == Qt.MouseButton.LeftButton:
            # itemAt: 获取指定位置的图形项
            # event.scenePos(): 鼠标在场景坐标系中的位置
            # self.views()[0].transform(): 视图的变换矩阵（用于坐标转换）
            item = self.itemAt(event.scenePos(), self.views()[0].transform())
            if isinstance(item, NodePin):
                if item.pin_type == 'output':
                    # 开始拖拽输出引脚 - 允许已连接的输出引脚创建新连接
                    if item.connected and item.data_type=="logic":
                        return
                    self.dragging_pin = item
                    self.dragging_pin.setBrush(QBrush(self.dragging_pin.color))
                    self.temp_connection = ConnectionLine(item, None,self.dragging_pin.color)
                    self.temp_connection.setLine(
                        self.dragging_pin.scenePos().x()+self.dragging_pin.rect().width()/2,
                        self.dragging_pin.scenePos().y(),
                        event.scenePos().x(),
                        event.scenePos().y()
                    )
                    self.addItem(self.temp_connection)
                    # 更新鼠标指针样式
                    if self.views():
                        self.views()[0].update_cursor_style()
                    return
                elif item.pin_type == 'input' and not item.connected:
                    pass
                    # 点击输入引脚，尝试连接 - 输入引脚仍然只能有一个连接
                    # 注意：selected_output_pin 逻辑需要完善，暂时注释掉
                    # if hasattr(self, 'selected_output_pin') and self.selected_output_pin:
                    #     self.create_connection(self.selected_output_pin, item)
                    #     self.selected_output_pin = None
                    return
            
            # 检查是否点击了连接线
            if isinstance(item, ConnectionLine):
                if event.modifiers() & Qt.KeyboardModifier.AltModifier:
                    # Alt+点击删除连接
                    self.remove_connection(item)
                    return
            
            # 如果点击的是空白区域，允许画布拖拽
            if item is None:
                #取消选择连接线
                self.clearSelection()
                event.accept()
                return
        
        super().mousePressEvent(event)
    
    def mouseMoveEvent(self, event):
        """鼠标移动事件"""
        if self.dragging_pin and self.temp_connection:
            # 更新临时连接线的终点
            self.temp_connection.setLine(
                self.dragging_pin.scenePos().x()+self.dragging_pin.rect().width()/2,
                self.dragging_pin.scenePos().y(),
                event.scenePos().x(),
                event.scenePos().y()
            )
        
        super().mouseMoveEvent(event)
    
    def mouseReleaseEvent(self, event):
        """鼠标释放事件"""
        if self.dragging_pin and self.temp_connection:
            # 检查是否释放在输入引脚上
            self.dragging_pin.update_appearance()
            item = self.itemAt(event.scenePos(), self.views()[0].transform())
            if isinstance(item, NodePin) and item.pin_type == 'input' and not item.connected:
                if item != self.dragging_pin:
                    self.create_connection(self.dragging_pin, item)
            
            # 清理临时连接
            self.removeItem(self.temp_connection)
            self.temp_connection = None
            self.dragging_pin = None
            # 更新鼠标指针样式
            if self.views():
                self.views()[0].update_cursor_style()
        
        super().mouseReleaseEvent(event)
    
    def create_connection(self, start_pin, end_pin):
        """创建连接"""
        if (start_pin.pin_type == 'output' and end_pin.pin_type == 'input' and
            start_pin.data_type == end_pin.data_type and
            start_pin.parentItem() != end_pin.parentItem()):
            
            # 创建连接线
            connection = ConnectionLine(start_pin, end_pin, start_pin.color)
            self.addItem(connection)
            self.connections.append(connection)
            
            # 添加到引脚的连接列表
            start_pin.connections.append(connection)
            end_pin.connections.append(connection)
            
            # 更新引脚状态 - 基于连接列表
            start_pin.connected = len(start_pin.connections) > 0
            end_pin.connected = len(end_pin.connections) > 0
            start_pin.update_appearance()
            end_pin.update_appearance()
    
    def remove_connection(self, connection):
        """移除连接"""
        if connection in self.connections:
            self.connections.remove(connection)
            
            # 从引脚的连接列表中移除
            if connection in connection.start_pin.connections:
                connection.start_pin.connections.remove(connection)
            if connection in connection.end_pin.connections:
                connection.end_pin.connections.remove(connection)
            
            # 更新引脚状态
            connection.start_pin.connected = False
            # 只有当输入引脚没有其他连接时才设置为False
            if not connection.end_pin.connections:
                connection.end_pin.connected = False
            connection.start_pin.update_appearance()
            connection.end_pin.update_appearance()
            
            # 从场景中移除
            self.removeItem(connection)
    
    def update_connections(self):
        """更新所有连接线位置"""
        for connection in self.connections:
            connection.update_position()
    def get_all_node(self):
        """根据名称获取所有节点"""
        nodes = []
        for item in self.items():
            if isinstance(item, Node):
                nodes.append(item)
        return nodes
