import sys
from WorkFlowEngine import MainWindow
from PyQt6.QtWidgets import QApplication

def main():
    """测试UI_2节点编辑器"""
    app = QApplication(sys.argv)
    
    # 创建主窗口7
    window = MainWindow()
    window.show()
    
    # 运行应用
    sys.exit(app.exec())

if __name__ == "__main__":
    main()