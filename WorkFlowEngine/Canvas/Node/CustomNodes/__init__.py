import os
import importlib

def search(lib:dict,key):
    for k in lib:
        if k==key:
            return lib[k]
    return None

def get_all_node_names():
    """获取 CustomNodes 文件夹中的所有节点名称"""
    node_names = []
    custom_nodes_path = os.path.dirname(os.path.abspath(__file__))
    
    # 遍历 CustomNodes 文件夹中的所有子文件夹
    for item in os.listdir(custom_nodes_path):
        item_path = os.path.join(custom_nodes_path, item)
        if os.path.isdir(item_path):
            # 检查子文件夹中是否有 Node.py 文件
            node_file_path = os.path.join(item_path, "__init__.py")
            if os.path.exists(node_file_path):
                globals()[item] = importlib.import_module(f".{item}", package=__name__)
                node_dict[globals()[item].Info().node_name]=globals()[item]
    return node_names
node_dict={}


node_names=get_all_node_names()
""" {"Start":Module}
print(node_dict["Start"].Info().node_name) """
