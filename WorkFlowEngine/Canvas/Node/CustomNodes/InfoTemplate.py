from ast import Return


class InfoTemplate:
    def __init__(self,node_name,zh_name=None):
        self.node_name=node_name
        self.zh_name=zh_name
        self.input=[]
        self.output=[]
    def run(self):
        f"""
        节点运行
        Args:
            input:[pin:value]
        Returns:
            输出参数
        """

        return []
    def logic_check(self,arg):
        if arg[0] != False:
            return True
        return False

