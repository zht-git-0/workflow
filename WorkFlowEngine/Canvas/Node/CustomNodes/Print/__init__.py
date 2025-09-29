from ..InfoTemplate import InfoTemplate
class Info(InfoTemplate):
    def __init__(self):
        super().__init__("Print","打印")
        self.input=[["logic",False],["str",True]]
        self.output=[["logic",False]]
    def run(self,arg):
        """
        打印输入
        """
        if super().logic_check(arg):
            print(arg[1])
        return [True]