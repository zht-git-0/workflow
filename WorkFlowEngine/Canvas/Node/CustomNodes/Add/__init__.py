from ..InfoTemplate import InfoTemplate
class Info(InfoTemplate):
    def __init__(self):
        super().__init__("Add(int)","加(int)")
        #self.logic=False
        self.input=[["int",True],["int",True]]
        self.output=[["int",False]]
    def run(self,arg):
        """ for i in arg: """
        int_arg=[]
        for i in arg:
            int_arg.append(int(i))
        return [sum(int_arg)]
        
