from PyQt6.QtWidgets import QLabel
from ...Packages import *
from .CustomNodes.pin_colors import pin_colors

class BaseItem(QGraphicsEllipseItem):
    def __init__(self, pin_type, data_type, parent=None):
        super().__init__(parent)
        self.parent=parent
        self.pin_type = pin_type  # 'input' or 'output'
        self.data_type = data_type  # 'int', 'str', 'bool', 'float'
        self.connected = False
        self.connections = []
        self.length=0
        # 设置引脚样式
        # 设置引脚的矩形区域，前两个参数 (-6, -6) 表示矩形左上角的坐标，
        # 后两个参数 (12, 12) 分别表示矩形的宽度和高度，以此创建一个边长为 12 的正方形引脚。
        self.setAcceptHoverEvents(True)
        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsMovable, False)
        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsSelectable, False)
class NodePin(BaseItem):
    """引脚类"""
    def __init__(self, pin_type, data_type, parent,i):
        super().__init__(pin_type, data_type, parent)
        # 设置引脚颜色
        self.color=pin_colors[self.data_type]
        self.pin_shape()
        self.line_edit = None  # 初始化line_edit为None
        self.combo_box = None  # 初始化combo_box为None
        NodeInfo=self.parent.NodeInfo
        self.pin_info=getattr(NodeInfo,pin_type)[i]
        if self.pin_info[0]=="none":
            # 创建NodeText和PinComboBox
            node_text = NodeText(self.pin_type, self.data_type, self, self.pin_info)
            self.combo_box = node_text.combo_box
            # 连接PinComboBox的选择改变信号到更新引脚颜色的函数
            if self.combo_box:
                self.combo_box.selection_changed.connect(self._update_pin_color)
                # 在combo_box创建完成后立即更新引脚颜色
                self._update_pin_color(self.combo_box.currentText())
        else:
            # 创建NodeText和PinLineEdit
            node_text = NodeText(self.pin_type, self.data_type, self, self.pin_info)
            self.line_edit = node_text.line_edit
        
        self.update_appearance()
    def update_appearance(self):
        """更新引脚外观"""
        
        # 更新所有子控件的状态
        if self.line_edit:
            self.line_edit.hide() if self.connected else self.line_edit.show()
        #禁用下拉列表
        if self.combo_box:
            #self.combo_box.hide() if has_connection else self.combo_box.show()
            self.combo_box.setEnabled(not self.connected)
        
        # 更新引脚外观
        brush = QBrush(self.color) if self.connected else QBrush(Qt.GlobalColor.transparent)
        self.setBrush(brush)
        self.setPen(QPen(self.color, 2))
    
    def hoverEnterEvent(self, event):
        """鼠标悬停事件"""
        self.setToolTip(f"{self.pin_type}: {self.data_type}")
        super().hoverEnterEvent(event)

    def pin_shape(self):
        if self.pin_type == 'input':
            self.setRect(-12,-6, 12, 12)
        else:
            self.setRect(0,-6, 12, 12)
            
    def _update_pin_color(self, data_type):
        """根据数据类型更新引脚颜色"""
        self.data_type = data_type
        # 更新引脚信息
        self.pin_info[0]=data_type
        #print(self.pin_info)
        self.color = pin_colors[data_type]
        self.update_appearance()
