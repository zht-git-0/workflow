from ..Packages import *
from .Node.Node import Node, NodePin
from .Node.ConnectionLine import ConnectionLine
from .CanvasScene import CanvasScene
from ..Menu.RightClickMenu import RightClickMenu  
# QGraphicsView: Qt图形框架中的视图类，用于显示QGraphicsScene的内容
# 视图提供了缩放、平移、旋转等变换功能，是用户与场景交互的窗口
# 一个场景可以被多个视图显示，每个视图可以有不同的变换和显示区域
class CanvasWidget(QGraphicsView):
    """画布视图类 - 显示场景内容的窗口"""
    def __init__(self, parent=None):
        super().__init__(parent)
        
        # 创建场景对象（CanvasScene是QGraphicsScene的子类）
        self.scene = CanvasScene()
        # setScene: 将场景关联到视图，视图将显示该场景的内容
        self.setScene(self.scene)
        
        # setRenderHint: 设置渲染提示，Antialiasing启用抗锯齿，使图形更平滑
        self.setRenderHint(QPainter.RenderHint.Antialiasing)
        # setDragMode: 设置拖拽模式，NoDrag表示不启用内置的拖拽功能
        self.setDragMode(QGraphicsView.DragMode.NoDrag)
        # setViewportUpdateMode: 设置视口更新模式，FullViewportUpdate在每次更新时重绘整个视口
        self.setViewportUpdateMode(QGraphicsView.ViewportUpdateMode.FullViewportUpdate)
        
        # setBackgroundBrush: 设置视图背景颜色（白色）
        # 注意：这会覆盖场景的背景设置
        self.setBackgroundBrush(QBrush(QColor(255, 255, 255)))
        
        # setMouseTracking: 启用鼠标跟踪，即使没有按下鼠标键也能接收鼠标移动事件
        self.setMouseTracking(True)
        
        # 保存原始拖拽模式，以便在需要时恢复
        self.original_drag_mode = self.dragMode()
        
        # 画布拖拽相关变量
        self.last_mouse_pos = None  # 上一次鼠标位置
        self.is_panning = False  # 是否正在拖拽画布
        
        # 右键选框相关变量
        self.selection_rect = None  # 选框矩形项
        self.selection_start_pos = None  # 选框起始位置
        self.is_selecting = False  # 是否正在选择
        
        # 右键菜单相关变量
        self.right_click_timer = None  # 右键计时器
        self.right_click_pos = None  # 右键点击位置
        self.is_long_press = False  # 是否为长按
        self.LONG_PRESS_THRESHOLD = 100  # 长按阈值（毫秒）
        
        # setCursor: 设置鼠标指针样式为箭头
        self.setCursor(Qt.CursorShape.ArrowCursor)
        
        # 隐藏滚动条
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        
        # 网格设置
        self.grid_size = 20  # 网格大小
        self.grid_color = QColor(220, 220, 220)  # 网格颜色
        
        # 设置接受拖拽
        self.setAcceptDrops(True)
    
    def update_cursor_style(self):
        """更新鼠标指针样式"""
        if self.is_panning:
            # 画布拖拽时显示闭合手型指针
            self.setCursor(Qt.CursorShape.ClosedHandCursor)
        elif hasattr(self.scene, 'dragging_pin') and self.scene.dragging_pin:
            # 节点连接时显示十字指针
            self.setCursor(Qt.CursorShape.CrossCursor)
        else:
            # 默认显示箭头指针
            self.setCursor(Qt.CursorShape.ArrowCursor)
    
    def drawBackground(self, painter, rect):
        """绘制网格背景"""
        super().drawBackground(painter, rect)
        
        # 设置网格画笔
        painter.setPen(QPen(self.grid_color, 1))
        
        # 计算网格起始位置
        left = int(rect.left()) - (int(rect.left()) % self.grid_size)
        top = int(rect.top()) - (int(rect.top()) % self.grid_size)
        
        # 绘制垂直线
        x = left
        while x <= rect.right():
            painter.drawLine(x, int(rect.top()), x, int(rect.bottom()))
            x += self.grid_size
        
        # 绘制水平线
        y = top
        while y <= rect.bottom():
            painter.drawLine(int(rect.left()), y, int(rect.right()), y)
            y += self.grid_size
    
    def keyPressEvent(self, event):
        """键盘按下事件 - 处理删除键删除选中节点"""
        if event.key() == Qt.Key.Key_Delete:
            # 获取场景中所有选中的项目
            selected_items = self.scene.selectedItems()
            
            # 收集要删除的连接线（包括选中的连接线和与选中节点相关的连接线）
            connections_to_remove = set()
            
            # 添加选中的连接线
            for item in selected_items:
                if isinstance(item, ConnectionLine):
                    connections_to_remove.add(item)
            
            # 添加与选中节点相关的连接线
            for item in selected_items:
                if isinstance(item, Node):
                    # 遍历节点的所有输入引脚
                    for pin in item.input_pins:
                        for connection in pin.connections:
                            connections_to_remove.add(connection)
                    # 遍历节点的所有输出引脚
                    for pin in item.output_pins:
                        for connection in pin.connections:
                            connections_to_remove.add(connection)
            
            # 删除所有相关连接线，先清理连接关系
            for connection in connections_to_remove:
                connection.cleanup_connections()
                self.scene.removeItem(connection)
            
            # 删除选中的节点
            for item in selected_items:
                if isinstance(item, Node):
                    self.scene.removeItem(item)
            
            event.accept()
            return
        
        super().keyPressEvent(event)
    
    def wheelEvent(self, event):
        """鼠标滚轮缩放 - QGraphicsView的滚轮事件处理"""
        zoom_factor = 1.15  # 缩放因子，每次缩放15%
        
        # 获取当前变换矩阵
        # transform(): 返回当前的变换矩阵，包含缩放、旋转、平移等信息
        transform = self.transform()
        # m11(): 获取变换矩阵的X轴缩放因子
        # 对于纯缩放变换，m11()和m22()返回相同的缩放值
        current_scale = transform.m11()
        
        # event.angleDelta().y(): 获取滚轮滚动的角度增量
        # 正值表示向上滚动（放大），负值表示向下滚动（缩小）
        if event.angleDelta().y() > 0:
            # 向上滚动，放大视图
            # 检查当前缩放是否小于最大限制（2倍）
            if current_scale < 2.0:  # 最大2倍
                # scale(): 在当前变换基础上应用缩放
                # 参数：x方向缩放因子，y方向缩放因子
                self.scale(zoom_factor, zoom_factor)
        else:
            # 向下滚动，缩小视图
            # 检查当前缩放是否大于最小限制（0.5倍）
            if current_scale > 0.5:  # 最小0.5倍
                # 缩小时使用倒数因子，实现缩小效果
                self.scale(1.0 / zoom_factor, 1.0 / zoom_factor)

    def mousePressEvent(self, event):
        """鼠标按下事件 - QGraphicsView的鼠标事件处理"""
        if event.button() == Qt.MouseButton.LeftButton:
            # mapToScene: 将视图坐标转换为场景坐标
            # event.pos(): 鼠标在视图坐标系中的位置
            # 返回值：鼠标在场景坐标系中的位置
            scene_pos = self.mapToScene(event.pos())
            # 在场景中查找该位置的图形项
            item = self.scene.itemAt(scene_pos, self.transform())
            
            # 如果点击的是空白区域，开始画布拖拽
            if item is None:
                self.is_panning = True
                self.last_mouse_pos = event.pos()
                self.setCursor(Qt.CursorShape.ClosedHandCursor)
                event.accept()
                return
            # 如果点击的是引脚或节点，临时禁用画布拖拽
            elif isinstance(item, (NodePin, Node)):
                self.setDragMode(QGraphicsView.DragMode.NoDrag)
        elif event.button() == Qt.MouseButton.RightButton:
            # 右键按下，判断是短按（弹出菜单）还是长按（选框选择）
            scene_pos = self.mapToScene(event.pos())
            item = self.scene.itemAt(scene_pos, self.transform())
            
            # 如果点击的是空白区域
            if item is None:
                self.right_click_pos = event.pos()
                self.is_long_press = False
                
                # 创建计时器，用于区分短按和长按
                self.right_click_timer = QTimer()
                self.right_click_timer.setSingleShot(True)
                self.right_click_timer.timeout.connect(self.start_selection_mode)
                self.right_click_timer.start(self.LONG_PRESS_THRESHOLD)
                
                # 接受鼠标右键按下事件，阻止事件继续传播
                event.accept()
                return

        
        super().mousePressEvent(event)
    
    def mouseMoveEvent(self, event):
        """鼠标移动事件 - QGraphicsView的鼠标移动处理"""
        if self.is_panning and self.last_mouse_pos:
            # 计算鼠标移动距离（视图坐标系）
            delta = event.pos() - self.last_mouse_pos
            
            # 获取水平和垂直滚动条
            # 通过移动滚动条来实现画布拖拽效果
            horizontal_scrollbar = self.horizontalScrollBar()
            vertical_scrollbar = self.verticalScrollBar()
            # 设置滚动条的新值，实现视图平移
            # 注意：减去delta是因为鼠标移动方向与滚动方向相反
            horizontal_scrollbar.setValue(horizontal_scrollbar.value() - delta.x())
            vertical_scrollbar.setValue(vertical_scrollbar.value() - delta.y())
            
            # 更新最后鼠标位置，为下一次移动计算做准备
            self.last_mouse_pos = event.pos()
        elif self.is_selecting and self.selection_rect and self.selection_start_pos:
            # 更新选框矩形
            current_pos = self.mapToScene(event.pos())
            rect = QRectF(self.selection_start_pos, current_pos).normalized()
            self.selection_rect.setRect(rect)
        
        super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        """鼠标释放事件"""
        if event.button() == Qt.MouseButton.LeftButton:
            # 如果正在进行画布拖拽，结束拖拽
            if self.is_panning:
                self.is_panning = False
                self.last_mouse_pos = None
                self.update_cursor_style()  # 恢复正常指针样式
                event.accept()
                return
            else:
                # 恢复原始拖拽模式
                self.setDragMode(self.original_drag_mode)
        elif event.button() == Qt.MouseButton.RightButton:
            # 右键释放
            if self.right_click_timer and self.right_click_timer.isActive():
                # 短按，弹出右键菜单
                self.right_click_timer.stop()
                self.show_context_menu(self.right_click_pos)
                self.right_click_timer = None
                self.right_click_pos = None
            elif self.is_selecting and self.selection_rect:
                # 长按，完成选框选择
                # 获取选框矩形
                selection_rect = self.selection_rect.rect()
                
                # 清除当前选择
                self.scene.clearSelection()
                
                # 选择选框内的所有节点
                for item in self.scene.items(selection_rect):
                    if isinstance(item, Node):
                        item.setSelected(True)
                    #elif isinstance(item, ConnectionLine):
                    #    item.setSelected(True)
                
                # 移除选框矩形
                self.scene.removeItem(self.selection_rect)
                self.selection_rect = None
                self.selection_start_pos = None
                self.is_selecting = False
                self.is_long_press = False
                
                event.accept()
                return
        
        super().mouseReleaseEvent(event)
    
    def start_selection_mode(self):
        """开始选框模式（长按触发）"""
        if self.right_click_pos:
            scene_pos = self.mapToScene(self.right_click_pos)
            self.is_selecting = True
            self.selection_start_pos = scene_pos
            self.is_long_press = True
            
            # 创建选框矩形
            self.selection_rect = QGraphicsRectItem()
            self.selection_rect.setRect(QRectF(scene_pos, scene_pos))
            self.selection_rect.setPen(QPen(QColor(0, 120, 215), 1, Qt.PenStyle.DashLine))
            self.selection_rect.setBrush(QBrush(QColor(0, 120, 215, 30)))
            self.scene.addItem(self.selection_rect)

    def show_context_menu(self, pos):
        """显示右键菜单（短按触发）"""
        
        def create_new_node(name):
            """创建新节点"""
            if self.right_click_pos:
                scene_pos = self.mapToScene(self.right_click_pos)
                # 在点击位置创建新节点
                self.scene.add_node(name, scene_pos.x(), scene_pos.y())
        # 创建右键菜单
        menu = RightClickMenu(self,create_new_node)
        #menu.add_node_action.triggered.connect(lambda:create_new_node("加法节点"))
        
        # 在指定位置显示菜单
        menu.exec(self.mapToGlobal(pos))   
    
    def dragEnterEvent(self, event):
        """拖拽进入事件处理"""
        if event.mimeData().hasText() or event.mimeData().hasFormat("application/x-qabstractitemmodeldatalist"):
            event.acceptProposedAction()
        else:
            event.ignore()
    
    def dragMoveEvent(self, event):
        """拖拽移动事件处理"""
        if event.mimeData().hasText() or event.mimeData().hasFormat("application/x-qabstractitemmodeldatalist"):
            event.acceptProposedAction()
        else:
            event.ignore()
    
    def dropEvent(self, event):
        """拖拽放下事件处理"""
        # 当有文本数据被拖拽到该区域时，此条件会被触发。
        # 常见的触发方式有：
        # 1. 从其他文本区域（如文本编辑器、浏览器等）拖拽文本过来
        # 2. 在代码中手动设置 QMimeData 的文本数据并触发拖拽操作
        if event.mimeData().hasText():
            # 获取拖拽的节点名称
            node_name = event.mimeData().text()
            # 获取放下位置的场景坐标
            scene_pos = self.mapToScene(event.position().toPoint())
            
            self.scene.add_node(node_name, scene_pos.x(), scene_pos.y())
            
            event.acceptProposedAction()
        else:
            event.ignore()
    
    def dragLeaveEvent(self, event):
        """拖拽离开事件处理"""
        event.accept()
    