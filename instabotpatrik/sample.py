

class MyModifier:
    def modify(self, n, type="double"):
        if type == "double":
            print("Running double calculation for 10 minutes")
            return n*2
        elif type == "triple":
            print("Running double calculation for 20 minutes")
            return n*3

class MySample:
    def __init__(self,
                 init_val):
        self.init_val = init_val

    def do_smt(self):
        print("Doing something")


class MyDbTest:
    def __init__(self):
        print("Db test class")