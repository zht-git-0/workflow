from .Packages import *
from .Canvas.CanvasWidget import CanvasWidget
from .Menu.NodeListPanel import NodeListPanel
from .Canvas.Node.Node import Node, NodePin
from .Canvas.Node.RunNodes import Run
from .WorkflowIO import WorkflowIO
from PyQt6.QtWidgets import QFileDialog, QMessageBox
class MainWindow(QMainWindow):
    """主窗口类"""
    def __init__(self):
        super().__init__()
        self.setWindowTitle("节点编辑器 - Graphics View版本")
        self.setGeometry(100, 100, 1200, 800)
        
        # 创建中央部件
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # 创建水平布局（用于侧边栏和画布）
        main_layout = QHBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # 创建画布
        self.canvas = CanvasWidget()
        
        # 创建节点列表侧边栏
        self.node_list_panel = NodeListPanel(self.canvas)
        
        # 创建展开按钮（初始隐藏）
        self.expand_button = QPushButton("▶")
        self.expand_button.setFixedSize(30, 50)
        self.expand_button.hide()
        self.expand_button.clicked.connect(self.expand_side_panel)
        # 设置展开按钮样式
        self.expand_button.setStyleSheet("""
            QPushButton {
                background-color: #e0e0e0;
                border: 1px solid #bbb;
                border-radius: 3px;
                color: black;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #d0d0d0;
            }
            QPushButton:pressed {
                background-color: #c0c0c0;
            }
        """)
        
        # 添加到主布局
        main_layout.addWidget(self.expand_button)  # 展开按钮（最左侧）
        main_layout.addWidget(self.node_list_panel)
        main_layout.addWidget(self.canvas, 1)  # 画布占据剩余空间
        
        # 连接侧边栏折叠信号
        self.node_list_panel.collapsed.connect(self.on_side_panel_collapsed)
        # 创建菜单栏
        self.create_menu_bar()
        
        # 创建工具栏
        self.create_tool_bar()
        
        # 初始时折叠侧边栏
        #self.node_list_panel.toggle_collapse()
        
        # 添加一些示例节点
        self.canvas.scene.add_node("Start", -400, -300)
    
    def create_menu_bar(self):
        """创建菜单栏"""
        menubar = self.menuBar()
        
        # 文件菜单
        file_menu = menubar.addMenu("文件")
        
        # 新建动作
        new_action = file_menu.addAction("新建")
        new_action.triggered.connect(self.new_scene)
        
        # 保存动作
        save_action = file_menu.addAction("保存")
        save_action.triggered.connect(self.save_workflow)
        
        # 导入动作
        import_action = file_menu.addAction("导入")
        import_action.triggered.connect(self.import_workflow)
        
        # 退出动作
        exit_action = file_menu.addAction("退出")
        exit_action.triggered.connect(self.close)
        
        # 编辑菜单
        edit_menu = menubar.addMenu("编辑")
        
        # 添加节点动作
        add_node_action = edit_menu.addAction("添加节点")
        add_node_action.triggered.connect(self.add_node)
        
        # 清空动作
        clear_action = edit_menu.addAction("清空画布")
        clear_action.triggered.connect(self.clear_scene)
        
        # 调试输出动作
        debug_action = edit_menu.addAction("调试输出")
        debug_action.triggered.connect(self.debug_output)
        
        # 视图菜单
        view_menu = menubar.addMenu("视图")
        
        # 重置视图动作
        reset_view_action = view_menu.addAction("重置视图")
        reset_view_action.triggered.connect(self.reset_view)
    
    def create_tool_bar(self):
        """创建工具栏"""
        toolbar = self.addToolBar("工具栏")
        
        # 添加节点按钮
        add_node_action = toolbar.addAction("添加节点")
        add_node_action.triggered.connect(self.add_node)
        
        # 清空按钮
        clear_action = toolbar.addAction("清空")
        clear_action.triggered.connect(self.clear_scene)
        
        # 重置视图按钮
        reset_view_action = toolbar.addAction("重置视图")
        reset_view_action.triggered.connect(self.reset_view)
    

    def add_node(self):
        """添加新节点"""
        import random
        x = random.randint(-200, 200)
        y = random.randint(-200, 200)
        node_name = f"节点{len(self.canvas.scene.items()) + 1}"
        self.canvas.scene.add_node(node_name, x, y)
    
    def clear_scene(self):
        """清空场景"""
        self.canvas.scene.clear()
        self.canvas.scene.connections = []
    
    def new_scene(self):
        """新建场景"""
        self.clear_scene()
    
    def reset_view(self):
        """重置视图"""
        self.resetTransform()
        self.centerOn(0, 0)
    
    def on_side_panel_collapsed(self, collapsed):
        """侧边栏折叠状态改变处理"""
        if collapsed:
            # 隐藏侧边栏，显示展开按钮
            self.node_list_panel.hide()
            self.expand_button.show()
        else:
            # 显示侧边栏，隐藏展开按钮
            self.node_list_panel.show()
            self.expand_button.hide()
    
    def expand_side_panel(self):
        """展开侧边栏"""
        self.node_list_panel.expand_panel()
    
    def debug_output(self):
        """调试输出节点连接状态"""
        # 获取场景中的所有节点实例
        # 遍历场景中的所有图形项，筛选出Node类型的实例
        nodes = self.canvas.scene.get_all_node()
        runner = Run(nodes)
        runner.debug_()
        #print(res)
    
    def save_workflow(self):
        """保存工作流"""
        file_path, _ = QFileDialog.getSaveFileName(self, "保存工作流", "", "工作流文件 (*.json)")
        if file_path:
            if not file_path.endswith('.json'):
                file_path += '.json'
            
            success = WorkflowIO.save_workflow(self.canvas.scene, file_path)
            #if success:
            #    QMessageBox.information(self, "保存成功", "工作流已成功保存！")
            #else:
            #    QMessageBox.warning(self, "保存失败", "保存工作流时发生错误！")
    
    def import_workflow(self):
        """导入工作流"""
        file_path, _ = QFileDialog.getOpenFileName(self, "导入工作流", "", "工作流文件 (*.json)")
        if file_path:
            success = WorkflowIO.load_workflow(self.canvas.scene, file_path)
            #if success:
            #    QMessageBox.information(self, "导入成功", "工作流已成功导入！")
            #else:
            #    QMessageBox.warning(self, "导入失败", "导入工作流时发生错误！")
        
    
