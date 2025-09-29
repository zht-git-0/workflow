from ..InfoTemplate import InfoTemplate
class Info(InfoTemplate):
    def __init__(self):
        super().__init__("TypeChange","类型转换")
        self.input=[["logic",False],["none",True]]
        self.output=[["logic",False],["none",True]]
    def run(self,arg):
        """
        类型转换
        """
        #[True,[output_pins,value]]
        type_dict={"int":int,"str":str}
        if super().logic_check(arg):
            return [True,type_dict[self.output[1][0]](arg[1])]
        return [False,None]
            #return [True,arg[1]]
        