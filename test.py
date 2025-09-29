from Engine import *

if __name__ == "__main__":
    flow={
        #名称:{
        #     "type":类型,
        #     "input":{
        #         "名称":类型
        #     },
        #     "output":{
        #         "名称":[类型,["连接节点1","连接节点2"]]
        #     }
        # }
        
        "Start":{
            "type":"Start",
            "input":{},
            "output":{
                "none":[None,["Add"]]
            }
        },
        "Add":{
            "type":"Add",
            "input":{
                "num1":1,
                "num2":2
            },
            "output":{
                "output":[int,["end","Add1"]],
                "bool":[bool,["printbool"]]
            }
        },
        "Add1":{
            "type":"Add",
            "input":{
                "num1":"output",
                "num2":2
            },
            "output":{
                "output":[int,["pr"]],
                "bool":[bool,[]]
            }
        },
        "printbool":{
            "type":"DraggableLabelPrint",
            "input":{
                "str":"bool"
            },
            "output":{
                "none":[None,[]]

            }
        },
        "end":{
            "type":"DraggableLabelPrint",
            "input":{
                "str":"output"
            },
            "output":{
                "none":[None,[]]
            }
        },
        "pr":{
            "type":"DraggableLabelPrint",
            "input":{
                "str":"output"
            },
            "output":{
                "none":[None,[]]
            }
        }
    }
    graph=Graph(flow)
    graph.run()