class NodeText(BaseItem):
    def __init__(self, pin_type, data_type, parent,pin_info):
        super().__init__(pin_type, data_type, parent)
        self.text=data_type
        self.line_edit=None
        self.combo_box=None
        self.pin_text()
        if pin_info[1]:
            if pin_info[0]=="none":
                self.create_pin_widget('combo_box')
            elif pin_info[0]=="img":
                self.create_pin_widget("img")
            else:
                self.create_pin_widget('line_edit')
    def pin_text(self):
        """将文本放入引脚"""
        if self.text=="logic" or self.text=="none":
            self.text=""
        self.text_item = QGraphicsTextItem(self.text, self)
        self.text_item.setDefaultTextColor(QColor(0, 0, 0))
        self.text_item.setFont(QFont("Arial", 15))
        # 获取节点文本项的边界矩形，该矩形定义了文本项在局部坐标系中的范围
        self.text_rect = self.text_item.boundingRect()
        if self.pin_type == 'input':
            self.text_item.setPos(
                0,
                (-self.text_rect.height()) /2,
            )
        else:
            self.text_item.setPos(
                (-self.text_rect.width()),
                (-self.text_rect.height()) /2,
            )
        self.parent.length+=self.text_rect.width()
    
    def create_pin_widget(self, widget_type):
        """创建引脚控件（动态合并pin_line_edit和pin_combo_box功能）
        
        Args:
            widget_type: 控件类型 ('line_edit' 或 'combo_box')
        """
        # 使用工厂类创建控件
        proxy_widget, widget = PinWidgetFactory.create_widget(widget_type, self.pin_type, self.text_rect)
        
        # 使用动态变量设置引用
        setattr(self, widget_type, widget)
        
        # 将代理组件添加到当前项
        proxy_widget.setParentItem(self)
        self.parent.length += widget.width()
class PinWidgetFactory:
    """引脚控件工厂类，负责创建和配置各种引脚控件实例"""
    @staticmethod
    def create_widget(widget_type, pin_type, text_rect):
        """创建并配置引脚控件实例
        
        Args:
            widget_type: 控件类型 ('line_edit' 或 'combo_box')
            pin_type: 引脚类型 ('input' 或 'output')
             text_rect: 文本区域的边界矩形
            
        Returns:
            tuple: (QGraphicsProxyWidget, QWidget) - 代理组件和控件实例 """
        # 根据控件类型创建相应的控件
        if widget_type == 'line_edit':
            widget = PinLineEdit()
        elif widget_type == 'combo_box':
            widget = PinTypeComboBox()
        elif widget_type =="img":
            widget = PinPicLabel()
        else:
            raise ValueError(f"不支持的控件类型: {widget_type}")
        
        # 创建QGraphicsProxyWidget来包装控件，使其可以在QGraphicsScene中使用
        proxy_widget = QGraphicsProxyWidget()
        proxy_widget.setWidget(widget)
        
        # 设置控件的位置
        if pin_type == 'input':
            # 输入引脚的控件放在引脚左侧
            proxy_widget.setPos(text_rect.width(), -widget.height()/2)
        else:
            # 输出引脚的控件放在引脚右侧
            proxy_widget.setPos(-text_rect.width() - widget.width(), -widget.height()/2)
        return proxy_widget, widget



class PinLineEdit(QLineEdit):
    def __init__(self,parent=None):
        super().__init__(parent)
        self.setPlaceholderText("输入")
        self.setFixedSize(60, 25)
        self.setStyleSheet("background-color: rgb(255, 255, 255); border: 2px solid rgb(200, 200, 200); color: rgb(0, 0, 0);")

class PinTypeComboBox(QComboBox):
    # 定义信号，当选择改变时发出
    selection_changed = pyqtSignal(str)
    
    def __init__(self,parent=None):
        super().__init__(parent)
        self.setStyleSheet("background-color: rgb(255, 255, 255); border: 2px solid rgb(200, 200, 200); color: rgb(0, 0, 0);")
        self.addItems(["int","str","bool","float"])
        # 连接当前索引改变的信号到内部处理函数
        self.currentIndexChanged.connect(self._on_selection_changed)
    
    def _on_selection_changed(self, index):
        """当选择改变时处理函数"""
        if index >= 0:
            selected_type = self.itemText(index)
            self.selection_changed.emit(selected_type)
class PinPicLabel(QLabel):
    def __init__(self,parent=None):
        super().__init__(parent)
    def set_pic(self,img):
        #设置为截图图片
        self.setPixmap(img)
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)

