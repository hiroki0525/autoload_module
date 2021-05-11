class TestModule:
    def __init__(self):
        self.classname = self.__class__.__name__

    def __str__(self):
        return self.classname

    def __eq__(self, other):
        return self.classname == other.classname

    def __hash__(self):
        return hash(self.classname)
