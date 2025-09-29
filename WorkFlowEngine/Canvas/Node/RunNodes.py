class Run:
    def __init__(self, nodes):
        self.nodes = nodes
        self.execution_order = []  # 节点的执行顺序
        self.pin_execution_order = []  # 引脚的访问顺序 [(node_index, pin_index, pin_type), ...]
        self.input_link={} # 链表，{当前引脚:前驱引脚的索引}
        self.output_link={} # 链表，{当前引脚:当前引脚的值}

        """执行工作流，返回节点和引脚的访问顺序"""
        # 构建节点依赖图
        dependencies = self._build_dependencies()
        
        # 使用拓扑排序获取执行顺序
        self.execution_order = self._topological_sort(dependencies)
        
        # 生成引脚访问顺序
        self.pin_execution_order = self._generate_pin_order()
        
        """ return {
            'node_order': self.execution_order,
            'pin_order': self.pin_execution_order
        } """
    
    def _build_dependencies(self):
        """构建节点依赖图"""
        #当前节点：[依赖节点1,依赖节点2,...]
        dependencies = {i: [] for i in range(len(self.nodes))}
        
        for node_idx, node in enumerate(self.nodes):
            # 对于每个节点的输入引脚，找到提供数据的节点
            for pin in node.input_pins:
                for connection in pin.connections:
                    # 找到连接的起始节点（数据提供者）
                    if connection.end_pin == pin:  # 当前引脚是终点
                        provider_node = connection.start_pin.parentItem()
                        provider_idx = self.nodes.index(provider_node)
                        if provider_idx not in dependencies[node_idx]:
                            dependencies[node_idx].append(provider_idx)
        
        return dependencies
    
    def _topological_sort(self, dependencies):
        """拓扑排序，确保依赖节点先执行，且从node_name为'Start'的节点开始"""
        # 计算入度
        in_degree = {i: 0 for i in range(len(self.nodes))}
        for node in dependencies:
            for dep in dependencies[node]:
                in_degree[node] += 1
        
        # 找到入度为0的节点（起始节点）
        zero_degree_nodes = [node for node in in_degree if in_degree[node] == 0]
        
        # 优先查找node_name为'start'的节点
        start_node = None
        for node_idx in zero_degree_nodes:
            if self.nodes[node_idx].NodeInfo.node_name == 'Start':
                start_node = node_idx
                break
        
        # 构建队列，如果有start节点则优先处理
        queue = []
        if start_node is not None:
            queue.append(start_node)
            # 添加其他入度为0的节点
            for node in zero_degree_nodes:
                if node != start_node:
                    queue.append(node)
        else:
            # 如果没有start节点，则按原方式处理
            queue = zero_degree_nodes
            
        result = []
        
        while queue:
            # 删除入度为0的节点
            current = queue.pop(0)
            result.append(current)
            
            # 减少依赖当前节点的其他节点的入度
            for node in dependencies:
                if current in dependencies[node]:
                    in_degree[node] -= 1
                    if in_degree[node] == 0:
                        queue.append(node)
        
        return result
    
    def _generate_pin_order(self):
        """生成引脚访问顺序"""
        pin_order = []
        
        # 按照节点执行顺序访问引脚
        for node_idx in self.execution_order:
            node = self.nodes[node_idx]
            
            # 先访问输入引脚（获取数据）
            for pin_idx, pin in enumerate(node.input_pins):
                pin_order.append((node_idx, pin_idx, 'input'))
            
            # 再访问输出引脚（提供数据）
            for pin_idx, pin in enumerate(node.output_pins):
                pin_order.append((node_idx, pin_idx, 'output'))
        
        return pin_order
    
    def debug_(self):
        """调试输出执行顺序"""
        """ print("节点执行顺序:")
        for idx in self.execution_order:
            print(f"  {idx}: {self.nodes[idx].NodeInfo.node_name}")
        
        print("\n引脚访问顺序:")
        for node_idx, pin_idx, pin_type in self.pin_execution_order:
            node = self.nodes[node_idx]
            pins = node.input_pins if pin_type == 'input' else node.output_pins
            if pin_idx < len(pins):
                pin = pins[pin_idx]
                print(f"  节点{node_idx}({node.name}) -> {pin_type}引脚{pin_idx}: {pin.data_type}") """
        self.run_node()
    def run_node(self):
        for node_idx in self.execution_order:
            node = self.nodes[node_idx]
            # 先访问引脚（获取数据）
            for pin_idx, pin in enumerate(node.output_pins):
                self.output_link[pin]=None
        for node_idx in self.execution_order:
            node = self.nodes[node_idx]
            # 先访问引脚（获取数据）
            for pin_idx, pin in enumerate(node.input_pins):
                if pin.connected:
                    start=pin.connections[0].start_pin
                    for input_key in self.output_link:
                        if input_key==start:
                            self.input_link[pin]=input_key
                            break
        # 执行节点
        for node_idx in self.execution_order:
            _input=[]
            #[value]
            node = self.nodes[node_idx]
            for pin_idx, pin in enumerate(node.input_pins):
                if (pin.connected and pin.combo_box==None) or pin.combo_box:
                    _input.append(self.output_link[self.input_link[pin]])
                elif pin.line_edit:
                    _input.append(pin.line_edit.text())
                
            #print(_input)
            _output=node.NodeInfo.run(_input)
            if _output and _output[0]==False:
                break
            for i in range(len(node.output_pins)):
                self.output_link[node.output_pins[i]]=_output[i]

                

        
            
