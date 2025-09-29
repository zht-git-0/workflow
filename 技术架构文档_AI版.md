# 工作流引擎技术架构文档 (AI版)

## 1. 系统概述

基于PyQt6的节点式工作流引擎，实现可视化编程和流程控制。核心特性包括：
- 图形化节点编辑与连接
- 多数据类型支持 (int, str, bool, float, logic)
- 拓扑排序执行引擎
- JSON格式工作流序列化

## 2. 架构设计

### 2.1 MVC架构模式
```
Model: 节点/连接数据模型
  ├── Node: 节点基类与自定义节点
  ├── NodePin: 引脚系统
  └── ConnectionLine: 连接线管理

View: 可视化组件
  ├── CanvasWidget: 画布视图 (QGraphicsView)
  ├── CanvasScene: 场景管理 (QGraphicsScene)
  └── MainWindow: 主窗口容器

Controller: 控制逻辑
  ├── Run: 执行引擎
  ├── WorkflowIO: 序列化/反序列化
  └── 事件处理系统
```

### 2.2 核心数据流
```
用户交互 → 事件处理 → 模型更新 → 视图刷新 → 执行引擎 → 结果输出
```

## 3. 关键技术实现

### 3.1 节点系统
```python
class Node(NodeBase):
    - 动态引脚生成 (基于NodeInfo配置)
    - 引脚类型: input/output
    - 数据类型: int/str/bool/float/logic/none
    - 状态管理: 选中/连接/执行
```

### 3.2 引脚系统
```python
class NodePin(BaseItem):
    - 数据类型颜色编码
    - 连接状态管理
    - 输入控件: QLineEdit/QComboBox
    - 连接验证: 类型匹配/单向连接
```

### 3.3 执行引擎
```python
class Run:
    - 依赖图构建: _build_dependencies()
    - 拓扑排序: _topological_sort()
    - 执行顺序: Start节点优先
    - 数据传递: output_link[input_pin] = value
```

### 3.4 工作流序列化
```python
class WorkflowIO:
    - JSON结构: {nodes: [...], connections: [...]}
    - 节点数据: 位置/类型/引脚值
    - 连接数据: 起止节点/引脚索引/颜色
    - 状态恢复: 连接状态/引脚值/控件状态
```

## 4. 扩展机制

### 4.1 自定义节点模板
```python
class InfoTemplate:
    - node_name: 节点标识
    - zh_name: 显示名称
    - input/output: 引脚配置
    - run(): 执行逻辑
    - logic_check(): 条件验证
```

### 4.2 节点注册系统
```python
node_dict = {
    "Start": Start.Info,
    "Add(int)": AddInt.Info,
    "Print": Print.Info,
    # ...
}
```

## 5. 交互设计

### 5.1 鼠标交互
- 左键: 选择/拖拽节点
- 右键短按: 上下文菜单
- 右键长按: 框选模式
- 滚轮: 画布缩放
- Delete: 删除选中项

### 5.2 拖拽系统
- 节点列表 → 画布: 节点创建
- 引脚 → 引脚: 连接创建
- 画布空白区域: 平移视图

## 6. 性能优化

### 6.1 渲染优化
- QGraphicsView抗锯齿
- 视口更新模式: FullViewportUpdate
- 连接线Z值: -1 (置于底层)

### 6.2 事件处理
- 鼠标跟踪: setMouseTracking(True)
- 事件传播控制: event.accept()
- 临时连接线: 拖拽时显示

## 7. 数据结构

### 7.1 节点数据结构
```json
{
    "name": "节点名称",
    "x": 0, "y": 0,
    "node_type": "节点类型",
    "input_pin_values": [...],
    "output_pin_values": [...],
    "input_pin_combo_values": [...],
    "output_pin_combo_values": [...]
}
```

### 7.2 连接数据结构
```json
{
    "start_node": 0,
    "end_node": 1,
    "start_pin": 0,
    "end_pin": 0,
    "color": "#ff0000"
}
```

## 8. 关键算法

### 8.1 拓扑排序算法
```python
def _topological_sort(self, dependencies):
    # 1. 计算入度
    # 2. 找到入度为0的节点 (优先Start节点)
    # 3. BFS遍历，减少依赖节点入度
    # 4. 返回执行顺序
```

### 8.2 连接更新算法
```python
def update_connections(self):
    # 遍历所有连接线
    # 更新起点和终点坐标
    # 处理异常情况 (节点删除)
```

## 9. 设计模式应用

### 9.1 工厂模式
- PinWidgetFactory: 创建引脚控件
- 节点注册系统: 动态创建节点实例

### 9.2 观察者模式
- 引脚连接状态变化 → 外观更新
- 节点位置变化 → 连接线更新

### 9.3 模板方法模式
- InfoTemplate: 定义节点基本结构
- 自定义节点: 实现特定逻辑

## 10. 技术亮点

1. **可视化编程**: 基于PyQt6图形框架的完整实现
2. **类型安全**: 引脚类型检查与颜色编码
3. **执行控制**: 基于拓扑排序的执行顺序保证
4. **扩展性**: 模块化节点系统，易于扩展
5. **状态管理**: 完整的序列化/反序列化支持
6. **交互体验**: 多种交互方式，操作直观

## 11. 适用场景

- 游戏脚本可视化编辑
- 数据处理流程设计
- 自动化工作流构建
- 教学演示系统
- 快速原型开发

## 12. 技术栈

- **GUI框架**: PyQt6 (QGraphicsView框架)
- **编程语言**: Python 3.10+
- **数据格式**: JSON
- **设计模式**: MVC/工厂/观察者/模板方法