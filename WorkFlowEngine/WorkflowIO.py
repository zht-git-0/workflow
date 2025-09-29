# 导入所需的库和模块
import json  # 用于JSON格式的数据序列化和反序列化
import os    # 用于文件路径操作
from .Packages import *  # 导入项目中的所有包和模块
from .Canvas.Node.CustomNodes.pin_colors import pin_colors  # 导入引脚颜色配置
from .Canvas.Node.Node import Node  # 导入节点类
from .Canvas.Node.ConnectionLine import ConnectionLine  # 导入连接线类

class WorkflowIO:
    """工作流输入输出类 - 负责保存和导入工作流
    
    该类提供了两个主要功能：
    1. save_workflow - 将当前工作流保存为JSON文件
    2. load_workflow - 从JSON文件加载工作流
    """
    
    @staticmethod
    def save_workflow(scene, file_path):
        """保存工作流到文件
        
        该方法将当前场景中的所有节点和连接线信息保存为JSON格式的文件，
        以便后续可以重新加载工作流。
        
        Args:
            scene: CanvasScene对象，包含所有节点和连接
            file_path: 保存文件的路径
            
        Returns:
            bool: 保存是否成功
        """
        try:
            # 获取场景中的所有节点，并建立节点到索引的映射
            nodes = []
            node_to_index = {}  # 节点对象到索引的映射
            
            for item in scene.items():
                # 检查场景中的每个项目是否是节点对象
                if isinstance(item, Node):
                    # 为节点分配索引
                    node_index = len(nodes)
                    node_to_index[item] = node_index
                    
                    # 收集输入引脚的文本值和下拉框值
                    input_pin_values = []  # 存储输入引脚的文本值
                    input_pin_combo_values = []  # 存储输入引脚的下拉框选择值
                    for pin in item.input_pins:
                        # 检查引脚是否有文本输入框
                        if pin.line_edit:
                            input_pin_values.append(pin.line_edit.text())
                            input_pin_combo_values.append("")
                        # 检查引脚是否有下拉选择框
                        elif pin.combo_box:
                            input_pin_values.append("")
                            input_pin_combo_values.append(pin.combo_box.currentText())
                        # 如果引脚既没有文本输入框也没有下拉框，则添加空值
                        else:
                            input_pin_values.append("")
                            input_pin_combo_values.append("")
                    
                    # 收集输出引脚的文本值和下拉框值
                    output_pin_values = []  # 存储输出引脚的文本值
                    output_pin_combo_values = []  # 存储输出引脚的下拉框选择值
                    for pin in item.output_pins:
                        # 检查引脚是否有文本输入框
                        if pin.line_edit:
                            output_pin_values.append(pin.line_edit.text())
                            output_pin_combo_values.append("")
                        # 检查引脚是否有下拉选择框
                        elif pin.combo_box:
                            output_pin_values.append("")
                            output_pin_combo_values.append(pin.combo_box.currentText())
                        # 如果引脚既没有文本输入框也没有下拉框，则添加空值
                        else:
                            output_pin_values.append("")
                            output_pin_combo_values.append("")
                    
                    # 构建节点数据字典，包含节点的所有必要信息
                    node_data = {
                        'name': item.name,  # 节点名称
                        'x': item.pos().x(),  # 节点在场景中的X坐标
                        'y': item.pos().y(),  # 节点在场景中的Y坐标
                        'node_type': item.NodeInfo.node_name,  # 节点类型
                        'input_pin_values': input_pin_values,  # 输入引脚的文本值
                        'output_pin_values': output_pin_values,  # 输出引脚的文本值
                        'input_pin_combo_values': input_pin_combo_values,  # 输入引脚的下拉框值
                        'output_pin_combo_values': output_pin_combo_values  # 输出引脚的下拉框值
                    }
                    nodes.append(node_data)  # 将节点数据添加到节点列表
            
            # 获取场景中的所有连接
            connections = []
            # 使用集合来跟踪已保存的连接，避免重复保存相同的连接
            saved_connections = set()
            
            # 遍历场景中的所有连接
            for connection in scene.connections:
                # 获取起始节点和结束节点
                start_node = connection.start_pin.parentItem()
                end_node = connection.end_pin.parentItem()
                
                # 检查节点是否在映射中
                if start_node not in node_to_index or end_node not in node_to_index:
                    continue
                
                start_node_index = node_to_index[start_node]
                end_node_index = node_to_index[end_node]
                
                # 获取引脚索引
                start_pin_index = -1
                end_pin_index = -1
                
                # 查找起始引脚在起始节点输出引脚列表中的索引
                for i, pin in enumerate(start_node.output_pins):
                    if pin == connection.start_pin:
                        start_pin_index = i
                        break
                
                # 查找结束引脚在结束节点输入引脚列表中的索引
                for i, pin in enumerate(end_node.input_pins):
                    if pin == connection.end_pin:
                        end_pin_index = i
                        break
                
                # 如果找到了起始引脚和结束引脚
                if start_pin_index != -1 and end_pin_index != -1:
                    # 创建连接的唯一标识符，用于检查重复连接
                    connection_id = (start_node_index, end_node_index, start_pin_index, end_pin_index)
                    
                    # 检查是否已经保存了相同的连接
                    if connection_id in saved_connections:
                        continue  # 跳过重复连接
                    
                    # 将连接添加到已保存连接集合中
                    saved_connections.add(connection_id)
                    
                    # 构建连接数据字典，包含连接的所有必要信息
                    connection_data = {
                        'start_node': start_node_index,  # 起始节点索引
                        'end_node': end_node_index,      # 结束节点索引
                        'start_pin': start_pin_index,    # 起始引脚索引
                        'end_pin': end_pin_index,        # 结束引脚索引
                        'color': connection.color.name() # 连接线颜色
                    }
                    connections.append(connection_data)  # 将连接数据添加到连接列表
            
            # 构建工作流数据字典，包含所有节点和连接信息
            workflow_data = {
                'nodes': nodes,          # 节点数据列表
                'connections': connections  # 连接数据列表
            }
            
            # 将工作流数据保存到JSON文件
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(workflow_data, f, indent=4, ensure_ascii=False)  # 使用UTF-8编码，缩进4个空格，不转义ASCII字符
            
            return True  # 保存成功，返回True
        except Exception as e:
            # 捕获并打印异常信息
            print(f"保存工作流失败: {e}")
            return False  # 保存失败，返回False
    
    @staticmethod
    def load_workflow(scene, file_path):
        """从文件导入工作流
        
        该方法从JSON文件中读取工作流数据，并在场景中重建节点和连接线。
        
        Args:
            scene: CanvasScene对象，用于导入节点和连接
            file_path: 导入文件的路径
            
        Returns:
            bool: 导入是否成功
        """
        try:
            # 清空当前场景，为导入新工作流做准备
            scene.clear()  # 清除场景中的所有项目
            scene.connections = []  # 清空连接列表
            
            # 从JSON文件中读取工作流数据
            with open(file_path, 'r', encoding='utf-8') as f:
                workflow_data = json.load(f)  # 加载JSON数据
            
            # 导入节点
            nodes = []  # 用于存储创建的节点对象
            for node_data in workflow_data['nodes']:
                # 根据节点类型和位置在场景中创建节点
                node = scene.add_node(node_data['node_type'], node_data['x'], node_data['y'])
                
                # 恢复输入引脚的文本值
                if 'input_pin_values' in node_data:
                    for i, value in enumerate(node_data['input_pin_values']):
                        # 确保索引在范围内且引脚有文本输入框
                        if i < len(node.input_pins) and node.input_pins[i].line_edit:
                            node.input_pins[i].line_edit.setText(value)  # 设置文本值
                
                # 恢复输入引脚的下拉框值
                if 'input_pin_combo_values' in node_data:
                    for i, value in enumerate(node_data['input_pin_combo_values']):
                        # 确保索引在范围内且引脚有下拉框且值不为空
                        if i < len(node.input_pins) and node.input_pins[i].combo_box and value:
                            index = node.input_pins[i].combo_box.findText(value)  # 查找值在下拉框中的索引
                            if index >= 0:
                                node.input_pins[i].combo_box.setCurrentIndex(index)  # 设置下拉框当前索引
                                # 更新引脚颜色以反映数据类型
                                node.input_pins[i].data_type = value
                                node.input_pins[i].color = pin_colors[value]
                                node.input_pins[i].update_appearance()  # 更新引脚外观
                
                # 恢复输出引脚的文本值
                if 'output_pin_values' in node_data:
                    for i, value in enumerate(node_data['output_pin_values']):
                        # 确保索引在范围内且引脚有文本输入框
                        if i < len(node.output_pins) and node.output_pins[i].line_edit:
                            node.output_pins[i].line_edit.setText(value)  # 设置文本值
                
                # 恢复输出引脚的下拉框值
                if 'output_pin_combo_values' in node_data:
                    for i, value in enumerate(node_data['output_pin_combo_values']):
                        # 确保索引在范围内且引脚有下拉框且值不为空
                        if i < len(node.output_pins) and node.output_pins[i].combo_box and value:
                            index = node.output_pins[i].combo_box.findText(value)  # 查找值在下拉框中的索引
                            if index >= 0:
                                node.output_pins[i].combo_box.setCurrentIndex(index)  # 设置下拉框当前索引
                                # 更新引脚颜色以反映数据类型
                                node.output_pins[i].data_type = value
                                node.output_pins[i].color = pin_colors[value]
                                node.output_pins[i].update_appearance()  # 更新引脚外观
                
                nodes.append(node)  # 将创建的节点添加到节点列表
            
            # 导入连接
            # 使用集合来跟踪已创建的连接，避免重复创建相同的连接
            existing_connections = set()
            
            # 先清空所有引脚的连接状态
            for node in nodes:
                for pin in node.input_pins + node.output_pins:
                    pin.connections = []
                    pin.connected = False
                    pin.update_appearance()
            
            # 清空场景中的连接列表
            scene.connections = []
            
            # 遍历所有连接数据
            for connection_data in workflow_data['connections']:
                try:
                    # 获取起始节点和结束节点
                    start_node = nodes[connection_data['start_node']]  # 起始节点
                    end_node = nodes[connection_data['end_node']]      # 结束节点
                    
                    # 获取起始引脚和结束引脚
                    start_pin = start_node.output_pins[connection_data['start_pin']]  # 起始引脚
                    end_pin = end_node.input_pins[connection_data['end_pin']]          # 结束引脚
                    
                    # 检查引脚索引是否有效
                    if connection_data['start_pin'] >= len(start_node.output_pins) or \
                       connection_data['end_pin'] >= len(end_node.input_pins):
                        continue
                    
                    # 创建连接的唯一标识符，基于节点索引和引脚索引
                    connection_id = (connection_data['start_node'], 
                                   connection_data['end_node'], 
                                   connection_data['start_pin'], 
                                   connection_data['end_pin'])
                    
                    # 检查是否已经存在相同的连接
                    if connection_id in existing_connections:
                        continue  # 跳过重复连接
                    
                    # 检查结束引脚是否已经被连接
                    if end_pin.connected:
                        continue  # 跳过已连接的输入引脚
                    
                    # 将连接添加到已存在连接集合中
                    existing_connections.add(connection_id)
                    
                    # 创建连接线对象
                    connection = ConnectionLine(start_pin, end_pin, start_pin.color)
                    connection.color = QColor(connection_data['color'])  # 设置连接线颜色
                    connection.setPen(QPen(QColor(connection_data['color']), 8))  # 设置连接线画笔
                    
                    # 将连接添加到场景和连接列表
                    scene.addItem(connection)  # 添加到场景
                    scene.connections.append(connection)  # 添加到连接列表
                    
                    # 将连接添加到引脚的连接列表
                    start_pin.connections.append(connection)  # 添加到起始引脚的连接列表
                    end_pin.connections.append(connection)    # 添加到结束引脚的连接列表
                    
                    # 更新引脚的连接状态和外观
                    start_pin.connected = True  # 起始引脚标记为已连接
                    end_pin.connected = True    # 结束引脚标记为已连接
                    start_pin.update_appearance()  # 更新起始引脚外观
                    end_pin.update_appearance()    # 更新结束引脚外观
                    
                except (IndexError, KeyError) as e:
                    # 捕获索引错误，避免程序崩溃
                    print(f"跳过无效连接: {e}")
                    continue
            
            return True  # 导入成功，返回True
        except Exception as e:
            # 捕获并打印异常信息
            print(f"导入工作流失败: {e}")
            return False  # 导入失败，返回False