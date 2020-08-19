class TestModule:
    def __eq__(self, other):
        return self.__hash__() == other.__hash__()

    def __hash__(self):
        return hash(self.__class__.__name__)

    def __str__(self):
        return self.__class__.__name__