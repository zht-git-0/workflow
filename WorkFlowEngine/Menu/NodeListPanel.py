from ..Packages import *
from . import setStyleSheet
from ..Canvas.Node.CustomNodes import node_dict
class NodeListPanel(QWidget):
    """可折叠的侧边菜单组件 - 节点列表面板"""
    # 定义信号
    collapsed = pyqtSignal(bool)  # 折叠状态改变信号
    
    def __init__(self, canvas_widget, parent=None):
        super().__init__(parent)
        self.canvas_widget = canvas_widget
        self.is_collapsed = False
        self.setMinimumWidth(200)
        self.setMaximumWidth(250)
        
        # 设置样式
        self.setStyleSheet(setStyleSheet)
        
        self.init_ui()
    def init_ui(self):
        """初始化用户界面"""
        # 主布局
        layout = QVBoxLayout(self)
        layout.setContentsMargins(5, 5, 5, 5)
        layout.setSpacing(5)
        
        # 折叠按钮
        self.collapse_button = QPushButton("◀ 节点列表")
        self.collapse_button.clicked.connect(self.toggle_collapse)
        layout.addWidget(self.collapse_button)
        
        # 内容区域
        self.content_widget = QWidget()
        content_layout = QVBoxLayout(self.content_widget)
        content_layout.setContentsMargins(0, 0, 0, 0)
        content_layout.setSpacing(5)
        
        # 节点列表
        self.node_list = NodeListWidget()
        content_layout.addWidget(self.node_list)
        
        # 添加内容到主布局
        layout.addWidget(self.content_widget)
        
        # 设置布局拉伸因子
        layout.setStretch(1, 1)  # 让内容区域占据剩余空间
    
    def toggle_collapse(self):
        """切换折叠状态"""
        self.is_collapsed = not self.is_collapsed
        
        if self.is_collapsed:
            # 折叠状态 - 发射信号让主窗口处理
            self.collapsed.emit(True)
        else:
            # 展开状态
            self.content_widget.show()
            self.collapse_button.setText("◀ 节点列表")
            self.setMaximumWidth(250)  # 恢复原始宽度
            self.collapsed.emit(False)
    
    def expand_panel(self):
        """展开面板"""
        if self.is_collapsed:
            self.is_collapsed = False
            self.content_widget.show()
            self.collapse_button.setText("◀ 节点列表")
            self.setMaximumWidth(250)  # 恢复原始宽度
            self.collapsed.emit(False)
    
    
    def add_node_type(self, node_name):
        """添加节点类型到列表"""
        self.node_list.addItem(node_name)


class NodeListWidget(QListWidget):
    """自定义的节点列表控件，重写拖拽事件以正确设置MIME数据"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.search_dic={}
        """ self.addItem("加法节点")
        self.addItem("减法节点")
        self.addItem("乘法节点")
        self.addItem("除法节点") """
        for node_name in node_dict.keys():
            self.addItem(node_dict[node_name].Info().zh_name)
            self.search_dic[node_dict[node_name].Info().zh_name]=node_name
        self.setAcceptDrops(True)
        self.setDragEnabled(True)
        self.setDragDropMode(QListWidget.DragDropMode.DragOnly)
        self.setDefaultDropAction(Qt.DropAction.CopyAction)
    def mimeData(self, items):
        """重写mimeData方法，设置正确的MIME数据"""
        if not items:
            return None
        # 获取第一个选中项的文本
        item = items[0]
        node_name = item.text()
        
        # 创建MIME数据
        mime_data = QMimeData()
        
        # 设置文本数据（作为备用）
        mime_data.setText(self.search_dic[node_name])
        
        """ # 创建标准的QAbstractItemModel拖拽数据格式
        # 格式：行(4字节) + 列(4字节) + 角色(4字节) + 值长度(4字节) + 值
        import struct
        
        # 构建数据块
        data = bytearray()
        
        # 行、列都为0
        data.extend(struct.pack('<i', 0))  # 行
        data.extend(struct.pack('<i', 0))  # 列
        data.extend(struct.pack('<i', 0))  # Qt::DisplayRole
        
        # 添加节点名称作为值
        node_name_bytes = node_name.encode('utf-8')
        data.extend(struct.pack('<i', len(node_name_bytes)))  # 值长度
        data.extend(node_name_bytes)  # 值
        
        # 设置MIME数据
        mime_data.setData('application/x-qabstractitemmodeldatalist', data)
        
        #print(f"设置MIME数据: 节点名称='{node_name}', 数据长度={len(data)}")
        #print(f"MIME数据(hex): {data.hex()}") """
        
        return mime_data