from ..Packages import QMenu
from . import setStyleSheet
from ..Canvas.Node.CustomNodes import node_dict
class RightClickMenu(QMenu):
    def __init__(self, parent,create_new_node):
        super().__init__(parent)
        self.setStyleSheet(setStyleSheet)
    
        # 创建新建节点子菜单
        new_node_menu = self.addMenu("新建节点")
        
        # 在新建节点子菜单下添加加法节点选项
        for node_name in node_dict.keys():
            new_node = new_node_menu.addAction(node_dict[node_name].Info().zh_name)
            new_node.triggered.connect(lambda checked, name=node_name: create_new_node(node_dict[name].Info().node_name))
        # 可以继续添加其他类型的节点到新建节点子菜单下
        # self.other_node_action = self.new_node_menu.addAction("其他节点")
