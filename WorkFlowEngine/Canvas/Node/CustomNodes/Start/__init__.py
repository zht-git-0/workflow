from ..InfoTemplate import InfoTemplate
class Info(InfoTemplate):
    def __init__(self):
        super().__init__("Start","开始")
        self.input=[]
        self.output=[["logic",False]]
    def run(self,arg):
        return [True]

