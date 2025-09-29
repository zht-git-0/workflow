from ...Packages import *
from .Pin import *
from .CustomNodes import node_dict
class NodeBase(QGraphicsRectItem):
    def __init__(self, name, x=0, y=0, parent=None,input_nums=1,output_nums=1):
        super().__init__(parent)
        self.name = name  
        self.input_pins = []
        self.output_pins = []
        self.input_nums=input_nums
        self.output_nums=output_nums
        self.last=0
        # 设置节点样式
        self.setPos(x, y)
        self.setBrush(QBrush(QColor(255, 255, 255)))
        self.setPen(QPen(QColor(200, 200, 200), 3))
        self.setRect(0, 0, 10, max(input_nums,output_nums)*40)
        # 设置节点可移动和可选择
        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsMovable, True)
        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsSelectable, True)
        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemSendsGeometryChanges, True)
        # 创建节点文本
        self.title = QGraphicsTextItem(name, self)
        self.title.setDefaultTextColor(QColor(0, 0, 0))
        self.title.setFont(QFont("Arial", 15))
        # 获取节点文本项的边界矩形，该矩形定义了文本项在局部坐标系中的范围
        text_rect = self.title.boundingRect()
        self.title.setPos(
            (self.rect().width() - text_rect.width()) /2,
            (-text_rect.height())/3*2
        )
    def rename(self,name):
        self.name=name
        self.title.setPlainText(name)
    def re_position_title(self):
        text_rect = self.title.boundingRect()
        self.title.setPos(
            (self.rect().width() - text_rect.width()) /2,
            (-text_rect.height())/3*2
        )
class Node(NodeBase):
    """节点类"""
    def __init__(self, name, x=0, y=0, parent=None,input_nums=2,output_nums=1):
        self.NodeInfo=node_dict[name].Info()
        input_nums=len(self.NodeInfo.input)
        output_nums=len(self.NodeInfo.output)
        super().__init__(name, x, y, parent,input_nums,output_nums)
        self._init()
    def creat_pin(self,i,port,data_type):
        if port=='input':
            _pin = NodePin(port,data_type, self,i)
            #_pin.setPos(0, self.rect().height() / (self.input_nums+1) * (i+1))
            self.input_pins.append(_pin)
        else:
            _pin = NodePin(port,data_type, self,i)
            #_pin.setPos(self.rect().width(), self.rect().height() / (self.output_nums+1) * (i+1))
            self.output_pins.append(_pin)
    def _setup_pins(self, pin_type, pin_count, pin_info_list):
        """设置引脚的通用方法"""
        pins_list = self.input_pins if pin_type == 'input' else self.output_pins
        
        # 创建引脚
        for i in range(pin_count):
            self.creat_pin(i, pin_type, pin_info_list[i][0])
        
        # 计算最大长度并更新节点宽度
        max_length = max((pin.length for pin in pins_list), default=0)
        if max_length > 0:
            self.setRect(0, 0, self.rect().width() + max_length, self.rect().height())
        if self.title.boundingRect().width()>self.rect().width() and pin_type=='output':
            self.setRect(0, 0, self.title.boundingRect().width(), self.rect().height())
        # 设置引脚位置
        for i, pin in enumerate(pins_list):
            if pin_type == 'input':
                pin.setPos(0, self.rect().height() / (pin_count + 1) * (i + 1))
            else:
                pin.setPos(self.rect().width(), self.rect().height() / (pin_count + 1) * (i + 1))
    
    def _init(self):
        """初始化节点"""   
        # 设置节点名称
        self.rename(self.NodeInfo.zh_name)
        
        # 设置输入引脚
        self._setup_pins('input', self.input_nums, self.NodeInfo.input)
        
        # 设置输出引脚
        self._setup_pins('output', self.output_nums, self.NodeInfo.output)
        
        # 重新定位标题
        self.re_position_title()
    def itemChange(self, change, value):
        """节点状态变化时处理"""
        #位置变化
        if change == QGraphicsItem.GraphicsItemChange.ItemPositionChange:
            # 通知场景更新连接线
            if self.scene():
                self.scene().update_connections()
        #选中变化
        elif change == QGraphicsItem.GraphicsItemChange.ItemSelectedHasChanged:
            # 节点选中状态变化时更新边框颜色
            if self.isSelected():
                # 选中时边框为蓝色
                self.setPen(QPen(QColor(0, 120, 215), 3))
            else:
                # 未选中时边框为灰色
                self.setPen(QPen(QColor(200, 200, 200), 3))
        
        
        return super().itemChange(change, value)
    def run(self):
        """节点运行"""
        print(self.name)